#!/usr/bin/env python3
"""Socket-free contract guard for the read-only local API bridge."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loop_pilot.api.server import ApiBridge  # noqa: E402
from loop_pilot.app import App  # noqa: E402
from loop_pilot.domain.models import RunRecord  # noqa: E402
from loop_pilot.domain.states import RunOutcome, RunPhase  # noqa: E402
from loop_pilot.review.store import ReviewStore  # noqa: E402


def _write_config(base: Path) -> Path:
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                f"  state_dir: {base / 'state'}",
                f"  artifact_dir: {base / 'artifacts'}",
                f"  sqlite_path: {base / 'state' / 'loop_pilot.db'}",
                f"  lock_dir: {base / 'locks'}",
                "  timezone: UTC",
            ]
        ),
        encoding="utf-8",
    )
    for name in (
        "intern.yaml",
        "paper.yaml",
        "daily_news.yaml",
        "policies.yaml",
        "sources.yaml",
        "models.yaml",
    ):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    return config_dir


def _check(name: str, fn) -> tuple[str, bool, str]:
    try:
        detail = fn()
    except Exception as exc:  # noqa: BLE001
        return name, False, str(exc)
    return name, True, detail or "PASS"


def _seed_app(base: Path) -> App:
    app = App.from_config_dir(_write_config(base))
    today = ApiBridge(app)._today()
    app.state_store.save_run(
        RunRecord(
            run_id="contract-run-1",
            loop_type="intern",
            phase=RunPhase.TERMINATED,
            outcome=RunOutcome.SUCCEEDED,
            terminal_reason="contract ok",
            started_at=f"{today}T00:00:00+00:00",
            finished_at=f"{today}T00:01:00+00:00",
        )
    )
    review_record = RunRecord(
        run_id="contract-review-1",
        loop_type="paper",
        phase=RunPhase.WAITING_APPROVAL,
        outcome=RunOutcome.PARTIAL,
        review_status="needs_review",
        started_at=f"{today}T00:02:00+00:00",
    )
    app.state_store.save_run(review_record)
    ReviewStore(app.config.sqlite_path).upsert_pending(
        run_id=review_record.run_id,
        loop_type=review_record.loop_type,
        artifact_path="var/artifacts/paper/contract-review-1",
    )
    return app


def check_health(bridge: ApiBridge) -> str:
    status, payload = bridge.dispatch("GET", "/api/health")
    assert status == 200
    assert payload["readOnly"] is True
    assert payload["mutationsEnabled"] is False
    endpoints = payload.get("endpoints", [])
    assert "/api/runs/{run_id}" in endpoints
    assert "/api/reviews/{run_id}" in endpoints
    assert all("approve" not in endpoint and "reject" not in endpoint for endpoint in endpoints)
    return f"{len(endpoints)} read-only endpoints"


def check_runs(bridge: ApiBridge) -> str:
    status, payload = bridge.dispatch("GET", "/api/runs?limit=1")
    assert status == 200
    assert len(payload["items"]) == 1
    status, detail = bridge.dispatch("GET", "/api/runs/contract-run-1")
    assert status == 200
    assert detail["run_id"] == "contract-run-1"
    assert detail["outcome"] == "succeeded"
    return "runs list/detail"


def check_summary(bridge: ApiBridge) -> str:
    status, payload = bridge.dispatch("GET", "/api/summary/today")
    assert status == 200
    assert payload["plannedCount"] == 2
    assert payload["pendingReviewCount"] == 1
    assert payload["outcomeCounts"]["succeeded"] == 1
    assert payload["outcomeCounts"]["partial"] == 1
    assert payload["needsReview"][0]["runId"] == "contract-review-1"
    assert [item["runId"] for item in payload["latestRuns"]] == [
        "contract-review-1",
        "contract-run-1",
    ]
    return "today summary"


def check_reviews(bridge: ApiBridge) -> str:
    status, payload = bridge.dispatch("GET", "/api/reviews")
    assert status == 200
    assert payload["items"][0]["runId"] == "contract-review-1"
    status, detail = bridge.dispatch("GET", "/api/reviews/contract-review-1")
    assert status == 200
    assert detail["runId"] == "contract-review-1"
    assert detail["run"]["phase"] == "WAITING_APPROVAL"
    return "reviews list/detail"


def check_read_only_rejection(bridge: ApiBridge) -> str:
    status, payload = bridge.dispatch("POST", "/api/reviews/contract-review-1/approve")
    assert status == 405
    assert payload["error"] == "method_not_allowed"
    return "POST rejected"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="looppilot-api-contract-") as raw:
        bridge = ApiBridge(_seed_app(Path(raw)))
        checks = [
            _check("health", lambda: check_health(bridge)),
            _check("runs", lambda: check_runs(bridge)),
            _check("summary", lambda: check_summary(bridge)),
            _check("reviews", lambda: check_reviews(bridge)),
            _check("read_only_rejection", lambda: check_read_only_rejection(bridge)),
        ]

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print(f"api-bridge contract: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks)")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
