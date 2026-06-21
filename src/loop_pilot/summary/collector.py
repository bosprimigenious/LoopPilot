"""Collect data for daily and weekly summaries."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.recovery_scan import scan_recovery
from loop_pilot.storage.base import StateStore
from loop_pilot.summary.models import (
    BlockedSummaryRow,
    DailySummaryData,
    ReviewSummaryRow,
    RunSummaryRow,
    WeeklySummaryData,
)
from loop_pilot.tasks.models import InboxItem
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


def loop_artifact_segment(loop_type: str) -> str:
    return loop_type.replace("_", "-")


def run_artifact_dir(artifact_dir: Path, loop_type: str, run_id: str) -> Path:
    return artifact_dir / loop_artifact_segment(loop_type) / run_id


def read_gate_result(artifact_dir: Path, loop_type: str, run_id: str) -> str | None:
    path = run_artifact_dir(artifact_dir, loop_type, run_id) / "gate_result.json"
    if not path.exists():
        legacy = run_artifact_dir(artifact_dir, loop_type, run_id) / "gate-result.json"
        path = legacy if legacy.exists() else path
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    gate = payload.get("gate") or payload.get("verdict")
    return str(gate) if gate else None


def report_path(artifact_dir: Path, loop_type: str, run_id: str) -> str | None:
    run_dir = run_artifact_dir(artifact_dir, loop_type, run_id)
    for name in ("report.md", "daily-news-report.md"):
        candidate = run_dir / name
        if candidate.exists():
            return str(candidate)
    return None


def _run_on_date(record: RunRecord, target: str) -> bool:
    started = record.started_at[:10] if record.started_at else ""
    finished = record.finished_at[:10] if record.finished_at else ""
    return started == target or finished == target


def _inbox_on_date(item: InboxItem, target: str) -> bool:
    return item.created_at[:10] == target or item.updated_at[:10] == target


class SummaryCollector:
    def __init__(
        self,
        *,
        state_store: StateStore,
        task_store: TaskStore,
        artifact_dir: Path,
        lock_dir: Path,
        timezone: str = "Asia/Shanghai",
    ) -> None:
        self.state_store = state_store
        self.task_store = task_store
        self.artifact_dir = artifact_dir
        self.lock_dir = lock_dir
        self.timezone = timezone
        self.today_service = TodayService(task_store, timezone=timezone)

    def resolve_date(self, date_str: str | None) -> str:
        if date_str:
            return date_str
        return datetime.now(ZoneInfo(self.timezone)).date().isoformat()

    def collect_daily(self, date_str: str | None = None) -> DailySummaryData:
        target = self.resolve_date(date_str)
        if target == self.today_service.today_date():
            date_label, today_items = self.today_service.list_today()
        else:
            date_label = target
            today_items = self.task_store.list_today_items(target)

        runs = [record for record in self.state_store.list_runs(limit=500) if _run_on_date(record, target)]
        inbox_all = self.task_store.list_inbox_items(status="all")
        inbox_new = [item for item in inbox_all if _inbox_on_date(item, target)]
        inbox_daily_news = [
            item for item in inbox_new if item.source in {"daily-news", "daily_news"}
        ]
        queue_items = self.task_store.list_queue_items()

        run_rows = [
            RunSummaryRow(
                run_id=record.run_id,
                loop_type=record.loop_type,
                outcome=record.outcome.value if record.outcome else None,
                phase=record.phase.value,
                gate=read_gate_result(self.artifact_dir, record.loop_type, record.run_id),
                report_path=report_path(self.artifact_dir, record.loop_type, record.run_id),
            )
            for record in runs
        ]

        needs_review = self._collect_review_rows(runs)
        blocked = self._collect_blocked_rows(runs)
        recovery = scan_recovery(self.state_store, lock_dir=self.lock_dir)
        recovery_notes = [
            f"{item.run_id}: {item.category} -> {item.recommended_action}"
            for item in recovery
        ]

        highlights = self._build_highlights(
            runs=runs,
            needs_review=needs_review,
            inbox_daily_news=inbox_daily_news,
            today_items=today_items,
        )
        tomorrow = self._build_tomorrow_suggestions(needs_review, queue_items, inbox_all)

        return DailySummaryData(
            date=date_label,
            timezone=self.timezone,
            highlights=highlights,
            today_items=today_items,
            runs=run_rows,
            needs_review=needs_review,
            inbox_new=inbox_new,
            inbox_daily_news=inbox_daily_news,
            queue_items=queue_items,
            blocked=blocked,
            tomorrow=tomorrow,
            recovery_findings=recovery_notes,
        )

    def collect_weekly(self, week: str | None = None) -> WeeklySummaryData:
        start, end, label = self._resolve_week(week)
        daily_paths: list[str] = []
        completed: list[str] = []
        needs_review: list[str] = []
        blocked: list[str] = []
        loop_stats: dict[str, dict[str, int]] = {}

        current = start
        while current <= end:
            day = current.isoformat()
            data = self.collect_daily(day)
            daily_dir = self.artifact_dir / "daily" / day / "daily-summary.md"
            if daily_dir.exists():
                daily_paths.append(str(daily_dir))
            for row in data.runs:
                stats = loop_stats.setdefault(row.loop_type, {"runs": 0, "succeeded": 0, "blocked": 0})
                stats["runs"] += 1
                if row.outcome == RunOutcome.SUCCEEDED.value:
                    stats["succeeded"] += 1
                    completed.append(f"{day}: {row.run_id} ({row.loop_type}) succeeded")
                if row.outcome in {RunOutcome.BLOCKED.value, RunOutcome.FAILED.value}:
                    stats["blocked"] += 1
                    blocked.append(f"{day}: {row.run_id} ({row.loop_type}) {row.outcome}")
            for item in data.needs_review:
                needs_review.append(f"{day}: {item.run_id} — {item.reason}")
            current += timedelta(days=1)

        highlights = []
        if completed:
            highlights.append(f"{len(completed)} run(s) completed this week")
        if needs_review:
            highlights.append(f"{len(needs_review)} item(s) still need review")
        if blocked:
            highlights.append(f"{len(blocked)} blocked/failed run(s)")

        recommended = self._build_week_recommendations(needs_review, blocked)

        return WeeklySummaryData(
            week=label,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            highlights=highlights,
            completed=completed[:20],
            needs_review=needs_review[:20],
            blocked=blocked[:20],
            loop_stats=loop_stats,
            recommended=recommended,
            daily_paths=daily_paths,
        )

    def _collect_review_rows(self, runs: list[RunRecord]) -> list[ReviewSummaryRow]:
        rows: list[ReviewSummaryRow] = []
        for record in runs:
            if not self._needs_review(record):
                continue
            reason = record.terminal_reason or record.review_status or f"phase={record.phase.value}"
            rows.append(
                ReviewSummaryRow(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    reason=reason,
                    suggested_command=f"loop-pilot inspect {record.run_id}",
                )
            )
        return rows

    def _collect_blocked_rows(self, runs: list[RunRecord]) -> list[BlockedSummaryRow]:
        rows: list[BlockedSummaryRow] = []
        for record in runs:
            if record.outcome not in {RunOutcome.BLOCKED, RunOutcome.FAILED}:
                continue
            rows.append(
                BlockedSummaryRow(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    reason=record.terminal_reason or record.outcome.value,
                )
            )
        return rows

    def _needs_review(self, record: RunRecord) -> bool:
        if record.phase == RunPhase.WAITING_APPROVAL:
            return True
        if record.review_status in {"pending", "needs_review", "needs_revision"}:
            return True
        if record.outcome in {RunOutcome.PARTIAL, RunOutcome.BLOCKED, RunOutcome.EXHAUSTED}:
            return True
        gate = read_gate_result(self.artifact_dir, record.loop_type, record.run_id)
        return gate in {"needs_review", "blocked"}

    def _build_highlights(
        self,
        *,
        runs: list[RunRecord],
        needs_review: list[ReviewSummaryRow],
        inbox_daily_news: list[InboxItem],
        today_items: list,
    ) -> list[str]:
        highlights: list[str] = []
        intern_review = sum(1 for row in needs_review if row.loop_type == "intern")
        paper_review = sum(1 for row in needs_review if row.loop_type == "paper")
        if intern_review:
            highlights.append(f"InternLoop: {intern_review} run(s) waiting for review")
        if paper_review:
            highlights.append(f"PaperLoop: {paper_review} run(s) with evidence gaps or review")
        if inbox_daily_news:
            highlights.append(f"DailyNews: {len(inbox_daily_news)} candidate task(s) imported to Inbox")
        if today_items:
            highlights.append(f"Today: {len(today_items)} scheduled task(s)")
        if not highlights and runs:
            highlights.append(f"{len(runs)} run(s) completed today")
        if not highlights:
            highlights.append("No major activity recorded for this date")
        return highlights[:3]

    @staticmethod
    def _build_tomorrow_suggestions(
        needs_review: list[ReviewSummaryRow],
        queue_items: list,
        inbox_open: list[InboxItem],
    ) -> list[str]:
        suggestions: list[str] = []
        if needs_review:
            suggestions.append(f"Review `{needs_review[0].run_id}` first")
        queued = [item for item in queue_items if item.status == "queued"]
        if queued:
            suggestions.append(f"Promote or run queue item `{queued[0].id}` ({queued[0].title})")
        open_inbox = [item for item in inbox_open if item.status == "open"]
        if len(open_inbox) > 5:
            suggestions.append(f"Archive or promote {len(open_inbox)} open Inbox item(s)")
        if not suggestions:
            suggestions.append("No urgent items; run `loop-pilot run daily --dry-run` tomorrow morning")
        return suggestions[:3]

    @staticmethod
    def _build_week_recommendations(needs_review: list[str], blocked: list[str]) -> list[str]:
        items: list[str] = []
        if needs_review:
            items.append("Clear pending review queue before adding new tasks")
        if blocked:
            items.append("Investigate recurring blocked runs and update fixtures or policies")
        items.append("Run `loop-pilot summary week` every Sunday for weekly rollup")
        return items[:5]

    def _resolve_week(self, week: str | None) -> tuple[date, date, str]:
        if week:
            normalized = week.upper()
            if "-W" not in normalized:
                raise ValueError(f"invalid week label: {week}")
            year_str, week_str = normalized.split("-W", 1)
            year = int(year_str)
            week_num = int(week_str)
            start = date.fromisocalendar(year, week_num, 1)
            label = f"{year}-W{week_num:02d}"
        else:
            today = datetime.now(ZoneInfo(self.timezone)).date()
            iso = today.isocalendar()
            start = date.fromisocalendar(iso.year, iso.week, 1)
            label = f"{iso.year}-W{iso.week:02d}"
        end = start + timedelta(days=6)
        return start, end, label
