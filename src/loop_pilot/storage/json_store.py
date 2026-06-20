"""JSON file state store for Mini."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.storage.base import StateStore


class JsonStateStore(StateStore):
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.runs_dir = state_dir / "runs"
        self.manifests_dir = state_dir / "manifests"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)

    def _run_path(self, run_id: str) -> Path:
        safe_id = run_id.replace(":", "_").replace("/", "_")
        return self.runs_dir / f"{safe_id}.json"

    def save_run(self, record: RunRecord) -> None:
        path = self._run_path(record.run_id)
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")

    def get_run(self, run_id: str) -> RunRecord | None:
        path = self._run_path(run_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return RunRecord.from_dict(data)

    def list_runs(self, limit: int = 50) -> list[RunRecord]:
        records: list[RunRecord] = []
        for path in sorted(self.runs_dir.glob("*.json"), reverse=True)[:limit]:
            data = json.loads(path.read_text(encoding="utf-8"))
            records.append(RunRecord.from_dict(data))
        return records

    def save_artifact_manifest(self, run_id: str, manifest: dict[str, Any]) -> Path:
        safe_id = run_id.replace(":", "_").replace("/", "_")
        path = self.manifests_dir / f"{safe_id}-manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path


# Backward-compatible alias
LocalStateStore = JsonStateStore
