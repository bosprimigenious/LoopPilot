"""Canonical terminal artifact contract tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.terminal_artifacts import CANONICAL_ARTIFACTS, assert_terminal_artifacts, finalize_terminal_artifacts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def test_finalize_terminal_artifacts_writes_canonical_set(tmp_path: Path) -> None:
    run_dir = tmp_path / "intern" / "run-001"
    run_dir.mkdir(parents=True)
    (run_dir / "development-report.md").write_text("# Dev report\n", encoding="utf-8")
    (run_dir / "trace.jsonl").write_text('{"event":"state_transition"}\n', encoding="utf-8")

    record = RunRecord(
        run_id="run-001",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
        started_at="2026-06-21T00:00:00Z",
        finished_at="2026-06-21T00:05:00Z",
    )
    finalize_terminal_artifacts(run_dir, record, gate="pass")

    missing = assert_terminal_artifacts(run_dir)
    assert missing == []
    assert (run_dir / "report.md").exists()
    assert (run_dir / "loop_trace.jsonl").exists()
    for name in CANONICAL_ARTIFACTS:
        assert (run_dir / name).exists(), name


def test_manifest_does_not_include_self_checksum(tmp_path: Path) -> None:
    run_dir = tmp_path / "intern" / "run-stale-manifest"
    run_dir.mkdir(parents=True)
    (run_dir / "development-report.md").write_text("# Dev report\n", encoding="utf-8")

    record = RunRecord(
        run_id="run-stale-manifest",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
        started_at="2026-06-21T00:00:00Z",
        finished_at="2026-06-21T00:05:00Z",
    )
    finalize_terminal_artifacts(run_dir, record, gate="pass")
    manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["artifacts"]}
    assert "artifact-manifest.json" not in manifest_paths

    (run_dir / "development-report.md").write_text("# Updated dev report\n", encoding="utf-8")
    finalize_terminal_artifacts(run_dir, record, gate="pass")
    manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["artifacts"]}
    assert "artifact-manifest.json" not in manifest_paths
    assert (run_dir / "artifact-manifest.json").exists()
    missing = assert_terminal_artifacts(run_dir)
    assert missing == []


def test_intern_patch_run_does_not_overwrite_canonical_manifest(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    loop = InternLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
    request = RunRequest(
        run_id="test-intern-manifest",
        loop_type="intern",
        fixture="simple_python_bug",
    )
    record = RunRecord(run_id=request.run_id, loop_type="intern", phase=RunPhase.CREATED)
    record, _, _ = loop.run(request, record)

    run_dir = artifact_dir / "intern" / request.run_id
    manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    gate = json.loads((run_dir / "gate_result.json").read_text(encoding="utf-8"))

    assert gate["gate"] == "needs_review"
    assert manifest["terminal_outcome"] == "partial"
    assert record.phase == RunPhase.TERMINATED
    assert record.review_status == "needs_review"
    assert "artifact-manifest.json" not in {item["path"] for item in manifest["artifacts"]}
    manifest_paths = {item["path"] for item in manifest["artifacts"]}
    assert "patch.diff" in manifest_paths
    assert "report.md" in manifest_paths
    report_entry = next(item for item in manifest["artifacts"] if item["path"] == "report.md")
    assert report_entry["sha256"] == _sha256(run_dir / "report.md")
