"""Review gate tests for patch.diff runs (0.4 truthful acceptance)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from loop_pilot.app import App
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.review.errors import ReviewDecisionError
from loop_pilot.review.service import ReviewService
from loop_pilot.runtime.orchestrator import ResumeError
from loop_pilot.summary.collector import SummaryCollector, read_gate_result
from loop_pilot.tasks.store import TaskStore


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


def test_patch_run_writes_needs_review_gate_before_approval(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-001"
    _seed_patch_run(app, run_id=run_id)

    service.maybe_enqueue(app.state_store.get_run(run_id))

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.phase == RunPhase.TERMINATED
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


def test_reject_after_approve_raises_and_preserves_state(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-double-reject"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        report_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))
    service.approve(run_id, note="ship it")

    with pytest.raises(ReviewDecisionError, match="already decided: approved"):
        service.reject(run_id, reason="too late")

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.review_status == "approved"
    assert record.outcome == RunOutcome.SUCCEEDED
    assert read_gate_result(app.config.artifact_dir, "intern", run_id) == "pass"


def test_defer_after_approve_raises(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-defer-after-approve"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))
    service.approve(run_id, note="ship it")

    with pytest.raises(ReviewDecisionError, match="already decided: approved"):
        service.defer(run_id, until="2099-01-01", reason="later")


def test_cancel_after_reject_raises(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-double-cancel"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))
    service.reject(run_id, reason="unsafe patch")

    with pytest.raises(ReviewDecisionError, match="already decided: rejected"):
        service.cancel(run_id, reason="changed mind")

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.review_status == "rejected"
    assert read_gate_result(app.config.artifact_dir, "intern", run_id) == "blocked"


def test_approve_after_reject_raises(tmp_path: Path) -> None:
    service, app = _review_service(tmp_path)
    run_id = "patch-run-approve-after-reject"
    _seed_patch_run(
        app,
        run_id=run_id,
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    service.maybe_enqueue(app.state_store.get_run(run_id))
    service.reject(run_id, reason="unsafe patch")

    with pytest.raises(ReviewDecisionError, match="already decided: rejected"):
        service.approve(run_id, note="second thoughts")

    record = app.state_store.get_run(run_id)
    assert record is not None
    assert record.review_status == "rejected"
    assert read_gate_result(app.config.artifact_dir, "intern", run_id) == "blocked"
