"""Schedule install lifecycle status (truthful marker semantics)."""

from __future__ import annotations

from enum import Enum


class InstallStatus(str, Enum):
    PREVIEWED = "previewed"
    BLOCKED = "blocked"
    INSTALLED = "installed"

    @classmethod
    def parse(cls, value: str | None) -> InstallStatus | None:
        if value is None:
            return None
        try:
            return cls(str(value).lower())
        except ValueError:
            return None
