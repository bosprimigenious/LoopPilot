"""Shared test helpers."""

from __future__ import annotations

from pathlib import Path


def sqlite_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                f"  state_dir: {tmp_path / 'state'}",
                f"  artifact_dir: {tmp_path / 'artifacts'}",
                f"  sqlite_path: {tmp_path / 'state' / 'loop_pilot.db'}",
                f"  lock_dir: {tmp_path / 'locks'}",
                "  timezone: UTC",
            ]
        ),
        encoding="utf-8",
    )
    for name in (
        "intern.yaml",
        "paper.yaml",
        "daily_news.yaml",
        "policies.yaml",
        "sources.yaml",
        "models.yaml",
    ):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    return config_dir
