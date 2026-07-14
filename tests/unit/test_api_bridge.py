from __future__ import annotations

import json
from pathlib import Path

from loop_pilot.api.server import ApiBridge
from loop_pilot.app import App
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.review.store import ReviewStore


def test_api_bridge_health_advertises_read_only_capabilities(sqlite_config_dir: Path) -> None:
    app = App.from_config_dir(sqlite_config_dir)

    status, payload = ApiBridge(app).dispatch("GET", "/api/health")

    assert status == 200
    assert payload["status"] == "ok"
    assert payload["readOnly"] is True
    assert payload["mutationsEnabled"] is False
    assert "/api/reviews/{run_id}" in payload["endpoints"]
    assert all("approve" not in endpoint and "reject" not in endpoint for endpoint in payload["endpoints"])


def test_api_bridge_lists_runs_and_details(sqlite_config_dir: Path) -> None:
    app = App.from_config_dir(sqlite_config_dir)
    record = RunRecord(
        run_id="run-api-1",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
        terminal_reason="done",
    )
    app.state_store.save_run(record)
    run_dir = app.config.artifact_dir / "intern" / record.run_id
    run_dir.mkdir(parents=True)
    report = run_dir / "development-report.md"
    report.write_text("# Done\n", encoding="utf-8")
    (run_dir / "artifact-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "run_id": record.run_id,
                "loop_type": record.loop_type,
                "artifacts": [
                    {
                        "path": "development-report.md",
                        "sha256": "abc123",
                        "kind": "report",
                        "human_readable": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    bridge = ApiBridge(app)
    status, payload = bridge.dispatch("GET", "/api/runs?limit=1")
    assert status == 200
    assert payload["items"][0]["runId"] == "run-api-1"
    assert payload["items"][0]["outcome"] == "succeeded"

    status, detail = bridge.dispatch("GET", "/api/runs/run-api-1")
    assert status == 200
    assert detail["run_id"] == "run-api-1"
    assert detail["outcome"] == "succeeded"
    assert detail["reportPath"] == str(report)
    assert detail["artifacts"] == [
        {
            "artifactId": "",
            "kind": "report",
            "path": "development-report.md",
            "absolutePath": str(report.resolve()),
            "mediaType": "",
            "sizeBytes": report.stat().st_size,
            "sha256": "abc123",
            "humanReadable": True,
            "exists": True,
        }
    ]


def test_api_bridge_reviews_are_read_only(sqlite_config_dir: Path) -> None:
    app = App.from_config_dir(sqlite_config_dir)
    record = RunRecord(
        run_id="run-review-1",
        loop_type="paper",
        phase=RunPhase.WAITING_APPROVAL,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
    )
    app.state_store.save_run(record)
    ReviewStore(app.config.sqlite_path).upsert_pending(
        run_id=record.run_id,
        loop_type=record.loop_type,
        artifact_path="var/artifacts/paper/run-review-1",
    )

    bridge = ApiBridge(app)
    status, payload = bridge.dispatch("GET", "/api/reviews")
    assert status == 200
    assert payload["items"][0]["runId"] == "run-review-1"
    assert payload["items"][0]["status"] == "pending"

    status, detail = bridge.dispatch("GET", "/api/reviews/run-review-1")
    assert status == 200
    assert detail["runId"] == "run-review-1"
    assert detail["artifactPath"] == "var/artifacts/paper/run-review-1"
    assert detail["run"]["phase"] == "WAITING_APPROVAL"

    status, denied = bridge.dispatch("POST", "/api/reviews/run-review-1/approve")
    assert status == 405
    assert denied["error"] == "method_not_allowed"


def test_api_bridge_today_summary(sqlite_config_dir: Path) -> None:
    app = App.from_config_dir(sqlite_config_dir)
    today = ApiBridge(app)._today()
    app.state_store.save_run(
        RunRecord(
            run_id="run-today-1",
            loop_type="daily_news",
            phase=RunPhase.TERMINATED,
            outcome=RunOutcome.SUCCEEDED,
            started_at=f"{today}T00:00:00+00:00",
        )
    )
    app.state_store.save_run(
        RunRecord(
            run_id="run-today-2",
            loop_type="intern",
            phase=RunPhase.WAITING_APPROVAL,
            outcome=RunOutcome.PARTIAL,
            started_at=f"{today}T01:00:00+00:00",
        )
    )

    status, payload = ApiBridge(app).dispatch("GET", "/api/summary/today")
    assert status == 200
    assert payload["date"] == today
    assert payload["plannedCount"] == 2
    assert payload["pendingReviewCount"] == 1
    assert payload["outcomeCounts"]["succeeded"] == 1
    assert payload["outcomeCounts"]["partial"] == 1
    assert payload["needsReview"][0]["runId"] == "run-today-2"
    assert [item["runId"] for item in payload["latestRuns"]] == ["run-today-2", "run-today-1"]
