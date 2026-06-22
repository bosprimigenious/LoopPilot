"""Map adapter kinds to SafetyLevel for adapter.invoke gate checks."""

from __future__ import annotations

from loop_pilot.adapters.registry import adapter_kind, is_real_adapter_kind
from loop_pilot.safety.levels import SafetyLevel

_KIND_LEVEL: dict[str, SafetyLevel] = {
    "mock": SafetyLevel.COLLECT,
    "cli": SafetyLevel.REAL_GUARDED,
    "cursor_cli": SafetyLevel.REAL_GUARDED,
    "api": SafetyLevel.REAL_BOUNDED,
    "openai_compatible": SafetyLevel.REAL_BOUNDED,
}


def safety_level_for_kind(kind: str) -> SafetyLevel:
    normalized = kind.lower()
    return _KIND_LEVEL.get(normalized, SafetyLevel.REAL_GUARDED)


def safety_level_for_adapter(adapter_config: dict) -> SafetyLevel:
    return safety_level_for_kind(adapter_kind(adapter_config))


def requires_adapter_invoke_gate(kind: str) -> bool:
    return is_real_adapter_kind(kind)
