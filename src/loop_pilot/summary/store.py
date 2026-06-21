"""Persist summary metadata in SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from loop_pilot.domain.models import rfc3339
from loop_pilot.storage.migrations import apply_migrations
from loop_pilot.summary.models import SummaryRecord
from loop_pilot.tasks.models import new_task_id


class SummaryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            apply_migrations(conn)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def upsert_summary(self, record: SummaryRecord) -> SummaryRecord:
        now = rfc3339()
        with self._connect() as conn:
            existing = conn.execute(
                """
                SELECT id, created_at FROM summaries
                WHERE summary_type = ? AND summary_date = ?
                """,
                (record.summary_type, record.summary_date),
            ).fetchone()
            summary_id = existing["id"] if existing else (record.id or new_task_id("sum"))
            created_at = existing["created_at"] if existing else now
            conn.execute(
                """
                INSERT INTO summaries (
                    id, summary_type, summary_date, path, status,
                    run_count, review_count, blocked_count, inbox_count,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(summary_type, summary_date) DO UPDATE SET
                    path = excluded.path,
                    status = excluded.status,
                    run_count = excluded.run_count,
                    review_count = excluded.review_count,
                    blocked_count = excluded.blocked_count,
                    inbox_count = excluded.inbox_count,
                    updated_at = excluded.updated_at
                """,
                (
                    summary_id,
                    record.summary_type,
                    record.summary_date,
                    str(record.path),
                    record.status,
                    record.run_count,
                    record.review_count,
                    record.blocked_count,
                    record.inbox_count,
                    created_at,
                    now,
                ),
            )
            conn.commit()
            row = conn.execute(
                """
                SELECT * FROM summaries
                WHERE summary_type = ? AND summary_date = ?
                """,
                (record.summary_type, record.summary_date),
            ).fetchone()
        assert row is not None
        return self._row_to_record(row)

    def get_summary(self, summary_type: str, summary_date: str) -> SummaryRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM summaries
                WHERE summary_type = ? AND summary_date = ?
                """,
                (summary_type, summary_date),
            ).fetchone()
        return self._row_to_record(row) if row else None

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> SummaryRecord:
        return SummaryRecord(
            id=row["id"],
            summary_type=row["summary_type"],
            summary_date=row["summary_date"],
            path=row["path"],
            status=row["status"],
            run_count=int(row["run_count"]),
            review_count=int(row["review_count"]),
            blocked_count=int(row["blocked_count"]),
            inbox_count=int(row["inbox_count"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
