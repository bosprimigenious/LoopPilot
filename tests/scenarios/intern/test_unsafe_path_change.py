"""Permission boundary — unsafe path blocked by Policy Gate."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


def test_unsafe_path_change_is_blocked(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="test-unsafe-001",
        loop_type="intern",
        fixture="unsafe_path_change",
    )
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    record, _, _ = loop.run(request, record)

    assert record.outcome == RunOutcome.BLOCKED
    assert "FORBIDDEN_PATH" in (record.terminal_reason or "")
