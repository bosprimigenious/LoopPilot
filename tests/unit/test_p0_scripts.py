"""P0 maintenance script behavior."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_install_scheduler_defaults_to_dry_run() -> None:
    proc = _run_script("install_scheduler.py")

    assert proc.returncode == 0, proc.stderr
    assert "Dry-run: True" in proc.stdout
    assert "does not install" in proc.stdout


def test_run_regression_dry_run_lists_fixed_commands() -> None:
    proc = _run_script("run_regression.py", "--dry-run")

    assert proc.returncode == 0, proc.stderr
    assert "python -m pytest -q" in proc.stdout
    assert "loop-pilot run all --fixture-set mini --dry-run" in proc.stdout


def test_backup_state_dry_run_previews_state_config_and_checkpoints(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    state_dir = tmp_path / "state"
    checkpoint_dir = tmp_path / "checkpoints"
    config_dir.mkdir()
    state_dir.mkdir()
    checkpoint_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text("runtime: {}\n", encoding="utf-8")
    (state_dir / "run.json").write_text("{}", encoding="utf-8")
    (checkpoint_dir / "open.json").write_text(json.dumps({"closed": False}), encoding="utf-8")

    proc = _run_script(
        "backup_state.py",
        "--config-dir",
        str(config_dir),
        "--state-dir",
        str(state_dir),
        "--checkpoint-dir",
        str(checkpoint_dir),
        "--backup-dir",
        str(tmp_path / "backups"),
        "--dry-run",
    )

    assert proc.returncode == 0, proc.stderr
    assert "Would back up" in proc.stdout
    assert "open.json" in proc.stdout
    assert not (tmp_path / "backups").exists()


def test_migrate_state_dry_run_prints_plan_without_creating_db(tmp_path: Path) -> None:
    db_path = tmp_path / "state" / "loop-pilot.sqlite3"

    proc = _run_script("migrate_state.py", "--db-path", str(db_path), "--dry-run")

    assert proc.returncode == 0, proc.stderr
    assert "Current schema version" in proc.stdout
    assert "Target schema version" in proc.stdout
    assert not db_path.exists()
