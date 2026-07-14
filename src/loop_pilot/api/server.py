"""Small read-only HTTP bridge for local LoopPilot clients."""

from __future__ import annotations

import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from loop_pilot import __version__
from loop_pilot.app import App
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome
from loop_pilot.review.store import ReviewItem, ReviewStore
from loop_pilot.summary.collector import report_path, run_artifact_dir
from loop_pilot.util.timezone import zone_info


class ApiBridge:
    """Read-only adapter between local LoopPilot state and JSON HTTP responses."""

    REVIEW_OUTCOMES = {RunOutcome.PARTIAL, RunOutcome.BLOCKED, RunOutcome.EXHAUSTED}
    READ_ONLY_ENDPOINTS = (
        "/api/health",
        "/api/summary/today",
        "/api/runs",
        "/api/runs/{run_id}",
        "/api/reviews",
        "/api/reviews/{run_id}",
    )

    def __init__(self, app: App) -> None:
        self.app = app
        self.cfg = app.config

    @classmethod
    def from_config_dir(cls, config_dir: Path) -> ApiBridge:
        return cls(App.from_config_dir(config_dir))

    def dispatch(self, method: str, target: str) -> tuple[int, dict[str, Any]]:
        parsed = urlparse(target)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if method == "OPTIONS":
            return 204, {}
        if method != "GET":
            return 405, {"error": "method_not_allowed", "message": "API bridge is read-only"}
        if path == "/api/health":
            return 200, self.health()
        if path == "/api/runs":
            return 200, {"items": self.list_runs(limit=self._limit(query, default=50))}
        if path.startswith("/api/runs/"):
            run_id = unquote(path.removeprefix("/api/runs/"))
            record = self.app.state_store.get_run(run_id)
            if record is None:
                return 404, {"error": "not_found", "message": f"run not found: {run_id}"}
            return 200, self.run_detail(record)
        if path == "/api/reviews":
            return 200, {"items": self.list_reviews()}
        if path.startswith("/api/reviews/"):
            run_id = unquote(path.removeprefix("/api/reviews/"))
            review = self.review_detail(run_id)
            if review is None:
                return 404, {"error": "not_found", "message": f"review not found: {run_id}"}
            return 200, review
        if path == "/api/summary/today":
            return 200, self.today_summary()
        return 404, {"error": "not_found", "message": f"unknown endpoint: {path}"}

    def health(self) -> dict[str, Any]:
        backend = str(self.cfg.runtime.get("state_backend", "json")).lower()
        return {
            "status": "ok",
            "service": "loop-pilot-api",
            "version": __version__,
            "stateBackend": backend,
            "readOnly": True,
            "mutationsEnabled": False,
            "allowedMethods": ["GET", "OPTIONS"],
            "corsPreflight": True,
            "endpoints": list(self.READ_ONLY_ENDPOINTS),
            "allowRealAdapters": self.cfg.allow_real_adapters,
        }

    def list_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return [self.run_summary(record) for record in self.app.state_store.list_runs(limit=limit)]

    def run_detail(self, record: RunRecord) -> dict[str, Any]:
        payload = record.to_dict()
        payload["gate"] = self._gate(record)
        payload["reportPath"] = report_path(self.cfg.artifact_dir, record.loop_type, record.run_id)
        payload["artifacts"] = self._artifact_preview(record)
        return payload

    def run_summary(self, record: RunRecord) -> dict[str, Any]:
        updated_at = record.finished_at or record.started_at
        return {
            "runId": record.run_id,
            "title": self._title(record),
            "loopType": record.loop_type,
            "phase": record.phase.value,
            "outcome": record.outcome.value if record.outcome else None,
            "reviewStatus": record.review_status,
            "reportStatus": record.report_status,
            "terminalReason": record.terminal_reason,
            "startedAt": record.started_at,
            "finishedAt": record.finished_at,
            "updatedAt": updated_at,
            "gate": self._gate(record),
            "reportPath": report_path(self.cfg.artifact_dir, record.loop_type, record.run_id),
        }

    def list_reviews(self) -> list[dict[str, Any]]:
        backend = str(self.cfg.runtime.get("state_backend", "json")).lower()
        if backend == "sqlite" and self.cfg.sqlite_path.exists():
            store = ReviewStore(self.cfg.sqlite_path)
            items = store.list_pending(include_deferred=True)
            if items:
                return [self._review_item_to_dict(item) for item in items]
        return self._review_rows_from_runs()

    def review_detail(self, run_id: str) -> dict[str, Any] | None:
        record = self.app.state_store.get_run(run_id)
        backend = str(self.cfg.runtime.get("state_backend", "json")).lower()
        if backend == "sqlite" and self.cfg.sqlite_path.exists():
            item = ReviewStore(self.cfg.sqlite_path).get_by_run_id(run_id)
            if item is not None:
                detail = self._review_item_to_dict(item)
                detail["run"] = self.run_summary(record) if record is not None else None
                return detail
        if record is None or not self._needs_review(record):
            return None
        detail = self._review_row_from_record(record)
        detail["run"] = self.run_summary(record)
        return detail

    def today_summary(self) -> dict[str, Any]:
        today = self._today()
        runs = [
            record
            for record in self.app.state_store.list_runs(limit=500)
            if (record.started_at or "").startswith(today)
            or (record.finished_at or "").startswith(today)
        ]
        latest = sorted(
            runs,
            key=lambda item: item.finished_at or item.started_at,
            reverse=True,
        )[:5]
        reviews = self.list_reviews()
        blocked = [
            record
            for record in runs
            if record.outcome in {RunOutcome.BLOCKED, RunOutcome.FAILED}
        ]
        return {
            "date": today,
            "plannedCount": len(runs),
            "pendingReviewCount": len(reviews),
            "blockedCount": len(blocked),
            "outcomeCounts": self._outcome_counts(runs),
            "latestRuns": [self.run_summary(record) for record in latest],
            "needsReview": reviews[:3],
        }

    def _review_rows_from_runs(self) -> list[dict[str, Any]]:
        return [
            self._review_row_from_record(record)
            for record in self.app.state_store.list_runs(limit=500)
            if self._needs_review(record)
        ]

    def _review_row_from_record(self, record: RunRecord) -> dict[str, Any]:
        return {
            "runId": record.run_id,
            "loopType": record.loop_type,
            "status": record.review_status or "needs_review",
            "title": record.terminal_reason or f"{record.loop_type} needs review",
            "reason": record.terminal_reason,
            "artifactPath": str(
                self.cfg.artifact_dir
                / record.loop_type.replace("_", "-")
                / record.run_id
            ),
            "createdAt": record.finished_at or record.started_at,
        }

    def _review_item_to_dict(self, item: ReviewItem) -> dict[str, Any]:
        data = asdict(item)
        return {
            "id": data["id"],
            "runId": data["run_id"],
            "loopType": data["loop_type"],
            "status": data["status"],
            "decision": data["decision"],
            "reason": data["reason"],
            "deferredUntil": data["deferred_until"],
            "artifactPath": data["artifact_path"],
            "createdAt": data["created_at"],
            "decidedAt": data["decided_at"],
        }

    def _needs_review(self, record: RunRecord) -> bool:
        if record.review_status in {"pending", "needs_review", "needs_revision", "resume_requested"}:
            return True
        return record.outcome in self.REVIEW_OUTCOMES

    @staticmethod
    def _outcome_counts(runs: list[RunRecord]) -> dict[str, int]:
        counts = {
            "succeeded": 0,
            "partial": 0,
            "blocked": 0,
            "failed": 0,
            "other": 0,
        }
        for record in runs:
            outcome = record.outcome.value if record.outcome else "other"
            if outcome in counts:
                counts[outcome] += 1
            else:
                counts["other"] += 1
        return counts

    def _gate(self, record: RunRecord) -> str | None:
        path = self.cfg.artifact_dir / record.loop_type.replace("_", "-") / record.run_id / "gate_result.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        gate = payload.get("gate") or payload.get("verdict")
        return str(gate) if gate else None

    def _artifact_preview(self, record: RunRecord) -> list[dict[str, Any]]:
        run_dir = run_artifact_dir(self.cfg.artifact_dir, record.loop_type, record.run_id)
        manifest_path = run_dir / "artifact-manifest.json"
        if not manifest_path.exists():
            return []
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        artifacts = manifest.get("artifacts", [])
        if not isinstance(artifacts, list):
            return []
        return [
            item
            for entry in artifacts
            if isinstance(entry, dict)
            for item in [self._artifact_entry(run_dir, entry)]
            if item is not None
        ]

    @staticmethod
    def _artifact_entry(run_dir: Path, entry: dict[str, Any]) -> dict[str, Any] | None:
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            return None
        try:
            candidate = (run_dir / raw_path).resolve()
            candidate.relative_to(run_dir.resolve())
        except ValueError:
            return None
        size = entry.get("size_bytes", entry.get("sizeBytes"))
        if size is None and candidate.is_file():
            size = candidate.stat().st_size
        human_readable = entry.get("human_readable", entry.get("humanReadable"))
        return {
            "artifactId": str(entry.get("artifact_id", entry.get("artifactId", ""))),
            "kind": str(entry.get("kind", "artifact")),
            "path": raw_path,
            "absolutePath": str(candidate),
            "mediaType": str(entry.get("media_type", entry.get("mediaType", ""))),
            "sizeBytes": size,
            "sha256": str(entry.get("sha256", "")),
            "humanReadable": bool(human_readable),
            "exists": candidate.is_file(),
        }

    @staticmethod
    def _title(record: RunRecord) -> str:
        labels = {
            "daily_news": "DailyNews 信号筛选",
            "intern": "InternLoop 开发闭环",
            "paper": "PaperLoop 研究闭环",
        }
        return labels.get(record.loop_type, record.loop_type or record.run_id)

    def _today(self) -> str:
        from datetime import datetime

        timezone = str(self.cfg.runtime.get("timezone", "Asia/Shanghai"))
        return datetime.now(zone_info(timezone)).date().isoformat()

    @staticmethod
    def _limit(query: dict[str, list[str]], *, default: int) -> int:
        raw = query.get("limit", [str(default)])[0]
        try:
            value = int(raw)
        except ValueError:
            return default
        return max(1, min(value, 500))


def serve_api(
    *,
    config_dir: Path,
    host: str = "127.0.0.1",
    port: int = 7860,
) -> None:
    bridge = ApiBridge.from_config_dir(config_dir)

    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send(*bridge.dispatch("OPTIONS", self.path))

        def do_GET(self) -> None:  # noqa: N802
            self._send(*bridge.dispatch("GET", self.path))

        def do_POST(self) -> None:  # noqa: N802
            self._send(*bridge.dispatch("POST", self.path))

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            body = b"" if status == 204 else json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
