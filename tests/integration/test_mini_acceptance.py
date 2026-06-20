"""Full Mini acceptance path from 25-mini-run-path.md."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


@pytest.mark.parametrize(
    "args",
    [
        ["doctor"],
        ["run", "intern", "--fixture", "simple_python_bug", "--dry-run"],
        ["run", "paper", "--fixture", "unsupported_claim", "--dry-run"],
        ["run", "daily-news", "--fixture", "github_star_snapshots", "--dry-run"],
        ["run", "all", "--fixture-set", "mini", "--dry-run"],
    ],
)
def test_mini_cli_commands(args: list[str]) -> None:
    runner = CliRunner()
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output


def test_bootstrap_scripts() -> None:
    root = Path(__file__).resolve().parents[2]
    for script, flag in [("bootstrap_local.py", "--dry-run"), ("seed_demo_data.py", "--dry-run")]:
        proc = subprocess.run(
            [sys.executable, str(root / "scripts" / script), flag],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
