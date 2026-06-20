"""Step 6 — interrupted action produces explainable failure."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.intern import loop as intern_mod
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.trace import read_trace


def test_interrupted_action_fails_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()

    def explode(self, work_dir):  # noqa: ANN001
        raise InterruptedError("simulated ACTING interruption")

    monkeypatch.setattr(intern_mod.InternLoop, "_apply_fix", explode)

    loop = intern_mod.InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(run_id="interrupt-001", loop_type="intern", fixture="simple_python_bug")
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    record, _, _ = loop.run(request, record)

    assert record.outcome == RunOutcome.FAILED
    assert "interrupted" in (record.terminal_reason or "").lower()
    trace = read_trace(artifact_dir / "intern" / request.run_id / "trace.jsonl")
    assert any(e.get("event") == "interrupted" for e in trace)
