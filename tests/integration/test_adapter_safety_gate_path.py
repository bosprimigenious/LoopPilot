"""Integration: SafetyGate blocks real adapter path even when allow_real_adapters=true."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from loop_pilot.cli import app


def _config(tmp_path: Path, *, max_level: int = 2) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "workspaces:\n"
        "  intern_demo:\n"
        "    root: examples/intern_demo\n"
        "    allowed_paths: [src/**, tests/**]\n"
        "    forbidden_paths: [.env*, secrets/**]\n"
        "    allow_write: false\n"
        "runtime:\n"
        "  state_backend: json\n"
        "  state_dir: var/state\n"
        "  artifact_dir: var/artifacts\n"
        "  allow_real_adapters: true\n"
        f"safety:\n  stage: ready\n  max_level: {max_level}\n",
        encoding="utf-8",
    )
    (config_dir / "models.yaml").write_text(
        "adapters:\n"
        "  mock:\n    kind: mock\n"
        "  cursor_cli:\n"
        "    kind: cursor_cli\n"
        "    command: [echo, hi]\n"
        "    capabilities:\n"
        "      supports_file_write: true\n"
        "      supports_tools: true\n"
        "      supports_dry_run: true\n"
        "roles:\n"
        "  coding_agent:\n    adapter: mock\n",
        encoding="utf-8",
    )
    return config_dir


def test_real_adapter_blocked_by_safety_gate_when_max_level_low(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "--config-dir",
            str(_config(tmp_path, max_level=2)),
            "run",
            "intern",
            "--workspace",
            "examples/intern_demo",
            "--adapter",
            "cursor_cli",
            "--allow-real-adapters",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "LEVEL_EXCEEDS_MAX" in result.output or "safety gate" in result.output.lower()
