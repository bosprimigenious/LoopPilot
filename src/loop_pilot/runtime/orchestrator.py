"""Orchestrator — drives a Run through phases deterministically."""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_pilot.config import LoopPilotConfig
from loop_pilot.domain.models import RunRecord, RunRequest, rfc3339
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.loops.paper.loop import PaperLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.locks import FileLockStore
from loop_pilot.runtime.run_ids import new_run_id
from loop_pilot.storage.base import StateStore


class Orchestrator:
    def __init__(self, config: LoopPilotConfig, state_store: StateStore) -> None:
        self.config = config
        self.state_store = state_store
        lock_dir = Path(config.runtime.get("lock_dir", config.state_dir / "locks"))
        self.locks = FileLockStore(lock_dir)
        self.policy = PolicyEngine(config.policies)
        self.renderer = ReportRenderer(Path("templates"))
        self.artifact_dir = Path(config.artifact_dir)

    def create_run_record(self, request: RunRequest) -> RunRecord:
        policy = self._budget_policy(request.loop_type)
        budget_mgr = BudgetManager(policy)
        started = datetime.now(timezone.utc)
        soft, hard = budget_mgr.compute_deadlines(started)
        return RunRecord(
            run_id=request.run_id,
            phase=RunPhase.CREATED,
            loop_type=request.loop_type,
            started_at=started.isoformat(),
            soft_deadline_at=soft,
            hard_deadline_at=hard,
            budgets=budget_mgr.create_snapshot(),
            fixture=request.fixture,
            dry_run=request.dry_run,
        )

    def run_loop(self, request: RunRequest, *, snapshot_day: str | None = None) -> RunRecord:
        record = self.create_run_record(request)
        record.phase = RunPhase.LOCKING
        self.state_store.save_run(record)
        lock_key = f"loop:{request.loop_type}"

        try:
            with self.locks.acquire(lock_key, request.run_id):
                loop = self._get_loop(request.loop_type)
                if request.loop_type == "daily_news" and snapshot_day:
                    record, _, _ = loop.run(request, record, snapshot_day=snapshot_day)
                else:
                    record, _, _ = loop.run(request, record)
        except Exception as exc:
            record = self._mark_failed(record, exc)

        self.state_store.save_run(record)
        manifest_path = (
            self.artifact_dir
            / request.loop_type.replace("_", "-")
            / record.run_id
            / "artifact-manifest.json"
        )
        if manifest_path.exists():
            self.state_store.save_artifact_manifest(
                record.run_id,
                json.loads(manifest_path.read_text(encoding="utf-8")),
            )
        return record

    def run_all(self, fixture_set: str = "mini", dry_run: bool = False) -> list[RunRecord]:
        results: list[RunRecord] = []
        sequence = [
            ("daily_news", "github_star_snapshots", "day2"),
            ("intern", "simple_python_bug", None),
            ("paper", "unsupported_claim", None),
        ]
        summary_sections: list[str] = []

        for loop_type, fixture, extra in sequence:
            request = RunRequest(
                run_id=self.new_run_id(loop_type),
                loop_type=loop_type,
                fixture=fixture,
                dry_run=dry_run,
                config_snapshot_hash=self.config.snapshot_hash(),
            )
            record = self.run_loop(request, snapshot_day=extra)
            results.append(record)
            outcome = record.outcome.value if record.outcome else "unknown"
            summary_sections.append(f"## {loop_type}\n\nOutcome: {outcome}\n")
            if record.terminal_reason:
                summary_sections.append(f"Reason: {record.terminal_reason}\n")

        summary_dir = self.artifact_dir / "daily-summary"
        summary_dir.mkdir(parents=True, exist_ok=True)
        summary_path = summary_dir / f"{rfc3339()[:10]}-summary.md"
        summary_path.write_text(self.renderer.render_daily_summary(results, summary_sections), encoding="utf-8")
        return results

    def new_run_id(self, loop_type: str) -> str:
        return new_run_id(loop_type)

    def _mark_failed(self, record: RunRecord, exc: Exception) -> RunRecord:
        record.phase = RunPhase.TERMINATED
        record.outcome = RunOutcome.FAILED
        record.terminal_reason = f"{type(exc).__name__}: {exc}"
        record.finished_at = rfc3339()
        record.report_status = "failed"
        return record

    def _get_loop(self, loop_type: str) -> InternLoop | PaperLoop | DailyNewsLoop:
        policy = self._budget_policy(loop_type)
        budget_mgr = BudgetManager(policy)
        if loop_type == "intern":
            return InternLoop(self.artifact_dir, self.policy, self.renderer, budget_mgr)
        if loop_type == "paper":
            return PaperLoop(self.artifact_dir, self.policy, self.renderer, budget_mgr)
        if loop_type == "daily_news":
            return DailyNewsLoop(self.artifact_dir, self.policy, self.renderer, budget_mgr)
        raise ValueError(f"Unknown loop type: {loop_type}")

    def _budget_policy(self, loop_type: str) -> BudgetPolicy:
        cfg: dict[str, Any] = {}
        if loop_type == "intern":
            cfg = self.config.intern.get("budget", {})
        elif loop_type == "paper":
            cfg = self.config.paper.get("budget", {})
        elif loop_type == "daily_news":
            cfg = self.config.daily_news.get("budget", {})
        return BudgetPolicy(
            max_duration_minutes=cfg.get("max_duration_minutes", 30),
            max_rounds=cfg.get("max_rounds", 3),
            max_model_calls=cfg.get("max_model_calls", 8),
        )
