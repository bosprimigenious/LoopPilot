#!/usr/bin/env python3
"""Run the fixed Mini/V1 regression command set."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


COMMANDS: list[list[str]] = [
    [sys.executable, "-m", "pytest", "-q"],
    [sys.executable, "-m", "pytest", "-q", "tests/integration/test_mini_acceptance.py"],
    [sys.executable, "-m", "pytest", "-q", "tests/integration/test_v1_cli.py"],
    [sys.executable, "-m", "loop_pilot.cli", "run", "all", "--fixture-set", "mini", "--dry-run"],
]


def _display(command: list[str]) -> str:
    shown = ["python" if part == sys.executable else part for part in command]
    if shown[:3] == ["python", "-m", "loop_pilot.cli"]:
        shown = ["loop-pilot", *shown[3:]]
    return " ".join(shown)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run LoopPilot fixed regression commands")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    args = parser.parse_args()

    print("# Regression Commands\n")
    for command in COMMANDS:
        print(f"- {_display(command)}")

    if args.dry_run:
        print("\nDry-run: True")
        return 0

    for command in COMMANDS:
        print(f"\n$ {_display(command)}")
        proc = subprocess.run(command, cwd=args.cwd, check=False)
        if proc.returncode != 0:
            return proc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
