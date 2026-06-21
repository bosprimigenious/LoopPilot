"""DailyNewsLoop scenario tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer


@pytest.fixture
def artifact_dir(tmp_path: Path) -> Path:
    d = tmp_path / "artifacts"
    d.mkdir()
    return d


class TestDailyNewsLoop:
    def test_day1_no_24h_winner_claim(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-news-day1",
            loop_type="daily_news",
            fixture="github_star_snapshots",
        )
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record, snapshot_day="day1")

        items_path = artifact_dir / "daily-news" / request.run_id / "processed-items.json"
        items = json.loads(items_path.read_text(encoding="utf-8"))
        for item in items:
            assert item.get("rank_label") == "candidate_hot_repo"
            assert item.get("star_delta_24h") is None

    def test_day2_correct_star_delta(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-news-day2",
            loop_type="daily_news",
            fixture="github_star_snapshots",
        )
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record, snapshot_day="day2")

        items_path = artifact_dir / "daily-news" / request.run_id / "processed-items.json"
        items = json.loads(items_path.read_text(encoding="utf-8"))
        deltas = {i["source_item_id"]: i.get("star_delta_24h") for i in items if i.get("star_delta_24h") is not None}
        assert deltas.get("repo-alpha") == 30
        assert deltas.get("repo-beta") == 5

    def test_deduplicate_and_filter_low_confidence(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-news-dedup",
            loop_type="daily_news",
            fixture="github_star_snapshots",
        )
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record, snapshot_day="day2")

        items_path = artifact_dir / "daily-news" / request.run_id / "processed-items.json"
        items = json.loads(items_path.read_text(encoding="utf-8"))
        urls = [i["canonical_url"] for i in items]
        assert urls.count("https://github.com/example/alpha-toolkit") == 1
        assert all(i.get("confidence") != "low" for i in items)

    def test_report_has_front_matter(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(run_id="test-news-report", loop_type="daily_news", fixture="github_star_snapshots")
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record, snapshot_day="day2")
        assert record.outcome == RunOutcome.SUCCEEDED

        report = artifact_dir / "daily-news" / request.run_id / "daily-news-report.md"
        content = report.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "artifact_manifest:" in content

    def test_candidate_routing_splits_intern_and_paper(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-news-routing",
            loop_type="daily_news",
            fixture="github_star_snapshots",
        )
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
        record, _, _ = loop.run(request, record, snapshot_day="day2")

        actions_path = artifact_dir / "daily-news" / request.run_id / "candidate-actions.json"
        assert actions_path.exists()
        actions = json.loads(actions_path.read_text(encoding="utf-8"))["candidates"]
        targets = {item["target_loop"] for item in actions}
        assert "intern" in targets
        assert "paper" in targets

        intern_path = artifact_dir / "daily-news" / request.run_id / "intern-candidates.md"
        paper_path = artifact_dir / "daily-news" / request.run_id / "paper-candidates.md"
        assert intern_path.exists()
        assert paper_path.exists()
        assert "Paper Inbox Candidates" in paper_path.read_text(encoding="utf-8")

        report = artifact_dir / "daily-news" / request.run_id / "daily-news-report.md"
        content = report.read_text(encoding="utf-8")
        assert "Intern Candidates" in content
        assert "Paper Candidates" in content

    def test_missing_fixture_blocks_without_success(self, artifact_dir: Path) -> None:
        loop = DailyNewsLoop(artifact_dir, PolicyEngine(), ReportRenderer(Path("templates")))
        request = RunRequest(
            run_id="test-news-missing",
            loop_type="daily_news",
            fixture="missing_fixture",
        )
        record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)

        record, _, _ = loop.run(request, record, snapshot_day="day2")

        assert record.outcome in {RunOutcome.BLOCKED, RunOutcome.FAILED}
        assert record.outcome != RunOutcome.SUCCEEDED
        assert "fixture" in (record.terminal_reason or "").lower()
