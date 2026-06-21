"""Queue operations."""

from __future__ import annotations

from loop_pilot.domain.models import rfc3339
from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.models import InboxItem, QueueItem, new_task_id
from loop_pilot.tasks.store import TaskStore


class QueueService:
    VALID_LOOP_TYPES = frozenset({"intern", "paper", "daily-news"})

    def __init__(self, store: TaskStore, inbox_service: InboxService | None = None) -> None:
        self.store = store
        self.inbox = inbox_service or InboxService(store)

    def promote(
        self,
        inbox_id: str,
        *,
        loop_type: str | None = None,
        priority: int | None = None,
    ) -> QueueItem:
        item = self.store.get_inbox_item(inbox_id)
        if item is None:
            raise KeyError(f"inbox item not found: {inbox_id}")
        if item.status != "open":
            raise ValueError(f"inbox item {inbox_id} is not open (status={item.status})")

        resolved_loop = loop_type or self._resolve_loop_type(item)
        if resolved_loop not in self.VALID_LOOP_TYPES:
            raise ValueError(f"invalid loop_type: {resolved_loop}")

        resolved_priority = priority if priority is not None else item.priority
        now = rfc3339()
        queue_item = QueueItem(
            id=new_task_id("que"),
            inbox_id=inbox_id,
            title=item.title,
            body=item.body,
            loop_type=resolved_loop,
            priority=resolved_priority,
            status="queued",
            scheduled_for=None,
            created_at=now,
            updated_at=now,
        )
        self.store.update_inbox_status(inbox_id, "promoted")
        saved = self.store.add_queue_item(queue_item)
        self.store.record_event(
            entity_type="queue",
            entity_id=saved.id,
            event_type="queue_promoted",
            payload={"inbox_id": inbox_id, "loop_type": resolved_loop, "priority": resolved_priority},
        )
        return saved

    def list_items(self, *, status: str | None = None) -> list[QueueItem]:
        return self.store.list_queue_items(status=status)

    def demote(self, queue_id: str) -> InboxItem:
        queue_item = self.store.get_queue_item(queue_id)
        if queue_item is None:
            raise KeyError(f"queue item not found: {queue_id}")
        if queue_item.status != "queued":
            raise ValueError(f"queue item {queue_id} cannot be demoted (status={queue_item.status})")

        inbox_id = queue_item.inbox_id
        if inbox_id is None:
            self.store.delete_queue_item(queue_id)
            raise ValueError(f"queue item {queue_id} has no linked inbox")

        self.store.delete_queue_item(queue_id)
        updated = self.store.update_inbox_status(inbox_id, "open")
        assert updated is not None
        self.store.record_event(
            entity_type="queue",
            entity_id=queue_id,
            event_type="queue_demoted",
            payload={"inbox_id": inbox_id},
        )
        return updated

    def get(self, queue_id: str) -> QueueItem | None:
        return self.store.get_queue_item(queue_id)

    @staticmethod
    def _resolve_loop_type(item: InboxItem) -> str:
        if item.loop_hint in {"intern", "paper", "daily-news"}:
            return item.loop_hint
        return "intern"
