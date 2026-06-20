"""Orchestrator — drives a Run through phases deterministically."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loop_pilot.config import LoopPilotConfig
from loop_pilot.domain.models import BudgetSnapshot, RunRecord, RunRequest, rfc3339
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.loops.paper.loop import PaperLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.locks import LocalLockStore
from loop_pilot.storage.base import StateStore
from loop_pilot.storage.json_store import JsonStateStore


class Orchestrator:
    def __init__(self, config: LoopPilotConfig, state_store: StateStore) -> None:
        self.config = config
        self.state_store = state_store
        self.locks = LocalLockStore()
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

    def run_loop(self, request: RunRequest) -> RunRecord:
        record = self.create_run_record(request)
        lock_key = f"loop:{request.loop_type}"

        with self.locks.acquire(lock_key, request.run_id):
            loop = self._get_loop(request.loop_type)
            record, manifest, _rounds = loop.run(request, record)

        self.state_store.save_run(record)
        manifest_path = self.artifact_dir / request.loop_type.replace("_", "-") / record.run_id / "artifact-manifest.json"
        if manifest_path.exists():
            import json

            self.state_store.save_artifact_manifest(record.run_id, json.loads(manifest_path.read_text(encoding="utf-8")))
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
            run_id = self._new_run_id(loop_type)
            request = RunRequest(
                run_id=run_id,
                loop_type=loop_type,
                fixture=fixture,
                dry_run=dry_run,
                config_snapshot_hash=self.config.snapshot_hash(),
            )
            try:
                if loop_type == "daily_news" and extra:
                    record = self.create_run_record(request)
                    with self.locks.acquire(f"loop:{loop_type}", run_id):
                        loop = DailyNewsLoop(self.artifact_dir, self.policy, self.renderer)
                        record, _, _ = loop.run(request, record, snapshot_day=extra)
                    self.state_store.save_run(record)
                else:
                    record = self.run_loop(request)
                results.append(record)
                outcome = record.outcome.value if record.outcome else "unknown"
                summary_sections.append(f"## {loop_type}\n\nOutcome: {outcome}\n")
            except Exception as exc:
                failed = self.create_run_record(request)
                failed.phase = RunPhase.TERMINATED
                from loop_pilot.domain.states import RunOutcome

                failed.outcome = RunOutcome.FAILED
                failed.terminal_reason = str(exc)
                failed.finished_at = rfc3339()
                self.state_store.save_run(failed)
                results.append(failed)
                summary_sections.append(f"## {loop_type}\n\nOutcome: failed — {exc}\n")

        summary_dir = self.artifact_dir / "daily-summary"
        summary_dir.mkdir(parents=True, exist_ok=True)
        summary_path = summary_dir / f"{rfc3339()[:10]}-summary.md"
        summary_path.write_text(self.renderer.render_daily_summary(results, summary_sections), encoding="utf-8")
        return results

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

    def _new_run_id(self, loop_type: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{ts}-{loop_type}-001"
