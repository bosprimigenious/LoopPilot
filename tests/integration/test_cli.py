"""CLI integration tests — run from project root."""

from __future__ import annotations

from click.testing import CliRunner

from loop_pilot.cli import app


class TestCLI:
    def test_doctor_passes(self) -> None:
        runner = CliRunner()
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0, result.output
        assert "Doctor: OK" in result.output

    def test_run_intern_dry_run(self) -> None:
        runner = CliRunner()
        result = runner.invoke(app, ["run", "intern", "--fixture", "simple_python_bug", "--dry-run"])
        assert result.exit_code == 0, result.output
        assert "completed: succeeded" in result.output

    def test_run_all_dry_run(self) -> None:
        runner = CliRunner()
        result = runner.invoke(app, ["run", "all", "--fixture-set", "mini", "--dry-run"])
        assert result.exit_code == 0, result.output
        assert "daily_news: succeeded" in result.output
