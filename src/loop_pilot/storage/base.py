"""State store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord


class StateStore(ABC):
    def supports_v1_features(self) -> bool:
        return False

    @abstractmethod
    def save_run(self, record: RunRecord) -> None: ...

    @abstractmethod
    def get_run(self, run_id: str) -> RunRecord | None: ...

    @abstractmethod
    def list_runs(self, limit: int = 50) -> list[RunRecord]: ...

    @abstractmethod
    def save_artifact_manifest(self, run_id: str, manifest: dict[str, Any]) -> Path: ...

    def save_checkpoint(
        self,
        run_id: str,
        checkpoint_id: str,
        phase: str,
        payload: dict[str, Any],
    ) -> None:
        raise NotImplementedError("checkpoints require V1 storage")

    def latest_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("checkpoints require V1 storage")

    def record_review(self, run_id: str, decision: str, reason: str = "") -> None:
        raise NotImplementedError("reviews require V1 storage")

    def list_reviews(self, run_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError("reviews require V1 storage")
