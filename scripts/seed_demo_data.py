#!/usr/bin/env python3
"""Seed demo fixture data for local testing only."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

FIXTURES = Path("tests/fixtures")
TARGET = Path("workspaces/demo-seed")


def seed(dry_run: bool = False) -> int:
    mappings = [
        (FIXTURES / "intern/simple_python_bug/input", TARGET / "intern-repo"),
        (FIXTURES / "paper/unsupported_claim/input", TARGET / "paper-draft"),
        (FIXTURES / "daily_news/github_star_snapshots/input", TARGET / "news-snapshots"),
    ]
    print("# Seed Demo Data\n")
    for src, dst in mappings:
        if not src.exists():
            print(f"- SKIP missing: {src}")
            continue
        if dry_run:
            print(f"- Would copy {src} -> {dst}")
        else:
            if dst.exists():
                print(f"- SKIP exists: {dst}")
            else:
                shutil.copytree(src, dst)
                print(f"- Created: {dst}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return seed(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
