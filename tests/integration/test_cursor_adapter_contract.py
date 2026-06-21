"""CursorCLIAdapter contract tests with mock subprocess."""

from __future__ import annotations

import sys
from pathlib import Path

from loop_pilot.adapters.cursor_cli import CursorCLIAdapter
from loop_pilot.adapters.base import AdapterStatus
from loop_pilot.domain.errors import ErrorCode


def test_cursor_cli_dry_run_writes_transcript(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    artifacts = tmp_path / "artifacts"
    worktree.mkdir()
    adapter = CursorCLIAdapter(
        adapter_id="cursor_cli",
        command=[sys.executable, "-c", "raise SystemExit(99)"],
        approved_worktree=worktree,
        artifact_dir=artifacts,
    )

    result = adapter.execute({"dry_run": True, "cwd": str(worktree)})

    assert result.status == AdapterStatus.SUCCESS.value
    assert result.structured_output["dry_run"] is True
    assert result.transcript_artifact is not None


def test_cursor_cli_rejects_git_push(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    adapter = CursorCLIAdapter(
        adapter_id="cursor_cli",
        command=["git", "push", "origin", "main"],
        approved_worktree=worktree,
        artifact_dir=tmp_path / "artifacts",
    )

    result = adapter.execute({"cwd": str(worktree)})

    assert result.status == AdapterStatus.ERROR.value
    assert result.error_code == ErrorCode.POLICY_DENIED.value
