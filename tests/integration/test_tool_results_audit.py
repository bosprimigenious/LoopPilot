"""Integration tests — tool-results.json aligns with ToolBroker audit fields."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.loops.paper.loop import PaperLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


REQUIRED_AUDIT_KEYS = {"event", "tool", "status", "duration_ms", "policy"}


@pytest.fixture
def artifact_dir(tmp_path: Path) -> Path:
    d = tmp_path / "artifacts"
    d.mkdir()
    return d


def _load_tool_results(run_dir: Path) -> dict:
    path = run_dir / "tool-results.json"
    assert path.is_file(), f"missing tool-results.json in {run_dir}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_intern_tool_results_include_broker_audit(artifact_dir: Path) -> None:
    loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="audit-intern-001",
        loop_type="intern",
        fixture="simple_python_bug",
    )
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    loop.run(request, record)

    payload = _load_tool_results(artifact_dir / "intern" / request.run_id)
    assert "audit" in payload
    assert isinstance(payload["audit"], list)
    assert payload["audit"], "Intern run must record broker audit entries"
    command_entries = [entry for entry in payload["audit"] if entry.get("tool") == "command"]
    assert command_entries, "pytest must appear as command audit"
    assert REQUIRED_AUDIT_KEYS.issubset(command_entries[0].keys())
    assert command_entries[0]["event"] == "tool_call"


def test_paper_tool_results_include_broker_audit(artifact_dir: Path) -> None:
    loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="audit-paper-001",
        loop_type="paper",
        fixture="unsupported_claim",
        dry_run=True,
    )
    record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
    loop.run(request, record)

    payload = _load_tool_results(artifact_dir / "paper" / request.run_id)
    assert payload.get("dry_run") is True
    assert payload.get("audit"), "Paper run must include broker audit trail"
    file_reads = [entry for entry in payload["audit"] if entry.get("tool") == "file_read"]
    assert file_reads
    assert REQUIRED_AUDIT_KEYS.issubset(file_reads[0].keys())


def test_daily_news_tool_results_include_broker_audit(artifact_dir: Path) -> None:
    loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="audit-daily-001",
        loop_type="daily_news",
        fixture="github_star_snapshots",
        dry_run=True,
    )
    record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
    loop.run(request, record)

    payload = _load_tool_results(artifact_dir / "daily-news" / request.run_id)
    assert payload.get("dry_run") is True
    assert isinstance(payload.get("audit"), list)
