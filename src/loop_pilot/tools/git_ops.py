"""Git operations with policy enforcement."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.tools.command import CommandResult, run_command


def diff_summary(worktree: Path, *, timeout: float = 30.0) -> CommandResult:
    return run_command(["git", "diff", "--stat"], cwd=worktree, timeout=timeout)


def status(worktree: Path, *, timeout: float = 10.0) -> CommandResult:
    return run_command(["git", "status", "--short"], cwd=worktree, timeout=timeout)
