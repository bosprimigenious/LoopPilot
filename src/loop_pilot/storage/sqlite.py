"""SQLite StateStore for V1 checkpoint and recovery semantics."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.storage.base import StateStore
from loop_pilot.storage.migrations import apply_migrations


class SQLiteStateStore(StateStore):
    def supports_v1_features(self) -> bool:
        return True

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            apply_migrations(conn)

    def save_run(self, record: RunRecord) -> None:
        payload = json.dumps(record.to_dict(), sort_keys=True)
        outcome = record.outcome.value if record.outcome else None
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs(run_id, payload, loop_type, phase, outcome, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(run_id) DO UPDATE SET
                  payload = excluded.payload,
                  loop_type = excluded.loop_type,
                  phase = excluded.phase,
                  outcome = excluded.outcome,
                  updated_at = CURRENT_TIMESTAMP
                """,
                (record.run_id, payload, record.loop_type, record.phase.value, outcome),
            )
            conn.commit()

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return RunRecord.from_dict(json.loads(row["payload"]))

    def list_runs(self, limit: int = 50) -> list[RunRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload FROM runs ORDER BY updated_at DESC, rowid DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [RunRecord.from_dict(json.loads(row["payload"])) for row in rows]

    def save_artifact_manifest(self, run_id: str, manifest: dict[str, Any]) -> Path:
        payload = json.dumps(manifest, sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO artifact_manifests(run_id, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(run_id) DO UPDATE SET
                  payload = excluded.payload,
                  updated_at = CURRENT_TIMESTAMP
                """,
                (run_id, payload),
            )
            conn.commit()
        return self.db_path

    def save_checkpoint(
        self,
        run_id: str,
        checkpoint_id: str,
        phase: str,
        payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints(checkpoint_id, run_id, phase, payload, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (checkpoint_id, run_id, phase, json.dumps(payload, sort_keys=True)),
            )
            conn.commit()

    def latest_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT checkpoint_id, run_id, phase, payload, created_at
                FROM checkpoints
                WHERE run_id = ?
                ORDER BY created_at DESC, rowid DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "checkpoint_id": row["checkpoint_id"],
            "run_id": row["run_id"],
            "phase": row["phase"],
            "payload": json.loads(row["payload"]),
            "created_at": row["created_at"],
        }

    def record_review(self, run_id: str, decision: str, reason: str = "") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO reviews(run_id, decision, reason) VALUES (?, ?, ?)",
                (run_id, decision, reason),
            )
            conn.commit()

    def list_reviews(self, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT review_id, run_id, decision, reason, reviewed_at
                FROM reviews
                WHERE run_id = ?
                ORDER BY review_id
                """,
                (run_id,),
            ).fetchall()
        return [dict(row) for row in rows]
