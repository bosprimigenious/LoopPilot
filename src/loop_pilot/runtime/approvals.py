"""Approval workflow helpers for V1 review commands."""

from __future__ import annotations

from loop_pilot.domain.models import RunRecord, rfc3339
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.checkpoints import CheckpointWriter
from loop_pilot.storage.base import StateStore


class ApprovalError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def latest_review_decision(store: StateStore, run_id: str) -> str | None:
    reviews = store.list_reviews(run_id)
    if not reviews:
        return None
    return reviews[-1]["decision"]


def approve_run(store: StateStore, run_id: str) -> RunRecord:
    record = _require_run(store, run_id)
    if record.phase != RunPhase.WAITING_APPROVAL:
        raise ApprovalError(f"Run {run_id} is not waiting for approval (phase={record.phase.value})")
    if record.outcome == RunOutcome.CANCELLED:
        raise ApprovalError(f"Run {run_id} was cancelled")

    store.record_review(run_id, "approve", "")
    record.review_status = "approved"
    CheckpointWriter(store).write(record, {"pending_action": "resume"}, resume_allowed=True)
    return record


def reject_run(store: StateStore, run_id: str, reason: str) -> RunRecord:
    record = _require_run(store, run_id)
    store.record_review(run_id, "reject", reason)
    record.review_status = "rejected"
    record.phase = RunPhase.TERMINATED
    record.outcome = RunOutcome.BLOCKED
    record.terminal_reason = reason
    record.finished_at = rfc3339()
    record.report_status = "generated"
    store.save_run(record)
    return record


def cancel_run(store: StateStore, run_id: str, reason: str = "Cancelled by user") -> RunRecord:
    record = _require_run(store, run_id)
    if record.phase == RunPhase.TERMINATED and record.outcome == RunOutcome.CANCELLED:
        return record

    store.record_review(run_id, "cancel", reason)
    record.review_status = "cancelled"
    record.phase = RunPhase.TERMINATED
    record.outcome = RunOutcome.CANCELLED
    record.terminal_reason = reason
    record.finished_at = rfc3339()
    record.report_status = "generated"
    CheckpointWriter(store).write(record, {"cancelled": True}, resume_allowed=False)
    store.save_run(record)
    return record


def approval_allows_resume(store: StateStore, run_id: str) -> bool:
    return latest_review_decision(store, run_id) == "approve"


def _require_run(store: StateStore, run_id: str) -> RunRecord:
    record = store.get_run(run_id)
    if record is None:
        raise ApprovalError(f"Run not found: {run_id}")
    return record
