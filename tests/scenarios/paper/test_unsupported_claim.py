"""PaperLoop scenario tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
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

    def test_missing_fixture_blocks_without_success(self, artifact_dir: Path) -> None:
        loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(run_id="test-paper-missing", loop_type="paper", fixture="missing_fixture")
        record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)

        record, _, _ = loop.run(request, record)

        assert record.outcome in {RunOutcome.BLOCKED, RunOutcome.FAILED}
        assert record.outcome != RunOutcome.SUCCEEDED
        assert "fixture" in (record.terminal_reason or "").lower()

    def test_bibtex_without_support_does_not_invent_smith2024(
        self, artifact_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fixture_root = tmp_path / "paper"
        fixture = fixture_root / "weak_bib"
        (fixture / "input").mkdir(parents=True)
        (fixture / "mock_responses").mkdir()
        (fixture / "README.md").write_text("weak bib fixture", encoding="utf-8")
        (fixture / "mock_responses" / "default.json").write_text(
            '{"status": "success", "structured_output": {}}',
            encoding="utf-8",
        )
        (fixture / "input" / "paper.md").write_text(
            "# Paper\n\nOur method significantly outperforms all baselines on every benchmark.\n",
            encoding="utf-8",
        )
        (fixture / "input" / "references.bib").write_text(
            "@article{Doe2026, title={A Dataset Catalog}, author={Doe, Jane}, year={2026}}\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(PaperLoop, "FIXTURE_ROOT", fixture_root)

        loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(run_id="test-paper-weak-bib", loop_type="paper", fixture="weak_bib")
        record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record)

        revised = artifact_dir / "paper" / request.run_id / "paper-revised.md"
        text = revised.read_text(encoding="utf-8")
        assert "Smith2024" not in text
        assert "SOURCE REQUIRED" in text
        assert record.outcome in {RunOutcome.PARTIAL, RunOutcome.BLOCKED}
        assert record.outcome != RunOutcome.SUCCEEDED

    def test_unsupported_claim_outcome_is_partial_not_succeeded(self, artifact_dir: Path) -> None:
        loop = PaperLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-paper-outcome",
            loop_type="paper",
            fixture="unsupported_claim",
        )
        record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record)

        assert record.outcome == RunOutcome.PARTIAL
        report = artifact_dir / "paper" / request.run_id / "paper-development-report.md"
        content = report.read_text(encoding="utf-8")
        assert "## Source Required" in content
        assert "\nyes\n" in content or content.strip().endswith("yes")
