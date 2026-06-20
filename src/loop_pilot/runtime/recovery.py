"""Recovery helpers for V1 checkpoint inspection and resume planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.approvals import approval_allows_resume
from loop_pilot.storage.base import StateStore


@dataclass
class RecoveryPlan:
    run: RunRecord
    checkpoint: dict[str, Any]
    can_resume: bool
    reason: str


def build_recovery_plan(store: StateStore, run_id: str) -> RecoveryPlan | None:
    run = store.get_run(run_id)
    if run is None:
        return None

    if run.outcome == RunOutcome.CANCELLED:
        return RecoveryPlan(run=run, checkpoint={}, can_resume=False, reason="run was cancelled")

    checkpoint = store.latest_checkpoint(run_id)

    if run.phase == RunPhase.TERMINATED and run.outcome == RunOutcome.SUCCEEDED:
        return RecoveryPlan(run=run, checkpoint=checkpoint or {}, can_resume=False, reason="run already succeeded")

    if run.phase == RunPhase.TERMINATED and run.outcome is not None:
        payload = (checkpoint or {}).get("payload", {})
        if payload.get("resume_allowed"):
            return RecoveryPlan(
                run=run,
                checkpoint=checkpoint or {},
                can_resume=True,
                reason="checkpoint available for retry",
            )
        return RecoveryPlan(run=run, checkpoint=checkpoint or {}, can_resume=False, reason="run already terminated")

    if checkpoint is None:
        return RecoveryPlan(run=run, checkpoint={}, can_resume=False, reason="no checkpoint")

    payload = checkpoint.get("payload", {})
    if payload.get("cancelled"):
        return RecoveryPlan(run=run, checkpoint=checkpoint, can_resume=False, reason="checkpoint marked cancelled")

    if run.phase == RunPhase.WAITING_APPROVAL:
        if not approval_allows_resume(store, run_id):
            return RecoveryPlan(
                run=run,
                checkpoint=checkpoint,
                can_resume=False,
                reason="awaiting user approval",
            )
        return RecoveryPlan(run=run, checkpoint=checkpoint, can_resume=True, reason="approved; ready to continue")

    if payload.get("resume_allowed") or run.phase.value == checkpoint.get("phase"):
        return RecoveryPlan(run=run, checkpoint=checkpoint, can_resume=True, reason="checkpoint available")

    return RecoveryPlan(
        run=run,
        checkpoint=checkpoint,
        can_resume=False,
        reason="checkpoint does not match current phase",
    )
