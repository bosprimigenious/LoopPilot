"""Queue store and service tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore


@pytest.fixture
def services(tmp_path: Path) -> tuple[InboxService, QueueService, TaskStore]:
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    queue = QueueService(store, inbox)
    return inbox, queue, store


def test_promote_inbox_to_queue(services: tuple[InboxService, QueueService, TaskStore]) -> None:
    inbox, queue, store = services
    item = inbox.add("fix login test", loop_hint="intern", priority=2).item
    promoted = queue.promote(item.id, loop_type="intern")
    assert promoted.inbox_id == item.id
    assert promoted.loop_type == "intern"
    assert promoted.status == "queued"

    updated_inbox = inbox.get(item.id)
    assert updated_inbox is not None
    assert updated_inbox.status == "promoted"

    events = store.list_events(entity_id=promoted.id)
    assert any(event.event_type == "queue_promoted" for event in events)


def test_demote_queue_back_to_inbox(services: tuple[InboxService, QueueService, TaskStore]) -> None:
    inbox, queue, _store = services
    item = inbox.add("temporary task").item
    promoted = queue.promote(item.id)
    reopened = queue.demote(promoted.id)
    assert reopened.status == "open"
    assert queue.list_items() == []


def test_promote_non_open_inbox_fails(services: tuple[InboxService, QueueService, TaskStore]) -> None:
    inbox, queue, _store = services
    item = inbox.add("already promoted").item
    queue.promote(item.id)
    with pytest.raises(ValueError, match="not open"):
        queue.promote(item.id)
