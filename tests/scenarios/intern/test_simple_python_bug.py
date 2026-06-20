"""InternLoop scenario tests."""

from __future__ import annotations

from pathlib import Path
import sys

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

        assert record.outcome == RunOutcome.SUCCEEDED
        assert record.phase == RunPhase.TERMINATED
        assert len(rounds) == 2
        assert rounds[0].decision == "retryable_fail"
        assert rounds[1].decision == "pass"

        report = artifact_dir / "intern" / request.run_id / "development-report.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "schema_version" in content
        assert "run_id:" in content
        assert manifest.terminal_outcome == "succeeded"

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
        assert record.outcome == RunOutcome.SUCCEEDED

    def test_worker_cannot_self_approve(self, artifact_dir: Path) -> None:
        """Evaluation is independent — round 1 must not be pass before fix."""
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(run_id="test-intern-eval", loop_type="intern", fixture="simple_python_bug")
        record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
        _, _, rounds = loop.run(request, record)
        assert rounds[0].decision != "pass"

    def test_pytest_uses_current_python_executable(
        self, artifact_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        captured: dict[str, object] = {}

        def fake_run(command, **kwargs):  # noqa: ANN001
            captured["command"] = command

            class Result:
                returncode = 0
                stdout = "1 passed\n"
                stderr = ""

            return Result()

        monkeypatch.setattr("subprocess.run", fake_run)
        report = loop._run_pytest(Path("."), dry_run=False, fixture_dir=Path("."), round_num=2)

        assert "1 passed" in report
        assert captured["command"][0] == sys.executable

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
