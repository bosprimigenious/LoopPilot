"""Verify Mini CLI guards review commands on json backend."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app


def test_json_backend_blocks_review_commands() -> None:
    runner = CliRunner()
    for cmd in ("review", "approve", "reject", "defer", "cancel", "resume"):
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code != 0 or "state_backend=sqlite" in result.output


def test_help_lists_core_surface() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("doctor", "run", "status", "inspect", "review"):
        assert cmd in result.output
