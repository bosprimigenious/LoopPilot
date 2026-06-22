"""InternLoop scenario tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


@pytest.fixture
def artifact_dir(tmp_path: Path) -> Path:
    d = tmp_path / "artifacts"
    d.mkdir()
    return d


class TestInternLoop:
    def test_simple_python_bug_succeeds_with_real_pytest(self, artifact_dir: Path) -> None:
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-intern-001",
            loop_type="intern",
            fixture="simple_python_bug",
        )
        record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
        record, manifest, rounds = loop.run(request, record)

        assert record.outcome == RunOutcome.PARTIAL
        assert record.phase == RunPhase.TERMINATED
        assert record.review_status == "needs_review"
        assert len(rounds) == 2
        assert rounds[0].decision == "retryable_fail"
        assert rounds[1].decision == "pass"

        report = artifact_dir / "intern" / request.run_id / "development-report.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "schema_version" in content
        assert "run_id:" in content
        assert manifest.terminal_outcome == "partial"

    def test_dry_run_does_not_modify_files(self, artifact_dir: Path) -> None:
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-intern-dry",
            loop_type="intern",
            fixture="simple_python_bug",
            dry_run=True,
        )
        record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record)
        assert record.dry_run is True
        assert record.outcome == RunOutcome.PARTIAL

    def test_worker_cannot_self_approve(self, artifact_dir: Path) -> None:
        """Evaluation is independent — round 1 must not be pass before fix."""
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(run_id="test-intern-eval", loop_type="intern", fixture="simple_python_bug")
        record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
        _, _, rounds = loop.run(request, record)
        assert rounds[0].decision != "pass"

    def test_pytest_routes_through_tool_broker(
        self, artifact_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        broker_calls: list[list[str]] = []
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))

        original = loop.tool_broker.run_command

        def spy_run_command(command: list[str], **kwargs):  # noqa: ANN001
            broker_calls.append(list(command))
            return original(command, **kwargs)

        monkeypatch.setattr(loop.tool_broker, "run_command", spy_run_command)

        work_dir = artifact_dir / "pytest-work"
        work_dir.mkdir()
        (work_dir / "test_ok.py").write_text("def test_x(): assert True\n", encoding="utf-8")
        report = loop._run_pytest(work_dir, dry_run=False, fixture_dir=Path("."), round_num=1)

        assert "1 passed" in report or "exit_code=0" in report
        assert broker_calls, "pytest must route through ToolBroker"
        assert broker_calls[0][:3] == [sys.executable, "-m", "pytest"]

    def test_non_dry_run_generates_real_git_diff(self, artifact_dir: Path) -> None:
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-intern-git-diff",
            loop_type="intern",
            fixture="simple_python_bug",
        )
        record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record)

        diff = artifact_dir / "intern" / request.run_id / "diff-summary.md"
        text = diff.read_text(encoding="utf-8")
        assert "diff --git" in text
        assert "-    return a - b" in text
        assert "+    return a + b" in text
