"""Orchestrator — drives a Run through phases deterministically."""

from __future__ import annotations

import json
import re
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
from loop_pilot.models.router import ModelRouter
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.checkpoints import CheckpointWriter
from loop_pilot.runtime.locks import FileLockStore
from loop_pilot.runtime.recovery import RecoveryPlan, build_recovery_plan
from loop_pilot.runtime.terminal_artifacts import finalize_terminal_artifacts
from loop_pilot.runtime.run_ids import new_run_id
from loop_pilot.storage.base import StateStore
from loop_pilot.tools.broker import ToolBroker
from loop_pilot.workspaces import resolve_workspace

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+"),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
)


class ResumeError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class Orchestrator:
    def __init__(
        self,
        config: LoopPilotConfig,
        state_store: StateStore,
        router: ModelRouter | None = None,
    ) -> None:
        self.config = config
        self.state_store = state_store
        self.router = router or ModelRouter(
            config.models,
            allow_real_adapters=config.allow_real_adapters,
        )
        lock_dir = Path(config.runtime.get("lock_dir", config.state_dir / "locks"))
        self.locks = FileLockStore(lock_dir)
        self.policy = PolicyEngine(config.policies)
        self.renderer = ReportRenderer(Path("templates"))
        self.artifact_dir = Path(config.artifact_dir)
        self.checkpoints = CheckpointWriter(state_store)

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

    def run_loop(
        self,
        request: RunRequest,
        *,
        snapshot_day: str | None = None,
        record: RunRecord | None = None,
        resume_from: dict[str, Any] | None = None,
    ) -> RunRecord:
        if record is None:
            record = self.create_run_record(request)
            record.phase = RunPhase.LOCKING
            self.state_store.save_run(record)
            self.checkpoints.write(record, {"event": "run_started"})

        lock_key = f"loop:{request.loop_type}"
        phase_hook = self.checkpoints.on_phase_change if self.checkpoints.enabled() else None
        effective_allow_real = (
            request.allow_real_adapters
            if request.allow_real_adapters is not None
            else self.config.allow_real_adapters
        )
        router = self.router
        if effective_allow_real != self.router.allow_real_adapters:
            router = ModelRouter(self.config.models, allow_real_adapters=effective_allow_real)

        try:
            with self.locks.acquire(lock_key, request.run_id):
                self.checkpoints.write(record, {"event": "lock_acquired"})
                loop = self._get_loop(request.loop_type, router=router)
                run_kwargs: dict[str, Any] = {
                    "phase_hook": phase_hook,
                    "resume_from": resume_from,
                }
                if request.loop_type in {"intern", "paper"} and request.workspace:
                    run_kwargs["workspace_spec"] = resolve_workspace(
                        self.config.workspaces,
                        request.workspace,
                        loop_type=request.loop_type,
                    )
                if request.loop_type == "daily_news" and request.source_profile:
                    run_kwargs["source_profile"] = self.config.get_source_profile(
                        request.source_profile
                    )
                if request.loop_type == "daily_news" and snapshot_day:
                    record, _, _ = loop.run(request, record, snapshot_day=snapshot_day, **run_kwargs)
                else:
                    record, _, _ = loop.run(request, record, **run_kwargs)
                if (
                    record.outcome == RunOutcome.FAILED
                    and record.terminal_reason
                    and "interrupted" in record.terminal_reason.lower()
                ):
                    self.checkpoints.write(
                        record,
                        {"event": "interrupted", "current_round": record.current_round},
                        resume_allowed=True,
                    )
        except Exception as exc:
            record = self._mark_failed(record, exc, request)
            self.checkpoints.write(record, {"event": "failed", "error": str(exc)}, resume_allowed=True)

        self.state_store.save_run(record)
        finish_payload: dict[str, Any] = {
            "event": "run_finished",
            "outcome": record.outcome.value if record.outcome else None,
        }
        resume_allowed = False
        if (
            record.outcome == RunOutcome.FAILED
            and record.terminal_reason
            and "interrupted" in record.terminal_reason.lower()
        ):
            resume_allowed = True
            finish_payload["event"] = "interrupted"
            finish_payload["current_round"] = record.current_round
        self.checkpoints.write(record, finish_payload, resume_allowed=resume_allowed)
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
        if self.state_store.supports_v1_features():
            from loop_pilot.review.service import ReviewService

            ReviewService(
                config=self.config,
                state_store=self.state_store,
                orchestrator=self,
            ).maybe_enqueue(record)
        return record

    def resume_run(self, run_id: str) -> RunRecord:
        plan = build_recovery_plan(self.state_store, run_id)
        if plan is None:
            raise ResumeError(f"Run not found: {run_id}")
        if not plan.can_resume:
            raise ResumeError(plan.reason)

        record = plan.run
        if record.outcome == RunOutcome.SUCCEEDED:
            raise ResumeError("run already succeeded")

        checkpoint = plan.checkpoint
        payload = checkpoint.get("payload", {})
        record.outcome = None
        record.terminal_reason = None
        record.finished_at = None
        if payload.get("resume_allowed") and payload.get("event") == "interrupted":
            record.phase = RunPhase.ACTING
        elif checkpoint.get("phase"):
            record.phase = RunPhase(checkpoint["phase"])
        request = RunRequest(
            run_id=run_id,
            loop_type=record.loop_type,
            fixture=payload.get("fixture") or record.fixture,
            dry_run=bool(payload.get("dry_run", record.dry_run)),
            config_snapshot_hash=self.config.snapshot_hash(),
        )
        record.attempt_id += 1
        if payload.get("event") == "interrupted":
            record.outcome = None
            record.terminal_reason = None
            record.finished_at = None
        self.checkpoints.write(record, {"event": "resume_started", "from_checkpoint": checkpoint.get("checkpoint_id")})

        resumed = self.run_loop(request, record=record, resume_from=checkpoint)
        self.checkpoints.write(
            resumed,
            {"event": "resume_finished", "from_checkpoint": checkpoint.get("checkpoint_id")},
        )
        return resumed

    def recovery_plan(self, run_id: str) -> RecoveryPlan | None:
        return build_recovery_plan(self.state_store, run_id)

    def run_all(
        self,
        fixture_set: str = "mini",
        profile: str | None = None,
        dry_run: bool = False,
    ) -> list[RunRecord]:
        if profile == "demo" or fixture_set == "demo":
            sequence = [
                ("daily_news", None, None, "demo"),
                ("intern", None, "intern_demo", None),
                ("paper", None, "paper_demo", None),
            ]
        else:
            sequence = [
                ("daily_news", "github_star_snapshots", None, None),
                ("intern", "simple_python_bug", None, None),
                ("paper", "unsupported_claim", None, None),
            ]
        results: list[RunRecord] = []
        summary_sections: list[str] = []

        for loop_type, fixture, workspace, source_profile in sequence:
            request = RunRequest(
                run_id=self.new_run_id(loop_type),
                loop_type=loop_type,
                fixture=fixture,
                workspace=workspace,
                source_profile=source_profile,
                dry_run=dry_run,
                config_snapshot_hash=self.config.snapshot_hash(),
            )
            snapshot_day = "day2" if loop_type == "daily_news" and not source_profile else None
            record = self.run_loop(request, snapshot_day=snapshot_day)
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

    def _mark_failed(self, record: RunRecord, exc: Exception, request: RunRequest) -> RunRecord:
        failed_phase = record.phase.value
        run_dir = self._run_artifact_dir(request, record.run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        tb_text = self._redact_secrets(traceback.format_exc())
        (run_dir / "error-traceback.txt").write_text(tb_text, encoding="utf-8")

        trace_path = run_dir / "trace.jsonl"
        error_event = {
            "event": "error",
            "error_type": type(exc).__name__,
            "error_message": self._redact_secrets(str(exc)),
            "phase": failed_phase,
        }
        with trace_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(error_event, ensure_ascii=False) + "\n")

        record.phase = RunPhase.TERMINATED
        record.outcome = RunOutcome.FAILED
        record.terminal_reason = (
            f"Failed during {failed_phase}: {type(exc).__name__}: {self._redact_secrets(str(exc))}"
        )
        record.finished_at = rfc3339()
        record.report_status = "failed"
        finalize_terminal_artifacts(run_dir, record, gate="blocked")
        return record

    def _run_artifact_dir(self, request: RunRequest, run_id: str) -> Path:
        loop_segment = request.loop_type.replace("_", "-")
        return self.artifact_dir / loop_segment / run_id

    @staticmethod
    def _redact_secrets(text: str) -> str:
        redacted = text
        for pattern in _SECRET_PATTERNS:
            redacted = pattern.sub("<redacted>", redacted)
        return redacted

    def _get_loop(
        self,
        loop_type: str,
        *,
        router: ModelRouter | None = None,
        tool_broker: ToolBroker | None = None,
    ) -> InternLoop | PaperLoop | DailyNewsLoop:
        policy = self._budget_policy(loop_type)
        budget_mgr = BudgetManager(policy)
        active_router = router or self.router
        broker = tool_broker or ToolBroker(self.config.runtime.get("tool_broker", {}))
        if loop_type == "intern":
            return InternLoop(
                self.artifact_dir,
                self.policy,
                self.renderer,
                budget_mgr,
                router=active_router,
                tool_broker=broker,
                config=self.config,
            )
        if loop_type == "paper":
            return PaperLoop(
                self.artifact_dir,
                self.policy,
                self.renderer,
                budget_mgr,
                router=active_router,
                tool_broker=broker,
                config=self.config,
            )
        if loop_type == "daily_news":
            return DailyNewsLoop(
                self.artifact_dir,
                self.policy,
                self.renderer,
                budget_mgr,
                router=active_router,
                tool_broker=broker,
                config=self.config,
            )
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
