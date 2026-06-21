"""Today service tests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


def test_today_add_inbox_promotes_and_schedules(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    queue = QueueService(store, inbox)
    today = TodayService(store, queue, timezone="UTC")

    item = inbox.add("today task", loop_hint="paper", priority=3).item
    scheduled = today.add_inbox_to_today(item.id, loop_type="paper")

    expected_date = datetime.now(timezone.utc).date().isoformat()
    assert scheduled.scheduled_for == expected_date

    date, items = today.list_today()
    assert date == expected_date
    assert len(items) == 1
    assert items[0].id == scheduled.id


def test_today_add_queue_schedules_existing_item(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    queue = QueueService(store, inbox)
    today = TodayService(store, queue, timezone="Asia/Shanghai")

    item = inbox.add("queue only").item
    promoted = queue.promote(item.id, loop_type="intern")
    scheduled = today.add_queue_to_today(promoted.id)

    expected_date = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    assert scheduled.scheduled_for == expected_date

    events = store.list_events(entity_id=promoted.id)
    assert any(event.event_type == "today_added" for event in events)
