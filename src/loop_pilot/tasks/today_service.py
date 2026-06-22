"""Today view and scheduling."""

from __future__ import annotations

from datetime import datetime

from loop_pilot.tasks.models import QueueItem
from loop_pilot.util.timezone import zone_info
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore


class TodayService:
    def __init__(
        self,
        store: TaskStore,
        queue_service: QueueService | None = None,
        *,
        timezone: str = "Asia/Shanghai",
    ) -> None:
        self.store = store
        self.queue = queue_service or QueueService(store)
        self.timezone = timezone

    def today_date(self) -> str:
        return datetime.now(zone_info(self.timezone)).date().isoformat()

    def list_today(self) -> tuple[str, list[QueueItem]]:
        date = self.today_date()
        return date, self.store.list_today_items(date)

    def add_inbox_to_today(
        self,
        inbox_id: str,
        *,
        loop_type: str | None = None,
        priority: int | None = None,
    ) -> QueueItem:
        existing = self.store.get_queue_by_inbox_id(inbox_id)
        if existing:
            return self.add_queue_to_today(existing.id)
        promoted = self.queue.promote(
            inbox_id,
            loop_type=loop_type,
            priority=priority,
        )
        return self.add_queue_to_today(promoted.id)

    def add_queue_to_today(self, queue_id: str) -> QueueItem:
        queue_item = self.store.get_queue_item(queue_id)
        if queue_item is None:
            raise KeyError(f"queue item not found: {queue_id}")
        if queue_item.status != "queued":
            raise ValueError(f"queue item {queue_id} is not queued")

        date = self.today_date()
        updated = self.store.update_queue_scheduled_for(queue_id, date)
        assert updated is not None
        self.store.record_event(
            entity_type="queue",
            entity_id=queue_id,
            event_type="today_added",
            payload={"scheduled_for": date},
        )
        return updated
