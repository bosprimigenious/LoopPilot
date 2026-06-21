"""Summary collector tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.storage.sqlite import SQLiteStateStore
from loop_pilot.summary.collector import SummaryCollector, report_path
from loop_pilot.summary.renderer import render_daily_summary, render_weekly_summary
from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


def test_collect_daily_includes_today_and_inbox(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    inbox = InboxService(tasks)
    queue = QueueService(tasks, inbox)
    today = TodayService(tasks, queue, timezone="UTC")

    created = inbox.add("fix login test", source="manual", loop_hint="intern", priority=2)
    queue_item = queue.promote(created.item.id, loop_type="intern")
    today.add_queue_to_today(queue_item.id)

    record = RunRecord(
        run_id="run-daily-001",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
        started_at=datetime.now(ZoneInfo("UTC")).isoformat(),
    )
    state.save_run(record)

    today_date = today.today_date()
    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
    )
    data = collector.collect_daily(today_date)
    markdown = render_daily_summary(data)

    assert len(data.today_items) == 1
    assert any(row.run_id == "run-daily-001" for row in data.runs)
    assert "# Daily Summary" in markdown
    assert "## 2. Today" in markdown


def test_collect_weekly_builds_stats(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    record = RunRecord(
        run_id="run-week-001",
        loop_type="paper",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        started_at=f"{today}T10:00:00+00:00",
    )
    state.save_run(record)

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=tmp_path / "artifacts",
        lock_dir=tmp_path / "locks",
        timezone="UTC",
    )
    iso = datetime.now(ZoneInfo("UTC")).date().isocalendar()
    week_label = f"{iso.year}-W{iso.week:02d}"
    data = collector.collect_weekly(week_label)
    text = render_weekly_summary(data)

    assert "Weekly Summary" in text
    assert data.week == week_label


def test_report_path_prefers_final_report_over_diff_summary(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    run_dir = artifact_dir / "intern" / "run-report-001"
    run_dir.mkdir(parents=True)
    (run_dir / "development-report.md").write_text("# Development report\n", encoding="utf-8")
    (run_dir / "diff-summary.md").write_text("# Diff summary\n", encoding="utf-8")
    manifest = {
        "run_id": "run-report-001",
        "loop_type": "intern",
        "artifacts": [
            {"path": "diff-summary.md", "sha256": "abc", "human_readable": True, "kind": "log"},
            {"path": "development-report.md", "sha256": "def", "human_readable": True, "kind": "report"},
        ],
    }
    (run_dir / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    resolved = report_path(artifact_dir, "intern", "run-report-001")
    assert resolved is not None
    assert resolved.endswith("development-report.md")
    assert not resolved.endswith("diff-summary.md")
