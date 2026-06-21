"""Integration tests for orchestrator and run-all."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.config import load_config
from loop_pilot.domain.models import RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
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
        assert outcomes["paper"] == "partial"

    def test_run_all_order(self, orchestrator: Orchestrator) -> None:
        results = orchestrator.run_all(fixture_set="mini", dry_run=True)
        assert [r.loop_type for r in results] == ["daily_news", "intern", "paper"]

    def test_startup_failure_is_persisted_for_status_and_inspect(
        self, orchestrator: Orchestrator, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fail_before_loop(loop_type: str, *, router=None):  # noqa: ARG001, ANN001
            raise RuntimeError("startup adapter failure")

        monkeypatch.setattr(orchestrator, "_get_loop", fail_before_loop)
        request = RunRequest(
            run_id=orchestrator.new_run_id("intern"),
            loop_type="intern",
            fixture="simple_python_bug",
        )

        record = orchestrator.run_loop(request)
        stored = orchestrator.state_store.get_run(request.run_id)

        assert record.outcome == RunOutcome.FAILED
        assert record.phase == RunPhase.TERMINATED
        assert stored is not None
        assert stored.outcome == RunOutcome.FAILED
        assert "startup adapter failure" in (stored.terminal_reason or "")
        assert "LOCKING" in (stored.terminal_reason or "")
