"""Verify V1 commands are not registered in Mini CLI."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app

DEFERRED_COMMANDS = ("resume", "approve", "reject", "cancel")


def test_deferred_commands_not_registered() -> None:
    runner = CliRunner()
    for cmd in DEFERRED_COMMANDS:
        result = runner.invoke(app, [cmd])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Error" in result.output


def test_help_lists_only_mini_surface() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("doctor", "run", "status", "inspect"):
        assert cmd in result.output
    for cmd in DEFERRED_COMMANDS:
        assert cmd not in result.output
