"""Unique run id generation."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def new_run_id(loop_type: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    suffix = uuid4().hex[:8]
    return f"{ts}-{loop_type}-{suffix}"
