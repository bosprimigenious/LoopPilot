"""DailyNews candidate-actions to inbox integration tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.app import App
from loop_pilot.cli import app
from loop_pilot.domain.models import RunRequest
from loop_pilot.tasks.store import TaskStore


def _models_yaml(config_dir: Path) -> None:
    (config_dir / "models.yaml").write_text(
        "\n".join(
            [
                "model_roles:",
                "  coding_agent:",
                "    candidates: [mock]",
                "  analysis_medium:",
                "    candidates: [mock]",
                "  screening_economical:",
                "    candidates: [mock]",
                "adapters:",
                "  mock:",
                "    kind: mock",
                "    capabilities:",
                "      supports_structured_output: true",
                "      supports_dry_run: true",
                "      supports_file_write: true",
                "      supports_tools: true",
            ]
        ),
        encoding="utf-8",
    )


def test_daily_news_run_then_import_inbox(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sqlite_config_dir: Path,
) -> None:
    config_dir = sqlite_config_dir
    _models_yaml(config_dir)

    sources = tmp_path / "config" / "sources.yaml"
    repo_root = Path(__file__).resolve().parents[2]
    demo_items = repo_root / "examples" / "daily_news_demo" / "items.json"
    if demo_items.exists():
        sources.write_text(
            f"sources:\n  demo:\n    kind: local_json\n    path: {demo_items.as_posix()}\n",
            encoding="utf-8",
        )

    monkeypatch.chdir(tmp_path)
    application = App.from_config_dir(config_dir)
    request = RunRequest(
        run_id="import-test-001",
        loop_type="daily_news",
        source_profile="demo" if demo_items.exists() else None,
        fixture=None if demo_items.exists() else "github_star_snapshots",
        dry_run=True,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    if request.fixture is None and request.source_profile is None:
        pytest.skip("demo source and fixture unavailable")

    record = application.orchestrator.run_loop(request)
    assert record.outcome is not None

    actions_path = tmp_path / "artifacts" / "daily-news" / record.run_id / "candidate-actions.json"
    if not actions_path.exists():
        actions_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path = repo_root / "tests" / "fixtures" / "tasks" / "candidate-actions.json"
        shutil.copy(fixture_path, actions_path)

    runner = CliRunner()
    dry_result = runner.invoke(
        app,
        [
            "--config-dir",
            str(config_dir),
            "inbox",
            "import-daily-news",
            "--from",
            str(actions_path),
            "--dry-run",
        ],
    )
    assert dry_result.exit_code == 0, dry_result.output
    assert "Would import" in dry_result.output

    import_result = runner.invoke(
        app,
        [
            "--config-dir",
            str(config_dir),
            "inbox",
            "import-daily-news",
            "--from",
            str(actions_path),
        ],
    )
    assert import_result.exit_code == 0, import_result.output

    store = TaskStore(config_dir.parent / "state" / "loop_pilot.db")
    inbox_rows = store.list_inbox_items(status="all")
    assert len(inbox_rows) >= 1

    repeat_result = runner.invoke(
        app,
        [
            "--config-dir",
            str(config_dir),
            "inbox",
            "import-daily-news",
            "--from",
            str(actions_path),
        ],
    )
    assert repeat_result.exit_code == 0, repeat_result.output
    assert "Skipped duplicates" in repeat_result.output
    assert len(store.list_inbox_items(status="all")) == len(inbox_rows)
