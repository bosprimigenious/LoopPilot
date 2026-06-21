"""Adapter blocked-path trace helpers for auditable 0.3 runs."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.domain.models import ArtifactReference, content_hash
from loop_pilot.runtime.trace import TraceWriter


def append_adapter_blocked_event(
    adapter_trace: TraceWriter,
    *,
    blocked_reason: str,
    dry_run: bool,
    allow_real_adapters: bool,
    adapter_id: str | None = None,
) -> None:
    adapter_trace.append(
        {
            "event": "adapter_blocked",
            "status": "blocked",
            "blocked_reason": blocked_reason,
            "dry_run": dry_run,
            "allow_real_adapters": allow_real_adapters,
            "adapter_id": adapter_id,
        }
    )


def adapter_trace_artifact_ref(run_dir: Path, run_id: str) -> ArtifactReference:
    path = run_dir / "adapter-call-trace.jsonl"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    return ArtifactReference(
        artifact_id=f"{run_id}-adapter-call-trace",
        kind="trace",
        path=str(path),
        media_type="application/x-ndjson",
        sha256=content_hash({"content": content}),
        size_bytes=len(content.encode()),
        created_by="adapter_registry",
    )
