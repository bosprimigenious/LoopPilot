"""Verify Mini CLI surface excludes deferred V1 commands."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app

MINI_DEFERRED_COMMANDS = ("resume", "approve", "reject", "cancel", "report")


def test_mini_does_not_expose_deferred_v1_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in MINI_DEFERRED_COMMANDS:
        assert f"  {cmd}" not in result.output


def test_help_lists_mini_surface() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("doctor", "run", "status", "inspect"):
        assert cmd in result.output
