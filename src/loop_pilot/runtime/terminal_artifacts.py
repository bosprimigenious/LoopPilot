"""Canonical terminal artifact contract (Milestone A Phase 2)."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome

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


_PATCH_DECIDED = frozenset({"approved", "rejected", "cancelled"})


def _patch_awaiting_review(run_dir: Path, record: RunRecord) -> bool:
    if not (run_dir / "patch.diff").exists():
        return False
    return (record.review_status or "") not in _PATCH_DECIDED


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


def finalize_terminal_artifacts(
    run_dir: Path,
    record: RunRecord,
    *,
    gate: str | None = None,
    tool_results: dict[str, Any] | None = None,
    review_required: bool = False,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    if _patch_awaiting_review(run_dir, record):
        record.outcome = RunOutcome.PARTIAL
        record.review_status = "needs_review"
        record.report_status = "needs_review"
        resolved_gate = "needs_review"
        review_required = True
    else:
        resolved_gate = gate or _gate_for_record(record)

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

    artifacts: list[dict[str, Any]] = []
    existing_path = run_dir / "artifact-manifest.json"
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            prior = existing.get("artifacts", [])
            if isinstance(prior, list):
                for item in prior:
                    if isinstance(item, dict) and item.get("path") != "artifact-manifest.json":
                        artifacts.append(dict(item))
        except json.JSONDecodeError:
            pass

    seen = {item.get("path") for item in artifacts if isinstance(item, dict)}
    adapter_trace_path = run_dir / "adapter-call-trace.jsonl"
    if adapter_trace_path.exists():
        has_adapter_trace = any(
            isinstance(item, dict)
            and item.get("kind") == "trace"
            and "adapter-call-trace.jsonl" in str(item.get("path", ""))
            for item in artifacts
        )
        if not has_adapter_trace:
            artifacts.append(
                {
                    "path": str(adapter_trace_path),
                    "sha256": _sha256(adapter_trace_path),
                    "human_readable": False,
                    "kind": "trace",
                }
            )
            seen.add(str(adapter_trace_path))

    for name in sorted({*CANONICAL_ARTIFACTS, "review_required.md", "patch.diff", *LOOP_REPORT_NAMES.values()}):
        if name == "artifact-manifest.json":
            continue
        path = run_dir / name
        if not path.exists():
            continue
        rel = name
        if rel in seen:
            continue
        kind = "report" if name.endswith(".md") else "machine"
        if "trace" in name:
            kind = "trace"
        artifacts.append(
            {
                "path": rel,
                "sha256": _sha256(path),
                "human_readable": name.endswith(".md"),
                "kind": kind,
            }
        )
        seen.add(rel)

    manifest = {
        "run_id": record.run_id,
        "loop_type": record.loop_type,
        "terminal_outcome": record.outcome.value if record.outcome else None,
        "artifacts": artifacts,
    }
    (run_dir / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def assert_terminal_artifacts(run_dir: Path) -> list[str]:
    missing = [name for name in CANONICAL_ARTIFACTS if not (run_dir / name).exists()]
    return missing
