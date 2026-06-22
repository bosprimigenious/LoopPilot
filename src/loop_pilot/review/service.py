"""Review queue and human decision service."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loop_pilot.config import LoopPilotConfig
from loop_pilot.domain.models import RunRecord, rfc3339
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.review.errors import ReviewDecisionError
from loop_pilot.review.review_agent import suggest_review, write_suggestion
from loop_pilot.review.store import ReviewItem, ReviewStore
from loop_pilot.runtime.approvals import ApprovalError, approve_run, cancel_run, reject_run
from loop_pilot.runtime.recovery import build_recovery_plan
from loop_pilot.runtime.terminal_artifacts import finalize_terminal_artifacts
from loop_pilot.storage.base import StateStore
from loop_pilot.summary.collector import read_gate_result, run_artifact_dir

if TYPE_CHECKING:
    from loop_pilot.runtime.orchestrator import Orchestrator


def write_review_suggestion(run_dir: Path, record: RunRecord, gate: str) -> Path:
    suggestion = suggest_review(record, run_dir)
    suggestion["gate"] = gate
    return write_suggestion(run_dir, suggestion)


def mark_patch_run_waiting_review(
    *,
    artifact_dir: Path,
    record: RunRecord,
    state_store: StateStore | None = None,
) -> RunRecord:
    """Patch-producing runs are not final success until a human approves."""
    record.phase = RunPhase.TERMINATED
    record.outcome = RunOutcome.PARTIAL
    record.review_status = "needs_review"
    record.report_status = "needs_review"
    record.terminal_reason = record.terminal_reason or "Patch produced; waiting for human review"
    run_dir = run_artifact_dir(artifact_dir, record.loop_type, record.run_id)
    finalize_terminal_artifacts(
        run_dir,
        record,
        gate="needs_review",
        review_required=True,
    )
    if state_store is not None:
        state_store.save_run(record)
    return record


class ReviewService:
    def __init__(
        self,
        *,
        config: LoopPilotConfig,
        state_store: StateStore,
        orchestrator: Orchestrator,
    ) -> None:
        self.config = config
        self.state_store = state_store
        self.orchestrator = orchestrator
        self.store = ReviewStore(config.sqlite_path)
        self.artifact_dir = Path(config.artifact_dir)

    def maybe_enqueue(self, record: RunRecord) -> ReviewItem | None:
        if not self._needs_review(record):
            return None
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, record.run_id)
        has_patch = (run_dir / "patch.diff").exists()
        if has_patch and record.review_status not in {"approved", "rejected", "cancelled"}:
            record = mark_patch_run_waiting_review(
                artifact_dir=self.artifact_dir,
                record=record,
                state_store=self.state_store,
            )
        elif record.review_status is None:
            record.review_status = "pending"
        gate = read_gate_result(self.artifact_dir, record.loop_type, record.run_id) or "needs_review"
        write_review_suggestion(run_dir, record, gate)
        review_path = run_dir / "review_required.md"
        if not review_path.exists():
            legacy = run_dir / "review-required.md"
            if legacy.exists():
                review_path.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                review_path.write_text(
                    f"# Review required\n\nRun `{record.run_id}` needs human review.\n",
                    encoding="utf-8",
                )
        item = self.store.upsert_pending(
            run_id=record.run_id,
            loop_type=record.loop_type,
            artifact_path=str(run_dir),
        )
        self.state_store.save_run(record)
        self.store.append_event(run_id=record.run_id, event_type="review_enqueued")
        return item

    def sync_from_runs(self) -> None:
        for record in self.state_store.list_runs(limit=500):
            self.maybe_enqueue(record)

    def list_pending(self) -> list[tuple[ReviewItem, RunRecord | None]]:
        self.sync_from_runs()
        rows: list[tuple[ReviewItem, RunRecord | None]] = []
        for item in self.store.list_pending():
            if item.status == "deferred" and item.deferred_until and item.deferred_until > rfc3339()[:10]:
                continue
            record = self.state_store.get_run(item.run_id)
            rows.append((item, record))
        return rows

    def show(self, run_id: str) -> tuple[ReviewItem | None, RunRecord | None]:
        item = self.store.get_by_run_id(run_id)
        record = self.state_store.get_run(run_id)
        return item, record

    def approve(self, run_id: str, note: str = "", *, actor: str = "human") -> RunRecord:
        if actor != "human":
            raise ApprovalError("workers cannot self-approve review items")
        self._require_decidable_item(run_id)
        record = self.state_store.get_run(run_id)
        if record is None:
            raise ApprovalError(f"Run not found: {run_id}")
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, run_id)
        if (run_dir / "patch.diff").exists():
            self.state_store.record_review(run_id, "approve", note)
            record.review_status = "approved"
            record.phase = RunPhase.TERMINATED
            record.outcome = RunOutcome.SUCCEEDED
            record.report_status = "completed"
            record.finished_at = record.finished_at or rfc3339()
            self.store.record_decision(
                run_id,
                decision="approve",
                status="approved",
                reason=note,
            )
            finalize_terminal_artifacts(run_dir, record, gate="pass", review_required=False)
        else:
            record = approve_run(self.state_store, run_id)
            self.store.record_decision(
                run_id,
                decision="approve",
                status="approved",
                reason=note,
            )
        self.store.append_event(run_id=run_id, event_type="review_approved", payload={"note": note})
        self.state_store.save_run(record)
        return record

    def reject(self, run_id: str, reason: str) -> RunRecord:
        if not reason.strip():
            raise ApprovalError("reject requires --reason")
        self._require_decidable_item(run_id)
        record = reject_run(self.state_store, run_id, reason)
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, run_id)
        finalize_terminal_artifacts(run_dir, record, gate="blocked", review_required=True)
        self.store.record_decision(run_id, decision="reject", status="rejected", reason=reason)
        self.store.append_event(run_id=run_id, event_type="review_rejected", payload={"reason": reason})
        return record

    def defer(self, run_id: str, until: str, reason: str = "") -> ReviewItem:
        self._require_decidable_item(run_id)
        updated = self.store.record_decision(
            run_id,
            decision="defer",
            status="deferred",
            reason=reason or f"deferred until {until}",
            deferred_until=until,
        )
        self.store.append_event(
            run_id=run_id,
            event_type="review_deferred",
            payload={"until": until, "reason": reason},
        )
        return updated

    def cancel(self, run_id: str, reason: str) -> RunRecord:
        self._require_decidable_item(run_id)
        record = cancel_run(self.state_store, run_id, reason)
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, run_id)
        finalize_terminal_artifacts(run_dir, record, gate="blocked", review_required=True)
        self.store.record_decision(run_id, decision="cancel", status="cancelled", reason=reason)
        self.store.append_event(run_id=run_id, event_type="review_cancelled", payload={"reason": reason})
        return record

    def resume(self, run_id: str) -> RunRecord:
        from loop_pilot.runtime.orchestrator import ResumeError

        item = self.store.get_by_run_id(run_id)
        if item is not None and item.status in {"rejected", "cancelled"}:
            raise ResumeError(f"cannot resume a {item.status} run")
        record = self.state_store.get_run(run_id)
        if record is None:
            raise ResumeError(f"Run not found: {run_id}")
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, run_id)
        if (run_dir / "patch.diff").exists() and record.review_status == "needs_review":
            raise ResumeError("requires approve/reject/cancel, not resume")
        if record.review_status in {"rejected", "cancelled"}:
            raise ResumeError(f"cannot resume run with review_status={record.review_status}")
        if (
            record.review_status == "approved"
            and record.phase == RunPhase.TERMINATED
            and record.outcome == RunOutcome.SUCCEEDED
        ):
            raise ResumeError("cannot resume: run already finalized after approval")
        plan = build_recovery_plan(self.state_store, run_id)
        if plan is None:
            raise ResumeError(f"Run not found: {run_id}")
        payload = (plan.checkpoint or {}).get("payload", {})
        if payload.get("phase") == RunPhase.ACTING.value and payload.get("event") == "interrupted":
            if not payload.get("resume_allowed"):
                raise ResumeError("resume blocked while run was interrupted during ACTING")
        return self.orchestrator.resume_run(run_id)

    def _require_item(self, run_id: str) -> ReviewItem:
        item = self.store.get_by_run_id(run_id)
        if item is None:
            self.sync_from_runs()
            item = self.store.get_by_run_id(run_id)
        if item is None:
            raise ApprovalError(f"No review item for run: {run_id}")
        return item

    def _require_decidable_item(self, run_id: str) -> ReviewItem:
        item = self._require_item(run_id)
        if item.status not in {"pending", "deferred"}:
            raise ReviewDecisionError(f"review item for run {run_id} is already decided: {item.status}")
        return item

    def _needs_review(self, record: RunRecord) -> bool:
        if record.phase == RunPhase.WAITING_APPROVAL:
            return True
        if record.review_status in {"pending", "needs_review", "needs_revision", "resume_requested"}:
            return True
        if record.outcome in {RunOutcome.PARTIAL, RunOutcome.BLOCKED, RunOutcome.EXHAUSTED}:
            return True
        gate = read_gate_result(self.artifact_dir, record.loop_type, record.run_id)
        if gate in {"needs_review", "blocked"}:
            return True
        run_dir = run_artifact_dir(self.artifact_dir, record.loop_type, record.run_id)
        return record.outcome == RunOutcome.SUCCEEDED and (run_dir / "patch.diff").exists()
