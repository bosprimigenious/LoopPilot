"""Inbox store and service tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.store import TaskStore


@pytest.fixture
def task_store(tmp_path: Path) -> TaskStore:
    return TaskStore(tmp_path / "loop_pilot.db")


@pytest.fixture
def inbox_service(task_store: TaskStore) -> InboxService:
    return InboxService(task_store)


def test_add_and_list_inbox(inbox_service: InboxService) -> None:
    result = inbox_service.add("fix failing login test", source="manual", loop_hint="intern", priority=2)
    assert result.created is True
    items = inbox_service.list_items(status="open")
    assert len(items) == 1
    assert items[0].title == "fix failing login test"
    assert items[0].loop_hint == "intern"


def test_archive_inbox_item(inbox_service: InboxService, task_store: TaskStore) -> None:
    item = inbox_service.add("archive me").item
    archived = inbox_service.archive(item.id)
    assert archived.status == "archived"
    assert inbox_service.list_items(status="open") == []
    events = task_store.list_events(entity_id=item.id)
    event_types = {event.event_type for event in events}
    assert "inbox_added" in event_types
    assert "inbox_archived" in event_types


def test_dedupe_skips_duplicate(inbox_service: InboxService) -> None:
    first = inbox_service.add("dup task", dedupe_key="dup-001")
    second = inbox_service.add("dup task again", dedupe_key="dup-001")
    assert first.created is True
    assert second.created is False
    assert first.item.id == second.item.id
