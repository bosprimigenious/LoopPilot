"""Integration tests for Practical MVP 0.2 workspace mode."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


@pytest.mark.parametrize(
    "args,expected_outcome",
    [
        (["run", "intern", "--workspace", "examples/intern_demo", "--dry-run"], "partial"),
        (["run", "paper", "--workspace", "examples/paper_demo", "--dry-run"], "partial"),
        (["run", "daily-news", "--source-profile", "demo", "--dry-run"], "succeeded"),
        (["run", "all", "--profile", "demo", "--dry-run"], "succeeded"),
    ],
)
def test_practical_mvp_cli_commands(args: list[str], expected_outcome: str) -> None:
    runner = CliRunner()
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    if args[1] == "all":
        assert "daily_news: succeeded" in result.output
        assert "intern: partial" in result.output
        assert "paper: partial" in result.output
    else:
        assert f"completed: {expected_outcome}" in result.output


def test_workspace_and_fixture_mutually_exclusive() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "intern", "--fixture", "simple_python_bug", "--workspace", "intern_demo", "--dry-run"],
    )
    assert result.exit_code != 0
    assert "not both" in result.output.lower()


def test_review_outputs_created_for_intern_workspace(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loop_pilot.config import load_config
    from loop_pilot.domain.models import RunRequest
    from loop_pilot.runtime.orchestrator import Orchestrator
    from loop_pilot.storage.json_store import JsonStateStore

    artifact_dir = tmp_path / "artifacts"
    config = load_config()
    config.runtime["artifact_dir"] = str(artifact_dir)
    config.runtime["state_dir"] = str(tmp_path / "state")
    orch = Orchestrator(config, JsonStateStore(tmp_path / "state"))
    orch.artifact_dir = artifact_dir

    request = RunRequest(
        run_id=orch.new_run_id("intern"),
        loop_type="intern",
        workspace="intern_demo",
        dry_run=True,
        config_snapshot_hash=config.snapshot_hash(),
    )
    record = orch.run_loop(request)
    run_dir = artifact_dir / "intern" / record.run_id
    assert (run_dir / "review-required.md").exists()
    assert (run_dir / "next-actions.md").exists()
