"""Summary generation service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loop_pilot.config import LoopPilotConfig
from loop_pilot.storage.base import StateStore
from loop_pilot.summary.collector import SummaryCollector
from loop_pilot.summary.models import SummaryRecord
from loop_pilot.summary.renderer import render_daily_summary, render_weekly_summary
from loop_pilot.summary.store import SummaryStore
from loop_pilot.tasks.store import TaskStore


@dataclass
class SummaryResult:
    path: Path
    record: SummaryRecord
    content: str


class SummaryService:
    def __init__(
        self,
        cfg: LoopPilotConfig,
        state_store: StateStore,
        task_store: TaskStore,
    ) -> None:
        timezone = str(cfg.runtime.get("timezone", "Asia/Shanghai"))
        self.cfg = cfg
        self.artifact_dir = cfg.artifact_dir
        self.collector = SummaryCollector(
            state_store=state_store,
            task_store=task_store,
            artifact_dir=cfg.artifact_dir,
            lock_dir=cfg.lock_dir,
            timezone=timezone,
        )
        self.summary_store = SummaryStore(cfg.sqlite_path)

    def generate_daily(self, date_str: str | None = None) -> SummaryResult:
        data = self.collector.collect_daily(date_str)
        content = render_daily_summary(data)
        output_dir = self.artifact_dir / "daily" / data.date
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "daily-summary.md"
        path.write_text(content, encoding="utf-8")

        record = self.summary_store.upsert_summary(
            SummaryRecord(
                id="",
                summary_type="daily",
                summary_date=data.date,
                path=str(path),
                status="generated",
                run_count=len(data.runs),
                review_count=len(data.needs_review),
                blocked_count=len(data.blocked),
                inbox_count=len(data.inbox_new),
            )
        )
        return SummaryResult(path=path, record=record, content=content)

    def generate_weekly(self, week: str | None = None) -> SummaryResult:
        data = self.collector.collect_weekly(week)
        content = render_weekly_summary(data)
        output_dir = self.artifact_dir / "weekly" / data.week
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "week-summary.md"
        path.write_text(content, encoding="utf-8")

        record = self.summary_store.upsert_summary(
            SummaryRecord(
                id="",
                summary_type="weekly",
                summary_date=data.week,
                path=str(path),
                status="generated",
                run_count=sum(item.get("runs", 0) for item in data.loop_stats.values()),
                review_count=len(data.needs_review),
                blocked_count=len(data.blocked),
                inbox_count=0,
            )
        )
        return SummaryResult(path=path, record=record, content=content)
