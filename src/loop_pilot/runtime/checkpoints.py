"""Checkpoint persistence at run phase boundaries."""

from __future__ import annotations

from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunPhase
from loop_pilot.storage.base import StateStore


def new_checkpoint_id(run_id: str, phase: RunPhase) -> str:
    safe_run = run_id.replace(":", "_").replace("/", "_")
    return f"cp-{safe_run}-{phase.value.lower()}"


class CheckpointWriter:
    """Writes durable checkpoints when the active store supports V1 semantics."""

    def __init__(self, store: StateStore) -> None:
        self.store = store

    def enabled(self) -> bool:
        return self.store.supports_v1_features()

    def write(
        self,
        record: RunRecord,
        payload: dict[str, Any] | None = None,
        *,
        resume_allowed: bool = False,
    ) -> str | None:
        if not self.enabled():
            return None

        checkpoint_id = new_checkpoint_id(record.run_id, record.phase)
        body: dict[str, Any] = {
            "loop_type": record.loop_type,
            "fixture": record.fixture,
            "dry_run": record.dry_run,
            "current_round": record.current_round,
            "resume_allowed": resume_allowed,
        }
        if payload:
            body.update(payload)

        self.store.save_checkpoint(record.run_id, checkpoint_id, record.phase.value, body)
        record.last_checkpoint_id = checkpoint_id
        self.store.save_run(record)
        return checkpoint_id

    def on_phase_change(self, record: RunRecord) -> None:
        """Hook for loop phase transitions."""
        self.write(record)
