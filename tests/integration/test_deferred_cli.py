"""Verify V1 CLI exposes recovery and review commands."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app

V1_COMMANDS = ("resume", "approve", "reject", "cancel", "report")


def test_v1_exposes_recovery_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in V1_COMMANDS:
        assert cmd in result.output


def test_help_lists_core_surface() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("doctor", "run", "status", "inspect"):
        assert cmd in result.output
