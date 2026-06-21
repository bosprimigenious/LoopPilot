"""SQLite persistence for Inbox / Queue / task events."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import rfc3339
from loop_pilot.storage.migrations import apply_migrations
from loop_pilot.tasks.models import InboxItem, QueueItem, TaskEvent, new_task_id


class TaskStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            apply_migrations(conn)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_inbox_item(self, item: InboxItem) -> InboxItem:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO inbox_items (
                    id, title, body, source, source_ref, loop_hint,
                    priority, status, dedupe_key, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.title,
                    item.body,
                    item.source,
                    item.source_ref,
                    item.loop_hint,
                    item.priority,
                    item.status,
                    item.dedupe_key,
                    item.created_at,
                    item.updated_at,
                ),
            )
            conn.commit()
        return item

    def get_inbox_item(self, inbox_id: str) -> InboxItem | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM inbox_items WHERE id = ?", (inbox_id,)).fetchone()
        return InboxItem.from_row(row) if row else None

    def list_inbox_items(self, *, status: str | None = "open") -> list[InboxItem]:
        with self._connect() as conn:
            if status is None or status == "all":
                rows = conn.execute(
                    "SELECT * FROM inbox_items ORDER BY priority ASC, created_at ASC"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM inbox_items WHERE status = ? ORDER BY priority ASC, created_at ASC",
                    (status,),
                ).fetchall()
        return [InboxItem.from_row(row) for row in rows]

    def update_inbox_status(self, inbox_id: str, status: str) -> InboxItem | None:
        now = rfc3339()
        with self._connect() as conn:
            conn.execute(
                "UPDATE inbox_items SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, inbox_id),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM inbox_items WHERE id = ?", (inbox_id,)).fetchone()
        return InboxItem.from_row(row) if row else None

    def inbox_dedupe_exists(self, dedupe_key: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM inbox_items WHERE dedupe_key = ? LIMIT 1",
                (dedupe_key,),
            ).fetchone()
        return row is not None

    def add_queue_item(self, item: QueueItem) -> QueueItem:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO queue_items (
                    id, inbox_id, title, body, loop_type, priority,
                    status, scheduled_for, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.inbox_id,
                    item.title,
                    item.body,
                    item.loop_type,
                    item.priority,
                    item.status,
                    item.scheduled_for,
                    item.created_at,
                    item.updated_at,
                ),
            )
            conn.commit()
        return item

    def get_queue_item(self, queue_id: str) -> QueueItem | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM queue_items WHERE id = ?", (queue_id,)).fetchone()
        return QueueItem.from_row(row) if row else None

    def get_queue_by_inbox_id(self, inbox_id: str) -> QueueItem | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM queue_items
                WHERE inbox_id = ? AND status = 'queued'
                ORDER BY created_at DESC LIMIT 1
                """,
                (inbox_id,),
            ).fetchone()
        return QueueItem.from_row(row) if row else None

    def list_queue_items(self, *, status: str | None = None) -> list[QueueItem]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT * FROM queue_items WHERE status = ?
                    ORDER BY priority ASC, created_at ASC
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM queue_items ORDER BY priority ASC, created_at ASC"
                ).fetchall()
        return [QueueItem.from_row(row) for row in rows]

    def list_today_items(self, scheduled_for: str) -> list[QueueItem]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM queue_items
                WHERE scheduled_for = ? AND status = 'queued'
                ORDER BY priority ASC, created_at ASC
                """,
                (scheduled_for,),
            ).fetchall()
        return [QueueItem.from_row(row) for row in rows]

    def update_queue_scheduled_for(self, queue_id: str, scheduled_for: str | None) -> QueueItem | None:
        now = rfc3339()
        with self._connect() as conn:
            conn.execute(
                "UPDATE queue_items SET scheduled_for = ?, updated_at = ? WHERE id = ?",
                (scheduled_for, now, queue_id),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM queue_items WHERE id = ?", (queue_id,)).fetchone()
        return QueueItem.from_row(row) if row else None

    def delete_queue_item(self, queue_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM queue_items WHERE id = ?", (queue_id,))
            conn.commit()
        return cursor.rowcount > 0

    def record_event(
        self,
        *,
        entity_type: str,
        entity_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> TaskEvent:
        event = TaskEvent(
            id=new_task_id("evt"),
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            payload_json=json.dumps(payload, sort_keys=True) if payload else None,
        )
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO task_events (id, entity_type, entity_id, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.entity_type,
                    event.entity_id,
                    event.event_type,
                    event.payload_json,
                    event.created_at,
                ),
            )
            conn.commit()
        return event

    def list_events(self, entity_id: str | None = None, limit: int = 50) -> list[TaskEvent]:
        with self._connect() as conn:
            if entity_id:
                rows = conn.execute(
                    """
                    SELECT * FROM task_events WHERE entity_id = ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (entity_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM task_events ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            TaskEvent(
                id=row["id"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                event_type=row["event_type"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
