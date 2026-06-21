"""Safety autonomy levels 0–4."""

from __future__ import annotations

from enum import IntEnum


class SafetyLevel(IntEnum):
    OBSERVE = 0
    COLLECT = 1
    MOCK_EXECUTE = 2
    REAL_GUARDED = 3
    REAL_BOUNDED = 4

    @classmethod
    def parse(cls, value: int | str | None, *, default: int = 0) -> SafetyLevel:
        if value is None:
            return cls(default)
        try:
            level = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid safety level: {value!r}") from exc
        if level not in range(5):
            raise ValueError(f"safety level must be 0–4, got {level}")
        return cls(level)

    @property
    def label(self) -> str:
        return {
            SafetyLevel.OBSERVE: "observe",
            SafetyLevel.COLLECT: "collect",
            SafetyLevel.MOCK_EXECUTE: "mock_execute",
            SafetyLevel.REAL_GUARDED: "real_guarded",
            SafetyLevel.REAL_BOUNDED: "real_bounded",
        }[self]
