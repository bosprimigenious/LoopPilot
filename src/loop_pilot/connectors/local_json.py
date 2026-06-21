"""Offline/local source connectors for DailyNews V1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalJsonConnector:
    """Load items from a local JSON file (offline RSS/GitHub snapshot substitute)."""

    def __init__(self, source_id: str, path: Path) -> None:
        self.source_id = source_id
        self.path = path

    def fetch(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            raise FileNotFoundError(f"Local source missing: {self.path}")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        items = data.get("items") or data.get("repositories") or []
        for item in items:
            item.setdefault("source_id", self.source_id)
        return items


def fetch_source(source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch one configured source; failures are isolated per source."""
    kind = str(source_cfg.get("kind", "local_json")).lower()
    source_id = str(source_cfg.get("id", "unknown"))
    if kind == "local_json":
        path = Path(source_cfg["path"])
        return LocalJsonConnector(source_id, path).fetch()
    raise ValueError(f"Unsupported source kind: {kind}")
