"""DailyNews candidate-actions importer tests."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.tasks.daily_news_importer import DailyNewsImporter
from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.store import TaskStore


def test_import_daily_news_candidates(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/tasks/candidate-actions.json")
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    importer = DailyNewsImporter(inbox)

    result = importer.import_from_file(fixture, dry_run=False)
    assert len(result.imported) == 2
    assert result.skipped_duplicates == []
    assert len(inbox.list_items(status="all")) == 2


def test_import_deduplicates_on_second_run(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/tasks/candidate-actions.json")
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    importer = DailyNewsImporter(inbox)

    first = importer.import_from_file(fixture, dry_run=False)
    second = importer.import_from_file(fixture, dry_run=False)

    assert len(first.imported) == 2
    assert len(second.imported) == 0
    assert len(second.skipped_duplicates) == 2
    assert len(inbox.list_items(status="all")) == 2


def test_import_dry_run_does_not_persist(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/tasks/candidate-actions.json")
    store = TaskStore(tmp_path / "loop_pilot.db")
    inbox = InboxService(store)
    importer = DailyNewsImporter(inbox)

    result = importer.import_from_file(fixture, dry_run=True)
    assert len(result.preview) == 2
    assert inbox.list_items(status="all") == []
