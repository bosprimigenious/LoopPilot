"""PaperLoop scenario tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.paper.loop import PaperLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


@pytest.fixture
def artifact_dir(tmp_path: Path) -> Path:
    d = tmp_path / "artifacts"
    d.mkdir()
    return d


class TestPaperLoop:
    def test_unsupported_claim_revised_without_fake_citation(self, artifact_dir: Path) -> None:
        loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-paper-001",
            loop_type="paper",
            fixture="unsupported_claim",
        )
        record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
        record, manifest, _ = loop.run(request, record)

        report = artifact_dir / "paper" / request.run_id / "paper-development-report.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "schema_version" in content
        assert "fake" not in content.lower()

        revised = artifact_dir / "paper" / request.run_id / "paper-revised.md"
        if revised.exists():
            text = revised.read_text(encoding="utf-8")
            assert "FakeAuthor" not in text
            assert "significantly outperforms all baselines" not in text or "Smith2024" in text

        evidence = artifact_dir / "paper" / request.run_id / "evidence-map.json"
        assert evidence.exists()

    def test_dry_run_paper(self, artifact_dir: Path) -> None:
        loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-paper-dry",
            loop_type="paper",
            fixture="unsupported_claim",
            dry_run=True,
        )
        record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record)
        assert record.report_status == "generated"
