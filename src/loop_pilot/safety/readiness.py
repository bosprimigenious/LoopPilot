"""Readiness gate — fail-closed until 0.5-ready prerequisites are met."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loop_pilot.config import LoopPilotConfig

PREP_STAGE = "prep"
READY_STAGE = "ready"
PREP_STAGE_BLOCKED = "PREP_STAGE_BLOCKED"
READY_STAGE_REQUIRED = "READY_STAGE_REQUIRED"


def safety_stage(config: LoopPilotConfig) -> str:
    safety = config.safety if isinstance(config.safety, dict) else {}
    return str(safety.get("stage", PREP_STAGE)).lower()


def is_prep_stage(config: LoopPilotConfig) -> bool:
    return safety_stage(config) != READY_STAGE


def is_ready_stage(config: LoopPilotConfig) -> bool:
    return safety_stage(config) == READY_STAGE


def prep_block_message(action: str) -> str:
    return (
        f"{action} is blocked in 0.5-prep; set safety.stage=ready after 0.4c + readiness gate"
    )
