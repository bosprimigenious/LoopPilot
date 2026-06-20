"""State store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord


class StateStore(ABC):
    @abstractmethod
    def save_run(self, record: RunRecord) -> None: ...

    @abstractmethod
    def get_run(self, run_id: str) -> RunRecord | None: ...

    @abstractmethod
    def list_runs(self, limit: int = 50) -> list[RunRecord]: ...

    @abstractmethod
    def save_artifact_manifest(self, run_id: str, manifest: dict[str, Any]) -> Path: ...
