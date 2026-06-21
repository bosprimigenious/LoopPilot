"""Task domain models for Inbox / Queue / Today."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from loop_pilot.domain.models import rfc3339


def new_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


@dataclass
class InboxItem:
    id: str
    title: str
    body: str | None
    source: str
    source_ref: str | None = None
    loop_hint: str = "unknown"
    priority: int = 3
    status: str = "open"
    dedupe_key: str | None = None
    created_at: str = field(default_factory=rfc3339)
    updated_at: str = field(default_factory=rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> InboxItem:
        return cls(
            id=row["id"],
            title=row["title"],
            body=row["body"],
            source=row["source"],
            source_ref=row["source_ref"],
            loop_hint=row["loop_hint"] or "unknown",
            priority=int(row["priority"]),
            status=row["status"],
            dedupe_key=row["dedupe_key"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class QueueItem:
    id: str
    inbox_id: str | None
    title: str
    body: str | None
    loop_type: str
    priority: int = 3
    status: str = "queued"
    scheduled_for: str | None = None
    created_at: str = field(default_factory=rfc3339)
    updated_at: str = field(default_factory=rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> QueueItem:
        return cls(
            id=row["id"],
            inbox_id=row["inbox_id"],
            title=row["title"],
            body=row["body"],
            loop_type=row["loop_type"],
            priority=int(row["priority"]),
            status=row["status"],
            scheduled_for=row["scheduled_for"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class TaskEvent:
    id: str
    entity_type: str
    entity_id: str
    event_type: str
    payload_json: str | None = None
    created_at: str = field(default_factory=rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
