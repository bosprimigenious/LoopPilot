"""Integration: real adapters blocked by default."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app


def test_intern_real_adapter_blocked_by_default() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "intern",
            "--workspace",
            "examples/intern_demo",
            "--adapter",
            "cursor_cli",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "allow_real_adapters=false" in result.output.lower()


def test_paper_deepseek_blocked_missing_key_with_opt_in() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "paper",
            "--workspace",
            "examples/paper_demo",
            "--adapter",
            "deepseek",
            "--allow-real-adapters",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "missing api key" in result.output.lower()
    assert "Traceback" not in result.output
