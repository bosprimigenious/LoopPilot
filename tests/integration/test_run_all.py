"""Integration tests for orchestrator and run-all."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.config import load_config
from loop_pilot.runtime.orchestrator import Orchestrator
from loop_pilot.storage.json_store import JsonStateStore


@pytest.fixture
def orchestrator(tmp_path: Path) -> Orchestrator:
    state_dir = tmp_path / "state"
    artifact_dir = tmp_path / "artifacts"
    config = load_config(Path("config"))
    config.runtime["state_dir"] = str(state_dir)
    config.runtime["artifact_dir"] = str(artifact_dir)
    store = JsonStateStore(state_dir)
    orch = Orchestrator(config, store)
    orch.artifact_dir = artifact_dir
    return orch


class TestRunAll:
    def test_run_all_isolates_loop_failures(self, orchestrator: Orchestrator, monkeypatch: pytest.MonkeyPatch) -> None:
        from loop_pilot.loops.intern import loop as intern_mod

        def failing_run(self, request, record):
            raise RuntimeError("injected intern failure")

        monkeypatch.setattr(intern_mod.InternLoop, "run", failing_run)

        results = orchestrator.run_all(fixture_set="mini", dry_run=True)
        assert len(results) == 3
        outcomes = {r.loop_type: r.outcome.value if r.outcome else None for r in results}
        assert outcomes["daily_news"] == "succeeded"
        assert outcomes["intern"] == "failed"
        assert outcomes["paper"] == "succeeded"

    def test_run_all_order(self, orchestrator: Orchestrator) -> None:
        results = orchestrator.run_all(fixture_set="mini", dry_run=True)
        assert [r.loop_type for r in results] == ["daily_news", "intern", "paper"]
