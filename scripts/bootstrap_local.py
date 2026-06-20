#!/usr/bin/env python3
"""Create local directories and example configuration without overwriting."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from loop_pilot.config import default_config_dict

CONFIG_FILES = [
    "loop-pilot.yaml",
    "intern.yaml",
    "paper.yaml",
    "daily_news.yaml",
    "policies.yaml",
    "sources.yaml",
    "models.yaml",
]

DIRS = ["var/state", "var/artifacts", "var/checkpoints"]


def bootstrap(config_dir: Path, dry_run: bool = False) -> int:
    created: list[str] = []
    skipped: list[str] = []

    for d in DIRS:
        target = Path(d)
        if target.exists():
            skipped.append(str(target))
        elif dry_run:
            created.append(str(target))
        else:
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(target))

    config_dir.mkdir(parents=True, exist_ok=True)
    if not (config_dir / "loop-pilot.yaml").exists():
        if dry_run:
            created.append(str(config_dir / "loop-pilot.yaml"))
        else:
            (config_dir / "loop-pilot.yaml").write_text(
                yaml.dump(default_config_dict(), default_flow_style=False),
                encoding="utf-8",
            )
            created.append(str(config_dir / "loop-pilot.yaml"))
    else:
        skipped.append(str(config_dir / "loop-pilot.yaml"))

    print("# Bootstrap Report\n")
    if created:
        print("## Created\n")
        for item in created:
            print(f"- {item}")
    if skipped:
        print("\n## Skipped (already exists)\n")
        for item in skipped:
            print(f"- {item}")
    print(f"\nDry-run: {dry_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap LoopPilot local environment")
    parser.add_argument("--config-dir", default="config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return bootstrap(args.config_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
