"""Schedule configuration profiles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScheduleProfile:
    time: str = "08:30"
    command: str = "loop-pilot run daily --dry-run"
    task_name: str = "LoopPilotDaily"


DEFAULT_PROFILE = ScheduleProfile()


def ready_stage_command(config_dir: Path) -> str:
    return (
        f"loop-pilot --config-dir {config_dir.resolve()} "
        "run daily --unattended --safe --no-dry-run"
    )
