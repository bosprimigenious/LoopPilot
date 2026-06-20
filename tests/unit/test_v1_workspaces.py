"""V1 workspace safety tests for Intern and Paper loops."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.loops.intern.workspace import create_approved_worktree, ensure_clean_git_workspace
from loop_pilot.loops.paper.workspace import create_paper_working_copy
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


def _git(args: list[str], cwd: Path) -> None:
    import subprocess

    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_intern_rejects_dirty_user_workspace(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init"], repo)
    (repo / "tracked.py").write_text("value = 1\n", encoding="utf-8")
    _git(["add", "."], repo)
    _git(["-c", "user.name=LoopPilot", "-c", "user.email=loop@example.com", "commit", "-m", "base"], repo)
    (repo / "tracked.py").write_text("value = 2\n", encoding="utf-8")

    with pytest.raises(LoopPilotError) as exc:
        ensure_clean_git_workspace(repo)

    assert exc.value.code == ErrorCode.WORKSPACE_CHANGED


def test_intern_creates_real_worktree_from_clean_configured_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init"], repo)
    (repo / "tracked.py").write_text("value = 1\n", encoding="utf-8")
    _git(["add", "."], repo)
    _git(["-c", "user.name=LoopPilot", "-c", "user.email=loop@example.com", "commit", "-m", "base"], repo)

    worktree = create_approved_worktree(
        repo,
        tmp_path / "worktrees",
        branch="HEAD",
        worktree_name="run-001",
    )

    assert (worktree / ".git").exists() or (worktree / ".git").is_file()
    assert (worktree / "tracked.py").read_text(encoding="utf-8") == "value = 1\n"
    assert worktree.parent == tmp_path / "worktrees"


def test_paper_working_copy_excludes_read_only_paths(tmp_path: Path) -> None:
    workspace = tmp_path / "paper"
    workspace.mkdir()
    (workspace / "paper.md").write_text("# Draft\n\nClaim.\n", encoding="utf-8")
    (workspace / "references.bib").write_text("@article{Safe2026,title={Safe}}\n", encoding="utf-8")
    raw = workspace / "experiments" / "raw"
    raw.mkdir(parents=True)
    (raw / "private-results.csv").write_text("secret,data\n", encoding="utf-8")

    copy = create_paper_working_copy(
        workspace,
        tmp_path / "copies",
        read_only_patterns=["experiments/raw/**"],
    )

    assert (copy / "paper.md").exists()
    assert (copy / "references.bib").exists()
    assert not (copy / "experiments" / "raw" / "private-results.csv").exists()


def test_daily_news_loads_local_source_set_and_routes_high_confidence_inbox(tmp_path: Path) -> None:
    source_set = tmp_path / "sources"
    source_set.mkdir()
    (source_set / "items.json").write_text(
        """
        {
          "items": [
            {
              "source_item_id": "local-1",
              "url": "https://example.invalid/repo",
              "title": "Local repo update",
              "confidence": "high",
              "category": "github",
              "stars": 12
            },
            {
              "source_item_id": "local-2",
              "url": "https://example.invalid/low",
              "title": "Low confidence",
              "confidence": "low",
              "category": "github",
              "stars": 99
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    loop = DailyNewsLoop(tmp_path / "artifacts", PolicyEngine(), ReportRenderer(Path("templates")))

    items = loop.load_local_source_set(source_set, min_confidence="medium")
    inbox = loop.route_inbox(items)

    assert [item["source_item_id"] for item in items] == ["local-1"]
    assert "Local repo update" in inbox
    assert "Low confidence" not in inbox
