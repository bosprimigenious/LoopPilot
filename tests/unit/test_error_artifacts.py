"""Orchestrator failure artifact tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from loop_pilot.config import LoopPilotConfig
from loop_pilot.domain.models import RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.orchestrator import Orchestrator
from loop_pilot.storage.json_store import JsonStateStore


@pytest.fixture
def orchestrator(tmp_path: Path) -> Orchestrator:
    state_dir = tmp_path / "state"
    artifact_dir = tmp_path / "artifacts"
    state_dir.mkdir()
    artifact_dir.mkdir()
    config = LoopPilotConfig(
        runtime={
            "state_dir": str(state_dir),
            "artifact_dir": str(artifact_dir),
            "state_backend": "json",
            "allow_real_adapters": False,
        }
    )
    return Orchestrator(config, JsonStateStore(state_dir))


def test_run_failure_writes_error_traceback_and_trace_event(orchestrator: Orchestrator, tmp_path: Path) -> None:
    request = RunRequest(
        run_id="fail-intern-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=True,
        config_snapshot_hash="test",
    )
    record = orchestrator.create_run_record(request)
    record.phase = RunPhase.LOCKING
    orchestrator.state_store.save_run(record)

    with patch.object(orchestrator, "_get_loop", side_effect=RuntimeError("token=super-secret")):
        result = orchestrator.run_loop(request, record=record)

    assert result.outcome == RunOutcome.FAILED
    assert "super-secret" not in (result.terminal_reason or "")

    run_dir = tmp_path / "artifacts" / "intern" / request.run_id
    tb_path = run_dir / "error-traceback.txt"
    assert tb_path.exists()
    tb_content = tb_path.read_text(encoding="utf-8")
    assert "RuntimeError" in tb_content
    assert "super-secret" not in tb_content

    trace_events = [json.loads(line) for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
    error_events = [event for event in trace_events if event.get("event") == "error"]
    assert error_events
    assert error_events[-1]["error_type"] == "RuntimeError"
    assert error_events[-1]["phase"] == RunPhase.LOCKING.value
