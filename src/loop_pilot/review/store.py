"""SQLite persistence for review_items and decision events."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import rfc3339
from loop_pilot.storage.migrations import apply_migrations
from loop_pilot.tasks.models import new_task_id


@dataclass
class ReviewItem:
    id: str
    run_id: str
    loop_type: str
    status: str
    decision: str | None
    reason: str | None
    deferred_until: str | None
    artifact_path: str | None
    created_at: str
    decided_at: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ReviewItem:
        return cls(
            id=row["id"],
            run_id=row["run_id"],
            loop_type=row["loop_type"],
            status=row["status"],
            decision=row["decision"],
            reason=row["reason"],
            deferred_until=row["deferred_until"],
            artifact_path=row["artifact_path"],
            created_at=row["created_at"],
            decided_at=row["decided_at"],
        )


class ReviewStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            apply_migrations(conn)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def upsert_pending(
        self,
        *,
        run_id: str,
        loop_type: str,
        artifact_path: str | None = None,
    ) -> ReviewItem:
        existing = self.get_by_run_id(run_id)
        if existing is not None and existing.status not in {"pending", "deferred"}:
            return existing
        now = rfc3339()
        if existing is not None and existing.status == "deferred":
            if existing.deferred_until and existing.deferred_until > now[:10]:
                return existing
        if existing is not None:
            with self._connect() as conn:
                conn.execute(
                    """
                    UPDATE review_items
                    SET status = 'pending', artifact_path = ?
                    WHERE run_id = ?
                    """,
                    (artifact_path, run_id),
                )
                conn.commit()
                row = conn.execute("SELECT * FROM review_items WHERE run_id = ?", (run_id,)).fetchone()
            assert row is not None
            return ReviewItem.from_row(row)

        item_id = new_task_id("rev")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO review_items (
                    id, run_id, loop_type, status, decision, reason,
                    deferred_until, artifact_path, created_at, decided_at
                ) VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, ?, ?, NULL)
                """,
                (item_id, run_id, loop_type, artifact_path, now),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM review_items WHERE run_id = ?", (run_id,)).fetchone()
        assert row is not None
        return ReviewItem.from_row(row)

    def get_by_run_id(self, run_id: str) -> ReviewItem | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM review_items WHERE run_id = ?", (run_id,)).fetchone()
        return ReviewItem.from_row(row) if row else None

    def list_pending(self, *, include_deferred: bool = False) -> list[ReviewItem]:
        with self._connect() as conn:
            if include_deferred:
                rows = conn.execute(
                    """
                    SELECT * FROM review_items
                    WHERE status IN ('pending', 'deferred', 'resume_requested')
                    ORDER BY created_at ASC
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM review_items
                    WHERE status = 'pending'
                       OR (status = 'deferred' AND (deferred_until IS NULL OR deferred_until <= ?))
                    ORDER BY created_at ASC
                    """,
                    (rfc3339()[:10],),
                ).fetchall()
        return [ReviewItem.from_row(row) for row in rows]

    def record_decision(
        self,
        run_id: str,
        *,
        decision: str,
        status: str,
        reason: str = "",
        deferred_until: str | None = None,
    ) -> ReviewItem:
        item = self.get_by_run_id(run_id)
        if item is None:
            raise KeyError(f"review item not found for run: {run_id}")
        now = rfc3339()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE review_items
                SET decision = ?, status = ?, reason = ?, deferred_until = ?, decided_at = ?
                WHERE run_id = ?
                """,
                (decision, status, reason, deferred_until, now, run_id),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM review_items WHERE run_id = ?", (run_id,)).fetchone()
        assert row is not None
        return ReviewItem.from_row(row)

    def append_event(
        self,
        *,
        run_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        event_id = new_task_id("evt")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO task_events (id, entity_type, entity_id, event_type, payload_json, created_at)
                VALUES (?, 'review', ?, ?, ?, ?)
                """,
                (event_id, run_id, event_type, json.dumps(payload or {}), rfc3339()),
            )
            conn.commit()

    def append_decision_event(
        self,
        *,
        run_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.append_event(run_id=run_id, event_type=event_type, payload=payload)
