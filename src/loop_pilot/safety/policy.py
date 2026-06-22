"""Default safe-mode policy: allow levels 0–3, block level 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loop_pilot.config import LoopPilotConfig
from loop_pilot.safety.levels import SafetyLevel

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class SafeAutonomyPolicy:
    config: LoopPilotConfig
    max_level: SafetyLevel = SafetyLevel.REAL_GUARDED
    allow_schedule_install: bool = False
    require_confirm_schedule: bool = True
    require_unattended_safe: bool = True

    @classmethod
    def from_config(cls, config: LoopPilotConfig) -> SafeAutonomyPolicy:
        safety = config.safety if isinstance(config.safety, dict) else {}
        schedule = config.schedule if isinstance(config.schedule, dict) else {}
        unattended = config.runtime.get("unattended", {})
        if not isinstance(unattended, dict):
            unattended = {}
        raw_max = safety.get("max_level", unattended.get("max_level", SafetyLevel.REAL_GUARDED))
        return cls(
            config=config,
            max_level=SafetyLevel.parse(raw_max, default=SafetyLevel.REAL_GUARDED),
            allow_schedule_install=bool(schedule.get("allow_install", False)),
            require_confirm_schedule=bool(schedule.get("require_confirm", True)),
            require_unattended_safe=bool(safety.get("require_unattended_safe", True)),
        )

    def allows_level(self, level: SafetyLevel) -> bool:
        return level <= self.max_level
