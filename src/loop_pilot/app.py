"""Application wiring."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.config import load_config
from loop_pilot.models.router import ModelRouter
from loop_pilot.runtime.orchestrator import Orchestrator
from loop_pilot.storage.base import StateStore
from loop_pilot.storage.json_store import JsonStateStore
from loop_pilot.storage.sqlite import SQLiteStateStore


class App:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config = load_config(config_dir)
        self.router = ModelRouter(
            self.config.models,
            allow_real_adapters=self.config.allow_real_adapters,
        )
        self.state_store = self._create_state_store()
        self.orchestrator = Orchestrator(self.config, self.state_store, router=self.router)

    @classmethod
    def from_config_dir(cls, config_dir: Path) -> App:
        return cls(config_dir=config_dir)

    def _create_state_store(self) -> StateStore:
        backend = str(self.config.runtime.get("state_backend", "json")).lower()
        if backend == "sqlite":
            return SQLiteStateStore(self.config.sqlite_path)
        return JsonStateStore(self.config.state_dir)
