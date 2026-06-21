"""Canonical terminal artifact contract (Milestone A Phase 2)."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord

CANONICAL_ARTIFACTS = (
    "run_meta.json",
    "gate_result.json",
    "tool-results.json",
    "report.md",
    "artifact-manifest.json",
    "loop_trace.jsonl",
)

LOOP_REPORT_NAMES = {
    "intern": "development-report.md",
    "paper": "paper-development-report.md",
    "daily_news": "daily-news-report.md",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _gate_for_record(record: RunRecord) -> str:
    if record.phase.value == "WAITING_APPROVAL":
        return "needs_review"
    if record.outcome is None:
        return "pass"
    outcome = record.outcome.value
    if outcome in {"blocked", "failed"}:
        return "blocked"
    if outcome in {"partial", "exhausted"}:
        return "needs_review"
    return "pass"


def _prior_metadata(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Load kind/human_readable from an existing manifest; never reuse sha256."""
    manifest_path = run_dir / "artifact-manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    metadata: dict[str, dict[str, Any]] = {}
    prior = existing.get("artifacts", [])
    if not isinstance(prior, list):
        return metadata
    for item in prior:
        if not isinstance(item, dict):
            continue
        rel = item.get("path")
        if not rel or rel == "artifact-manifest.json":
            continue
        entry: dict[str, Any] = {}
        if "kind" in item:
            entry["kind"] = item["kind"]
        if "human_readable" in item:
            entry["human_readable"] = item["human_readable"]
        metadata[str(rel)] = entry
    return metadata


def _infer_kind(rel: str) -> str:
    if rel in {
        "report.md",
        "development-report.md",
        "paper-development-report.md",
        "daily-news-report.md",
        "review_required.md",
    }:
        return "report"
    if rel.endswith(".md"):
        return "log"
    if "trace" in rel:
        return "trace"
    return "machine"


def _infer_human_readable(rel: str) -> bool:
    return rel.endswith(".md")


def _scan_run_dir_artifacts(run_dir: Path, prior: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(run_dir).as_posix()
        if rel == "artifact-manifest.json" or rel.startswith("."):
            continue
        meta = prior.get(rel, {})
        kind = meta.get("kind") if "kind" in meta else _infer_kind(rel)
        human_readable = (
            meta.get("human_readable") if "human_readable" in meta else _infer_human_readable(rel)
        )
        artifacts.append(
            {
                "path": rel,
                "sha256": _sha256(path),
                "human_readable": human_readable,
                "kind": kind,
            }
        )
    return artifacts


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def finalize_terminal_artifacts(
    run_dir: Path,
    record: RunRecord,
    *,
    gate: str | None = None,
    tool_results: dict[str, Any] | None = None,
    review_required: bool = False,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved_gate = gate or _gate_for_record(record)
    prior = _prior_metadata(run_dir)

    run_meta = {
        "run_id": record.run_id,
        "loop_type": record.loop_type,
        "phase": record.phase.value,
        "outcome": record.outcome.value if record.outcome else None,
        "started_at": record.started_at,
        "finished_at": record.finished_at,
        "dry_run": record.dry_run,
        "terminal_reason": record.terminal_reason,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    gate_payload = {"gate": resolved_gate, "run_id": record.run_id}
    (run_dir / "gate_result.json").write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")

    if tool_results is None:
        existing = run_dir / "tool-results.json"
        if existing.exists():
            try:
                tool_results = json.loads(existing.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                tool_results = {"calls": [], "note": "no tool calls began"}
        else:
            tool_results = {"calls": [], "note": "no tool calls began"}
    (run_dir / "tool-results.json").write_text(json.dumps(tool_results, indent=2), encoding="utf-8")

    report_md = run_dir / "report.md"
    loop_report_name = LOOP_REPORT_NAMES.get(record.loop_type, "report.md")
    loop_report = run_dir / loop_report_name
    if loop_report.exists() and loop_report != report_md:
        report_md.write_text(loop_report.read_text(encoding="utf-8"), encoding="utf-8")
    elif not report_md.exists():
        outcome = record.outcome.value if record.outcome else "unknown"
        report_md.write_text(
            f"# Run {record.run_id}\n\nOutcome: {outcome}\n",
            encoding="utf-8",
        )

    trace_src = run_dir / "trace.jsonl"
    trace_dst = run_dir / "loop_trace.jsonl"
    if trace_src.exists():
        shutil.copy2(trace_src, trace_dst)
    elif not trace_dst.exists():
        trace_dst.write_text(
            json.dumps({"event": "run_terminal", "run_id": record.run_id}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    needs_review = review_required or resolved_gate in {"needs_review", "blocked"}
    if needs_review:
        review_path = run_dir / "review_required.md"
        if not review_path.exists():
            review_path.write_text(
                f"# Review required\n\nRun `{record.run_id}` needs human review.\n",
                encoding="utf-8",
            )

    artifacts = _scan_run_dir_artifacts(run_dir, prior)

    manifest = {
        "run_id": record.run_id,
        "loop_type": record.loop_type,
        "terminal_outcome": record.outcome.value if record.outcome else None,
        "artifacts": artifacts,
    }
    _atomic_write_json(run_dir / "artifact-manifest.json", manifest)
    return manifest


def assert_terminal_artifacts(run_dir: Path) -> list[str]:
    missing = [name for name in CANONICAL_ARTIFACTS if not (run_dir / name).exists()]
    return missing
