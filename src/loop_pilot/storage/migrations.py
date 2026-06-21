"""SQLite schema migrations for V1+ state."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

CURRENT_SCHEMA_VERSION = 3

MigrationFn = Callable[[sqlite3.Connection], None]

MIGRATIONS: dict[int, MigrationFn] = {}


def _migration(version: int) -> Callable[[MigrationFn], MigrationFn]:
    def register(fn: MigrationFn) -> MigrationFn:
        MIGRATIONS[version] = fn
        return fn

    return register


@_migration(1)
def _migrate_v1(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            loop_type TEXT NOT NULL,
            phase TEXT NOT NULL,
            outcome TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checkpoints (
            checkpoint_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(run_id) REFERENCES runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reason TEXT NOT NULL,
            reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(run_id) REFERENCES runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS artifact_manifests (
            run_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(run_id) REFERENCES runs(run_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS run_locks (
            lock_key TEXT PRIMARY KEY,
            holder_run_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


@_migration(2)
def _migrate_v2(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS inbox_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT,
            source TEXT NOT NULL,
            source_ref TEXT,
            loop_hint TEXT,
            priority INTEGER NOT NULL DEFAULT 3,
            status TEXT NOT NULL DEFAULT 'open',
            dedupe_key TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_inbox_items_dedupe_key
        ON inbox_items(dedupe_key)
        WHERE dedupe_key IS NOT NULL
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS queue_items (
            id TEXT PRIMARY KEY,
            inbox_id TEXT,
            title TEXT NOT NULL,
            body TEXT,
            loop_type TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 3,
            status TEXT NOT NULL DEFAULT 'queued',
            scheduled_for TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(inbox_id) REFERENCES inbox_items(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS task_events (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT,
            created_at TEXT NOT NULL
        )
        """
    )


@_migration(3)
def _migrate_v3(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            summary_type TEXT NOT NULL,
            summary_date TEXT NOT NULL,
            path TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'generated',
            run_count INTEGER NOT NULL DEFAULT 0,
            review_count INTEGER NOT NULL DEFAULT 0,
            blocked_count INTEGER NOT NULL DEFAULT 0,
            inbox_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(summary_type, summary_date)
        )
        """
    )


def get_applied_versions(conn: sqlite3.Connection) -> set[int]:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    rows = conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    return {int(row[0]) for row in rows}


def get_current_schema_version(conn: sqlite3.Connection) -> int:
    applied = get_applied_versions(conn)
    return max(applied) if applied else 0


def plan_migrations(conn: sqlite3.Connection) -> list[int]:
    applied = get_applied_versions(conn)
    return sorted(version for version in MIGRATIONS if version not in applied)


def apply_migrations(conn: sqlite3.Connection, *, dry_run: bool = False) -> list[int]:
    pending = plan_migrations(conn)
    if dry_run:
        return pending

    applied: list[int] = []
    for version in pending:
        migration = MIGRATIONS[version]
        migration(conn)
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (version,),
        )
        applied.append(version)
    conn.commit()
    return applied


def required_tables() -> tuple[str, ...]:
    return (
        "schema_migrations",
        "runs",
        "checkpoints",
        "reviews",
        "artifact_manifests",
        "events",
        "run_locks",
        "inbox_items",
        "queue_items",
        "task_events",
        "summaries",
    )
