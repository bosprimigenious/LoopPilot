"""Application wiring."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.config import LoopPilotConfig, load_config
from loop_pilot.runtime.orchestrator import Orchestrator
from loop_pilot.storage.base import StateStore
from loop_pilot.storage.json_store import JsonStateStore


class App:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config = load_config(config_dir)
        self.state_store = JsonStateStore(self.config.state_dir)
        self.orchestrator = Orchestrator(self.config, self.state_store)

    @classmethod
    def from_config_dir(cls, config_dir: Path) -> App:
        return cls(config_dir=config_dir)
