#!/usr/bin/env python3
"""Back up local LoopPilot state, config, and SQLite checkpoints."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def _iter_existing(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


def _copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up local LoopPilot state")
    parser.add_argument("--state-dir", type=Path, default=Path("var/state"))
    parser.add_argument("--config-dir", type=Path, default=Path("config"))
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path("var/state/loop-pilot.sqlite3"),
        help="SQLite DB containing V1 checkpoints (orchestrator default)",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Legacy JSON checkpoint dir; omitted when sqlite-path is used",
    )
    parser.add_argument("--backup-dir", type=Path, default=Path("var/backups"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target_root = args.backup_dir / stamp
    sources = _iter_existing([args.state_dir, args.config_dir, args.sqlite_path])
    if args.checkpoint_dir and args.checkpoint_dir.exists():
        sources.append(args.checkpoint_dir)

    print("# Backup Plan\n")
    if not sources:
        print("- No local state/config/checkpoints found")
        return 0

    for source in sources:
        destination = target_root / source.name
        prefix = "Would back up" if args.dry_run else "Backed up"
        print(f"- {prefix}: {source} -> {destination}")
        if not args.dry_run:
            _copy_path(source, destination)

    if args.sqlite_path.exists():
        print("\n## SQLite checkpoints\n")
        print(f"- V1 checkpoints stored in {args.sqlite_path} (checkpoints table)")

    if args.checkpoint_dir and args.checkpoint_dir.exists():
        print("\n## Legacy checkpoints\n")
        for checkpoint in sorted(args.checkpoint_dir.rglob("*")):
            if checkpoint.is_file():
                print(f"- {checkpoint.relative_to(args.checkpoint_dir)}")

    print(f"\nDry-run: {args.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
