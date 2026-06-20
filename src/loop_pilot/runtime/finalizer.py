"""Finalize runs: terminal phase, outcome, and report status."""

from __future__ import annotations

from loop_pilot.domain.models import ArtifactManifest, RunRecord, rfc3339
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.storage.artifacts import write_manifest


class RunFinalizer:
    def apply_terminal(
        self,
        record: RunRecord,
        outcome: RunOutcome,
        reason: str | None = None,
    ) -> RunRecord:
        record.phase = RunPhase.TERMINATED
        record.outcome = outcome
        record.terminal_reason = reason
        record.finished_at = rfc3339()
        record.report_status = "generated"
        return record

    def persist_manifest(self, path, manifest: ArtifactManifest):
        return write_manifest(path, manifest.to_dict())
