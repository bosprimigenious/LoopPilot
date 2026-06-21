"""V1 recovery, approval, and checkpoint integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.app import App
from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.approvals import cancel_run
from loop_pilot.runtime.orchestrator import ResumeError
from loop_pilot.runtime.recovery import build_recovery_plan
from loop_pilot.storage.sqlite import SQLiteStateStore


def _sqlite_config(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                f"  state_dir: {tmp_path / 'state'}",
                f"  artifact_dir: {tmp_path / 'artifacts'}",
                f"  sqlite_path: {tmp_path / 'state' / 'loop-pilot.sqlite3'}",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    (config_dir / "models.yaml").write_text(
        "\n".join(
            [
                "model_roles:",
                "  coding_agent:",
                "    candidates: [mock]",
                "    require: {file_write: true, tool_calls: true, dry_run: true}",
                "  analysis_medium:",
                "    candidates: [mock]",
                "    require: {structured_output: true}",
                "  screening_economical:",
                "    candidates: [mock]",
                "    require: {structured_output: true}",
                "adapters:",
                "  mock:",
                "    kind: mock",
                "    capabilities:",
                "      supports_structured_output: true",
                "      supports_dry_run: true",
                "      supports_file_write: true",
                "      supports_tools: true",
            ]
        ),
        encoding="utf-8",
    )
    return config_dir


def test_run_loop_writes_checkpoints_to_sqlite(tmp_path: Path) -> None:
    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    request = RunRequest(
        run_id="cp-intern-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=True,
        config_snapshot_hash=application.config.snapshot_hash(),
    )

    record = application.orchestrator.run_loop(request)

    checkpoint = application.state_store.latest_checkpoint(record.run_id)
    assert checkpoint is not None
    assert record.last_checkpoint_id is not None
    assert record.outcome == RunOutcome.PARTIAL
    assert record.phase == RunPhase.WAITING_APPROVAL
    assert record.review_status == "needs_review"


def test_cancelled_run_cannot_resume(tmp_path: Path) -> None:
    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    store = application.state_store
    record = RunRecord(
        run_id="cancelled-001",
        loop_type="intern",
        phase=RunPhase.WAITING_APPROVAL,
        fixture="simple_python_bug",
        dry_run=True,
    )
    store.save_run(record)
    store.save_checkpoint(
        record.run_id,
        checkpoint_id="cp-waiting",
        phase=RunPhase.WAITING_APPROVAL.value,
        payload={"resume_allowed": True, "fixture": "simple_python_bug", "dry_run": True},
    )
    cancel_run(store, record.run_id)

    plan = build_recovery_plan(store, record.run_id)
    assert plan is not None
    assert plan.can_resume is False

    with pytest.raises(ResumeError, match="cancelled"):
        application.orchestrator.resume_run(record.run_id)


def test_resume_after_approval_completes_intern_dry_run(tmp_path: Path) -> None:
    from loop_pilot.review.service import ReviewService

    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    request = RunRequest(
        run_id="resume-intern-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=True,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    assert record.outcome == RunOutcome.PARTIAL

    service = ReviewService(
        config=application.config,
        state_store=application.state_store,
        orchestrator=application.orchestrator,
    )
    service.maybe_enqueue(record)
    approved = service.approve(record.run_id, note="approved for test")

    assert approved.phase == RunPhase.TERMINATED
    assert approved.outcome == RunOutcome.SUCCEEDED
    assert approved.review_status == "approved"
    assert approved.review_status != "resume_requested"

    with pytest.raises(ResumeError, match="finalized|already succeeded"):
        service.resume(record.run_id)


def test_resume_without_approval_is_blocked(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    record = RunRecord(
        run_id="needs-approval-001",
        loop_type="intern",
        phase=RunPhase.WAITING_APPROVAL,
        fixture="simple_python_bug",
        dry_run=True,
    )
    store.save_run(record)
    store.save_checkpoint(
        record.run_id,
        checkpoint_id="cp-waiting",
        phase=RunPhase.WAITING_APPROVAL.value,
        payload={"fixture": "simple_python_bug", "dry_run": True},
    )

    plan = build_recovery_plan(store, record.run_id)
    assert plan is not None
    assert plan.can_resume is False
    assert "approval" in plan.reason


def test_acting_interrupt_can_resume_from_exact_round(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loop_pilot.loops.intern import loop as intern_mod

    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    original_apply = intern_mod.InternLoop._apply_fix
    interrupted = {"once": False, "apply_calls": 0}

    def explode_once(self, work_dir):  # noqa: ANN001
        interrupted["apply_calls"] += 1
        if interrupted["apply_calls"] < 2:
            return original_apply(self, work_dir)
        if not interrupted["once"]:
            interrupted["once"] = True
            raise InterruptedError("simulated ACTING interruption")
        return original_apply(self, work_dir)

    monkeypatch.setattr(intern_mod.InternLoop, "_apply_fix", explode_once)

    request = RunRequest(
        run_id="interrupt-resume-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=False,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    assert record.outcome == RunOutcome.FAILED
    assert "interrupted" in (record.terminal_reason or "").lower()

    plan = build_recovery_plan(application.state_store, record.run_id)
    assert plan is not None
    assert plan.can_resume is True
    assert plan.checkpoint.get("payload", {}).get("current_round", 0) >= 2

    resumed = application.orchestrator.resume_run(record.run_id)
    assert resumed.outcome == RunOutcome.PARTIAL
    assert resumed.phase == RunPhase.WAITING_APPROVAL
    assert resumed.review_status == "needs_review"


def test_duplicate_resume_after_success_is_rejected(tmp_path: Path) -> None:
    from loop_pilot.review.service import ReviewService

    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    request = RunRequest(
        run_id="dup-resume-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=True,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    assert record.outcome == RunOutcome.PARTIAL

    service = ReviewService(
        config=application.config,
        state_store=application.state_store,
        orchestrator=application.orchestrator,
    )
    service.maybe_enqueue(record)
    approved = service.approve(record.run_id, note="ok")
    assert approved.outcome == RunOutcome.SUCCEEDED

    with pytest.raises(ResumeError, match="finalized|already succeeded"):
        service.resume(record.run_id)


def test_lock_not_left_after_failed_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loop_pilot.loops.intern import loop as intern_mod

    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)

    def failing_run(self, request, record, **kwargs):  # noqa: ANN001
        raise RuntimeError("injected failure")

    monkeypatch.setattr(intern_mod.InternLoop, "run", failing_run)

    request = RunRequest(
        run_id="lock-fail-001",
        loop_type="intern",
        fixture="simple_python_bug",
        dry_run=True,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    assert record.outcome == RunOutcome.FAILED
    assert not application.orchestrator.locks.is_held("loop:intern")


def test_lock_not_left_after_cancelled_run(tmp_path: Path) -> None:
    config_dir = _sqlite_config(tmp_path)
    application = App.from_config_dir(config_dir)
    store = application.state_store
    record = RunRecord(
        run_id="lock-cancel-001",
        loop_type="intern",
        phase=RunPhase.ACTING,
        fixture="simple_python_bug",
        dry_run=True,
    )
    store.save_run(record)
    cancel_run(store, record.run_id)
    assert not application.orchestrator.locks.is_held("loop:intern")

