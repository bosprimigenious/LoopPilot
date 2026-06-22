"""Review gate tests for patch.diff runs (0.4 truthful acceptance)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from loop_pilot.app import App
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.schema_validation import validate_artifact_manifest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.review.service import ReviewService
from loop_pilot.runtime.orchestrator import ResumeError
from loop_pilot.summary.collector import SummaryCollector, read_gate_result
from loop_pilot.tasks.store import TaskStore


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _review_service(tmp_path: Path) -> tuple[ReviewService, App]:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    artifact_dir = tmp_path / "artifacts"
    state_dir = tmp_path / "state"
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                f"  state_dir: {state_dir}",
                f"  artifact_dir: {artifact_dir}",
                f"  sqlite_path: {state_dir / 'loop_pilot.db'}",
                f"  lock_dir: {tmp_path / 'locks'}",
                "  timezone: UTC",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    app = App.from_config_dir(config_dir)
    service = ReviewService(config=app.config, state_store=app.state_store, orchestrator=app.orchestrator)
    return service, app


def _load_db_manifest(sqlite_path: Path, run_id: str) -> dict:
    import sqlite3

    with sqlite3.connect(sqlite_path) as conn:
        row = conn.execute(
            "SELECT payload FROM artifact_manifests WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    assert row is not None, f"artifact_manifests row missing for {run_id}"
    return json.loads(row[0])


def _seed_patch_run(
    app: App,
    *,
    run_id: str = "patch-run-001",
    outcome: RunOutcome = RunOutcome.SUCCEEDED,
    phase: RunPhase = RunPhase.TERMINATED,
    review_status: str | None = None,
    report_status: str = "generated",
) -> Path:
    record = RunRecord(
        run_id=run_id,
        loop_type="intern",
        phase=phase,
        outcome=outcome,
        review_status=review_status,
        report_status=report_status,
        started_at=datetime.now(ZoneInfo("UTC")).isoformat(),
        finished_at=datetime.now(ZoneInfo("UTC")).isoformat(),
    )
    app.state_store.save_run(record)
    run_dir = app.config.artifact_dir / "intern" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "patch.diff").write_text("--- a/foo\n+++ b/foo\n", encoding="utf-8")
    (run_dir / "development-report.md").write_text("# Dev\n", encoding="utf-8")
    (run_dir / "gate_result.json").write_text(
        json.dumps({"gate": "pass", "run_id": run_id}),
        encoding="utf-8",
    )
    return run_dir


def test_patch_run_phase_is_waiting_approval_before_approve(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-waiting"
    _seed_patch_run(app, run_id=run_id, phase=RunPhase.REPORTING, outcome=RunOutcome.SUCCEEDED)

    service.maybe_enqueue(app.state_store.get_run(run_id))

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.phase == RunPhase.WAITING_APPROVAL
    assert record.phase != RunPhase.TERMINATED
    assert record.outcome == RunOutcome.PARTIAL
    assert record.review_status == "needs_review"


def test_review_suggestion_included_in_final_manifest(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-manifest-suggestion"
    run_dir = _seed_patch_run(app, run_id=run_id)

    service.maybe_enqueue(app.state_store.get_run(run_id))

    suggestion_path = run_dir / "review_suggestion.json"
    assert suggestion_path.exists()
    manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    suggestion_entry = next(
        item for item in manifest["artifacts"] if item["path"] == "review_suggestion.json"
    )
    assert suggestion_entry["sha256"] == _sha256(suggestion_path)
    suggestion = json.loads(suggestion_path.read_text(encoding="utf-8"))
    assert suggestion["gate"] == "needs_review"


def test_patch_run_writes_needs_review_gate_before_approval(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-001"
    _seed_patch_run(app, run_id=run_id)

    service.maybe_enqueue(app.state_store.get_run(run_id))

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.phase == RunPhase.WAITING_APPROVAL
    assert record.outcome == RunOutcome.PARTIAL
    assert record.review_status == "needs_review"
    assert record.report_status == "needs_review"

    gate = read_gate_result(app.config.artifact_dir, "intern", run_id)
    assert gate == "needs_review"
    assert gate != "pass"

    run_dir = app.config.artifact_dir / "intern" / run_id
    assert (run_dir / "review_required.md").exists()


def test_patch_run_is_needs_review_not_completed_in_summary(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-summary"
    _seed_patch_run(app, run_id=run_id)

    service.maybe_enqueue(app.state_store.get_run(run_id))

    iso = datetime.now(ZoneInfo("UTC")).date().isocalendar()
    collector = SummaryCollector(
        state_store=app.state_store,
        task_store=TaskStore(app.config.sqlite_path),
        artifact_dir=app.config.artifact_dir,
        lock_dir=app.config.lock_dir,
        timezone="UTC",
    )
    weekly = collector.collect_weekly(f"{iso.year}-W{iso.week:02d}")
    assert not any(run_id in item and "succeeded" in item for item in weekly.completed)


def test_approve_refreshes_persisted_artifact_manifest(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-db-sync"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        report_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    run_dir = app.config.artifact_dir / "intern" / run_id
    pre_approve_manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    app.state_store.save_artifact_manifest(run_id, pre_approve_manifest)

    assert read_gate_result(app.config.artifact_dir, "intern", run_id) == "needs_review"
    db_before = _load_db_manifest(app.config.sqlite_path, run_id)
    assert db_before["terminal_outcome"] == "partial"

    service.approve(run_id, note="ship it")

    assert read_gate_result(app.config.artifact_dir, "intern", run_id) == "pass"
    disk_manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    db_manifest = _load_db_manifest(app.config.sqlite_path, run_id)
    assert disk_manifest == db_manifest
    assert disk_manifest["terminal_outcome"] == "succeeded"
    assert disk_manifest["schema_version"] == "1"
    for item in disk_manifest["artifacts"]:
        rel = item["path"]
        assert item["sha256"] == _sha256(run_dir / rel), rel


def test_approved_manifest_validates_against_schema(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-schema-approved"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        report_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))
    service.approve(run_id, note="looks good")

    run_dir = app.config.artifact_dir / "intern" / run_id
    manifest = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    validate_artifact_manifest(manifest)


def test_approve_patch_run_finalizes_directly(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-002"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        report_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    record = service.approve(run_id, note="looks good")
    assert record.review_status == "approved"
    assert record.phase == RunPhase.TERMINATED
    assert record.outcome == RunOutcome.SUCCEEDED
    assert record.report_status == "completed"

    gate = read_gate_result(app.config.artifact_dir, "intern", run_id)
    assert gate == "pass"


def test_approved_patch_run_does_not_enter_resume_requested(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-resume-check"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        report_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    record = service.approve(run_id, note="looks good")
    assert record.review_status != "resume_requested"

    with pytest.raises(ResumeError, match="finalized|approved|succeeded"):
        service.resume(run_id)


def test_rejected_patch_run_cannot_resume(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-003"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    service.reject(run_id, reason="unsafe patch")

    gate = read_gate_result(app.config.artifact_dir, "intern", run_id)
    assert gate == "blocked"

    with pytest.raises(ResumeError, match="rejected"):
        service.resume(run_id)


def test_cancelled_patch_run_cannot_resume(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-004"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    service.cancel(run_id, reason="no longer needed")

    with pytest.raises(ResumeError, match="cancelled"):
        service.resume(run_id)


def test_patch_run_needs_review_blocks_resume(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-resume-block"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))

    with pytest.raises(ResumeError, match="approve/reject/cancel"):
        service.resume(run_id)
