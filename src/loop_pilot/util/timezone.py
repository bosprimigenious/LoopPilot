"""Timezone helpers with tzdata fallback."""

from __future__ import annotations

from datetime import timezone
from zoneinfo import ZoneInfo


def zone_info(name: str) -> ZoneInfo | timezone:
    try:
        return ZoneInfo(name)
    except Exception:
        if name in {"UTC", "Etc/UTC"}:
            return timezone.utc
        raise
