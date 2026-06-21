"""Schedule configuration profiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduleProfile:
    time: str = "08:30"
    command: str = "loop-pilot run daily --dry-run"
    task_name: str = "LoopPilotDaily"


DEFAULT_PROFILE = ScheduleProfile()
