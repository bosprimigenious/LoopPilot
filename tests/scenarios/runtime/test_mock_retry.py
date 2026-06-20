"""Step 2 — runtime mock retry scenario."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.trace import read_trace


def test_mock_loop_retryable_fail_then_pass(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(run_id="mock-retry-001", loop_type="intern", fixture="simple_python_bug")
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    record, _, rounds = loop.run(request, record)

    assert len(rounds) == 2
    assert rounds[0].decision == "retryable_fail"
    assert rounds[1].decision == "pass"

    trace_path = artifact_dir / "intern" / request.run_id / "trace.jsonl"
    events = read_trace(trace_path)
    phases = [e["phase"] for e in events if e.get("event") == "state_transition"]
    assert "DIAGNOSING" in phases
    assert "REFLECTING" in phases
    assert "REPLANNING" in phases
