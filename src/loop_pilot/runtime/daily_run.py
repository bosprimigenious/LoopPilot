"""Daily dry-run orchestration for 0.4-d."""

from __future__ import annotations

from dataclasses import dataclass, field

from loop_pilot.config import LoopPilotConfig
from loop_pilot.runtime.locks import FileLockStore
from loop_pilot.runtime.recovery_scan import scan_recovery
from loop_pilot.storage.base import StateStore
from loop_pilot.storage.db_ops import verify_database
from loop_pilot.summary.service import SummaryResult, SummaryService
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


@dataclass
class DailyRunPlanItem:
    queue_id: str
    loop_type: str
    title: str
    action: str


@dataclass
class DailyRunResult:
    verify_ok: bool
    recovery_count: int
    today_date: str
    planned: list[DailyRunPlanItem] = field(default_factory=list)
    pending_review_count: int = 0
    summary: SummaryResult | None = None
    steps: list[str] = field(default_factory=list)


class DailyRunService:
    def __init__(
        self,
        cfg: LoopPilotConfig,
        state_store: StateStore,
        task_store: TaskStore,
    ) -> None:
        self.cfg = cfg
        self.state_store = state_store
        self.task_store = task_store
        self.summary_service = SummaryService(cfg, state_store, task_store)
        self.today_service = TodayService(
            task_store,
            timezone=str(cfg.runtime.get("timezone", "Asia/Shanghai")),
        )
        self.locks = FileLockStore(cfg.lock_dir)

    def run_daily(self, *, dry_run: bool = True) -> DailyRunResult:
        if not dry_run:
            raise ValueError("0.4-d only supports run daily --dry-run")

        steps: list[str] = []
        with self.locks.acquire("loop:daily", "daily-dry-run"):
            steps.append("lock acquired")

            verify = verify_database(self.cfg.sqlite_path, self.cfg.artifact_dir)
            steps.append("db verify: OK" if verify.ok else "db verify: issues found")

            findings = scan_recovery(self.state_store, lock_dir=self.cfg.lock_dir)
            steps.append(f"recovery-scan: {len(findings)} finding(s)")

            today_date, today_items = self.today_service.list_today()
            steps.append(f"today: {len(today_items)} item(s)")

            planned = [
                DailyRunPlanItem(
                    queue_id=item.id,
                    loop_type=item.loop_type,
                    title=item.title,
                    action=f"would dry-run loop {item.loop_type} for queue item {item.id}",
                )
                for item in today_items
            ]

            data = self.summary_service.collector.collect_daily(today_date)
            summary = self.summary_service.generate_daily(today_date)
            steps.append(f"summary written: {summary.path}")

        return DailyRunResult(
            verify_ok=verify.ok,
            recovery_count=len(findings),
            today_date=today_date,
            planned=planned,
            pending_review_count=len(data.needs_review),
            summary=summary,
            steps=steps,
        )
