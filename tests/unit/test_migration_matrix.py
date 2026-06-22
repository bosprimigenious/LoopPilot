"""Migration matrix tests for v1→v4 repair paths."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from loop_pilot.storage.db_ops import migrate_database, plan_migrations_for_path, verify_database
from loop_pilot.storage.migrations import CURRENT_SCHEMA_VERSION, MIGRATIONS


def _tables(db_path: Path) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def test_empty_to_latest(tmp_path: Path) -> None:
    db_path = tmp_path / "fresh.db"
    assert not db_path.exists()
    pending = plan_migrations_for_path(db_path)
    assert pending == sorted(MIGRATIONS.keys())
    applied = migrate_database(db_path, dry_run=False)
    assert applied == sorted(MIGRATIONS.keys())
    assert "review_items" in _tables(db_path)
    assert "summaries" in _tables(db_path)


def test_v1_to_latest(tmp_path: Path) -> None:
    db_path = tmp_path / "v1.db"
    conn = sqlite3.connect(db_path)
    MIGRATIONS[1](conn)
    conn.execute("INSERT INTO schema_migrations(version) VALUES (1)")
    conn.commit()
    conn.close()

    applied = migrate_database(db_path, dry_run=False)
    assert 4 in applied or CURRENT_SCHEMA_VERSION in applied
    assert "review_items" in _tables(db_path)


def test_v3_summaries_only_to_v4(tmp_path: Path) -> None:
    db_path = tmp_path / "v3.db"
    conn = sqlite3.connect(db_path)
    for version in (1, 2, 3):
        MIGRATIONS[version](conn)
        conn.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
    conn.commit()
    conn.close()

    assert "review_items" not in _tables(db_path)
    applied = migrate_database(db_path, dry_run=False)
    assert 4 in applied
    assert "review_items" in _tables(db_path)


def test_latest_migrate_again_is_noop(tmp_path: Path) -> None:
    db_path = tmp_path / "noop.db"
    migrate_database(db_path)
    second = migrate_database(db_path)
    assert second == []


def test_dry_run_missing_db_does_not_create_file(tmp_path: Path) -> None:
    db_path = tmp_path / "missing.db"
    before = list(tmp_path.iterdir())
    pending = migrate_database(db_path, dry_run=True)
    after = list(tmp_path.iterdir())
    assert pending == sorted(MIGRATIONS.keys())
    assert before == after
    assert not db_path.exists()


def test_dry_run_existing_db_is_read_only(tmp_path: Path) -> None:
    db_path = tmp_path / "existing.db"
    migrate_database(db_path)
    mtime_before = db_path.stat().st_mtime
    size_before = db_path.stat().st_size
    pending = migrate_database(db_path, dry_run=True)
    assert pending == []
    assert db_path.stat().st_mtime == mtime_before
    assert db_path.stat().st_size == size_before


def test_verify_fails_on_v3_without_review_items(tmp_path: Path) -> None:
    db_path = tmp_path / "v3only.db"
    conn = sqlite3.connect(db_path)
    for version in (1, 2, 3):
        MIGRATIONS[version](conn)
        conn.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
    conn.commit()
    conn.close()

    report = verify_database(db_path, tmp_path / "artifacts")
    messages = [issue.message for issue in report.issues]
    assert any("v4 repair migration" in msg for msg in messages)
    assert report.ok is False


def test_corrupt_schema_reports_missing_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "corrupt.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT)")
    conn.execute("INSERT INTO schema_migrations(version) VALUES (99)")
    conn.commit()
    conn.close()

    report = verify_database(db_path, tmp_path / "artifacts")
    assert report.ok is False
