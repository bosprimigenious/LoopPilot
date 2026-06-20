#!/usr/bin/env python3
"""Apply SQLite state migrations explicitly."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loop_pilot.storage.migrations import CURRENT_SCHEMA_VERSION, apply_migrations  # noqa: E402


def _current_version(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        ).fetchone()
        if row is None:
            return 0
        version_row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(version_row[0] or 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply LoopPilot SQLite state migrations")
    parser.add_argument("--db-path", type=Path, default=Path("var/state/loop-pilot.sqlite3"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    current = _current_version(args.db_path)
    print("# SQLite Migration Plan\n")
    print(f"Current schema version: {current}")
    print(f"Target schema version: {CURRENT_SCHEMA_VERSION}")

    if args.dry_run:
        print("Dry-run: True")
        return 0

    args.db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.db_path) as conn:
        apply_migrations(conn)
    print(f"Migration applied: {args.db_path}")
    print("Dry-run: False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
