"""Integration tests — controlled live run evidence structure (mock / MANUAL)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from loop_pilot.cli import app
from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


REPO_ROOT = Path(__file__).resolve().parents[2]
MANUAL_LOG = REPO_ROOT / "docs" / "development" / "logs" / "2026-06-21-0.3-live-adapter-manual-check.md"


def test_controlled_mock_intern_run_produces_tool_results_evidence(tmp_path: Path) -> None:
    """Mock adapter + real pytest path documents broker audit for MANUAL log cross-check."""
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="controlled-mock-intern",
        loop_type="intern",
        fixture="simple_python_bug",
    )
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    record, manifest, rounds = loop.run(request, record)

    run_dir = artifact_dir / "intern" / request.run_id
    tool_results = json.loads((run_dir / "tool-results.json").read_text(encoding="utf-8"))
    trace_path = run_dir / "trace.jsonl"

    assert record.outcome is not None
    assert len(rounds) >= 1
    assert tool_results.get("audit")
    assert trace_path.is_file()
    assert manifest.terminal_outcome == record.outcome.value
    assert (run_dir / "development-report.md").is_file()


def test_dry_run_cli_runs_produce_candidate_artifacts_for_manual_log() -> None:
    """Controlled mock CLI runs match MANUAL log structure (no credentials required)."""
    runner = CliRunner()
    cases = [
        (["run", "intern", "--fixture", "simple_python_bug", "--dry-run"], "succeeded"),
        (["run", "paper", "--fixture", "unsupported_claim", "--dry-run"], "partial"),
        (["run", "daily-news", "--source-profile", "demo", "--dry-run"], "succeeded"),
    ]
    for args, expected in cases:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert f"completed: {expected}" in result.output


def test_manual_log_template_exists_with_controlled_run_section() -> None:
    assert MANUAL_LOG.is_file(), "MANUAL log template must exist for 0.3.0b1"
    text = MANUAL_LOG.read_text(encoding="utf-8")
    assert "DeepSeek" in text
    assert "Cursor CLI" in text
    assert "controlled" in text.lower() or "Controlled" in text
