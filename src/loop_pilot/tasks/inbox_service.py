"""Inbox operations."""

from __future__ import annotations

from dataclasses import dataclass

from loop_pilot.domain.models import rfc3339
from loop_pilot.tasks.models import InboxItem, new_task_id
from loop_pilot.tasks.store import TaskStore


@dataclass
class InboxAddResult:
    item: InboxItem
    created: bool


class InboxService:
    VALID_SOURCES = frozenset({"manual", "daily-news", "intern", "paper", "import"})
    VALID_LOOP_HINTS = frozenset({"intern", "paper", "daily-news", "unknown"})
    VALID_STATUSES = frozenset({"open", "promoted", "archived"})

    def __init__(self, store: TaskStore) -> None:
        self.store = store

    def add(
        self,
        title: str,
        *,
        body: str | None = None,
        source: str = "manual",
        source_ref: str | None = None,
        loop_hint: str = "unknown",
        priority: int = 3,
        dedupe_key: str | None = None,
    ) -> InboxAddResult:
        if source not in self.VALID_SOURCES:
            raise ValueError(f"invalid inbox source: {source}")
        if loop_hint not in self.VALID_LOOP_HINTS:
            raise ValueError(f"invalid loop_hint: {loop_hint}")
        if dedupe_key and self.store.inbox_dedupe_exists(dedupe_key):
            existing = self._find_by_dedupe_key(dedupe_key)
            if existing:
                return InboxAddResult(item=existing, created=False)

        now = rfc3339()
        item = InboxItem(
            id=new_task_id("inb"),
            title=title.strip(),
            body=body,
            source=source,
            source_ref=source_ref,
            loop_hint=loop_hint,
            priority=priority,
            status="open",
            dedupe_key=dedupe_key,
            created_at=now,
            updated_at=now,
        )
        saved = self.store.add_inbox_item(item)
        self.store.record_event(
            entity_type="inbox",
            entity_id=saved.id,
            event_type="inbox_added",
            payload={"source": source, "loop_hint": loop_hint, "priority": priority},
        )
        return InboxAddResult(item=saved, created=True)

    def list_items(self, *, status: str = "open") -> list[InboxItem]:
        if status not in self.VALID_STATUSES and status != "all":
            raise ValueError(f"invalid inbox status filter: {status}")
        return self.store.list_inbox_items(status=status)

    def archive(self, inbox_id: str) -> InboxItem:
        item = self.store.get_inbox_item(inbox_id)
        if item is None:
            raise KeyError(f"inbox item not found: {inbox_id}")
        if item.status == "archived":
            return item
        updated = self.store.update_inbox_status(inbox_id, "archived")
        assert updated is not None
        self.store.record_event(
            entity_type="inbox",
            entity_id=inbox_id,
            event_type="inbox_archived",
        )
        return updated

    def get(self, inbox_id: str) -> InboxItem | None:
        return self.store.get_inbox_item(inbox_id)

    def _find_by_dedupe_key(self, dedupe_key: str) -> InboxItem | None:
        for item in self.store.list_inbox_items(status="all"):
            if item.dedupe_key == dedupe_key:
                return item
        return None
