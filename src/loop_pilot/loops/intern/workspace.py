"""Git workspace helpers for InternLoop Mini."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class GitWorkspaceError(Exception):
    pass


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def prepare_git_worktree(fixture_input: Path, dry_run: bool) -> tuple[Path, Path | None]:
    """Create a real git repo from fixture input. Returns (work_dir, temp_root_for_cleanup)."""
    if dry_run:
        return fixture_input, None

    if not fixture_input.exists():
        raise GitWorkspaceError(f"Fixture input missing: {fixture_input}")

    temp_root = Path(tempfile.mkdtemp(prefix="loop-pilot-intern-"))
    repo_dir = temp_root / "repo"
    shutil.copytree(fixture_input, repo_dir, dirs_exist_ok=True)

    init = _run_git(["init"], repo_dir)
    if init.returncode != 0:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise GitWorkspaceError(f"git init failed: {init.stderr}")

    _run_git(["config", "user.email", "loop-pilot@example.com"], repo_dir)
    _run_git(["config", "user.name", "LoopPilot Mini"], repo_dir)
    add = _run_git(["add", "."], repo_dir)
    if add.returncode != 0:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise GitWorkspaceError(f"git add failed: {add.stderr}")

    commit = _run_git(["commit", "-m", "baseline"], repo_dir)
    if commit.returncode != 0:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise GitWorkspaceError(f"git commit failed: {commit.stderr}")

    return repo_dir, temp_root


def git_diff_summary(work_dir: Path) -> str:
    result = _run_git(["diff", "HEAD"], work_dir)
    if result.returncode != 0:
        return f"git diff failed: {result.stderr}"
    if not result.stdout.strip():
        return "No changes"
    return result.stdout


def cleanup_workspace(temp_root: Path | None) -> None:
    if temp_root and temp_root.exists():
        shutil.rmtree(temp_root, ignore_errors=True)
