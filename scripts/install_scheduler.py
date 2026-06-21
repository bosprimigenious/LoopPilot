#!/usr/bin/env python3
"""Generate local OS scheduler configuration without installing it."""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path


def _scheduler_config(command: str, cwd: Path) -> str:
    if platform.system().lower().startswith("win"):
        return "\n".join(
            [
                "# Windows Task Scheduler preview",
                "$Action = New-ScheduledTaskAction \\",
                f"  -Execute 'powershell.exe' -Argument '-NoProfile -Command \"cd {cwd}; {command}\"'",
                "$Trigger = New-ScheduledTaskTrigger -Daily -At 09:00",
                "Register-ScheduledTask -TaskName 'LoopPilotDaily' -Action $Action -Trigger $Trigger",
            ]
        )
    return "\n".join(
        [
            "# cron preview",
            f"0 9 * * * cd {cwd} && {command}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Print or generate LoopPilot scheduler config")
    parser.add_argument("--command", default="loop-pilot run all --fixture-set mini --dry-run")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true", help="Generate output file instead of preview only")
    parser.add_argument("--yes", action="store_true", help="Explicit confirmation for non dry-run generation")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    dry_run = not (args.apply and args.yes)
    config = _scheduler_config(args.command, args.cwd.resolve())

    print("# Scheduler Configuration\n")
    print(config)
    print("\nThis script does not install or register scheduler entries.")
    print(f"Dry-run: {dry_run}")

    if not dry_run and args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(config + "\n", encoding="utf-8")
        print(f"Generated: {args.output}")
    elif args.apply and not args.yes:
        print("Refusing non dry-run generation without --yes.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
