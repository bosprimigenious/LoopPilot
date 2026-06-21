"""Canonical terminal artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.terminal_artifacts import CANONICAL_ARTIFACTS, assert_terminal_artifacts, finalize_terminal_artifacts


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


def test_manifest_does_not_include_stale_self_checksum(tmp_path: Path) -> None:
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
