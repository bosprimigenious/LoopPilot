"""Human review Markdown outputs for Practical MVP 0.2."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.domain.models import ArtifactReference, RunRecord, content_hash
from loop_pilot.domain.states import RunOutcome


def write_review_required(
    run_dir: Path,
    record: RunRecord,
    *,
    recommended: str,
    rationale: str,
    checklist: list[str] | None = None,
) -> ArtifactReference:
    lines = [
        "# Review Required",
        "",
        f"Run: `{record.run_id}`",
        f"Loop: {record.loop_type}",
        f"Outcome: {record.outcome.value if record.outcome else 'unknown'}",
        "",
        "## Recommended action",
        "",
        f"**{recommended}**",
        "",
        rationale,
        "",
    ]
    if checklist:
        lines.append("## Checklist")
        lines.append("")
        for item in checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")
    content = "\n".join(lines)
    path = run_dir / "review-required.md"
    path.write_text(content, encoding="utf-8")
    return _artifact(record.run_id, path, "review", "human_review")


def write_next_actions(
    run_dir: Path,
    record: RunRecord,
    actions: list[str],
) -> ArtifactReference:
    lines = [
        "# Next Actions",
        "",
        f"Run: `{record.run_id}`",
        "",
        "Human follow-up:",
        "",
    ]
    for action in actions:
        lines.append(f"- {action}")
    lines.append("")
    content = "\n".join(lines)
    path = run_dir / "next-actions.md"
    path.write_text(content, encoding="utf-8")
    return _artifact(record.run_id, path, "draft", "human_review")


def write_next_research_tasks(
    run_dir: Path,
    record: RunRecord,
    tasks: list[str],
) -> ArtifactReference:
    lines = [
        "# Next Research Tasks",
        "",
        f"Run: `{record.run_id}`",
        "",
    ]
    for task in tasks:
        lines.append(f"- {task}")
    lines.append("")
    content = "\n".join(lines)
    path = run_dir / "next_research_tasks.md"
    path.write_text(content, encoding="utf-8")
    return _artifact(record.run_id, path, "draft", "human_review")


def recommended_for_outcome(outcome: RunOutcome | None) -> str:
    if outcome == RunOutcome.SUCCEEDED:
        return "accept"
    if outcome == RunOutcome.PARTIAL:
        return "continue"
    if outcome == RunOutcome.BLOCKED:
        return "reject"
    if outcome == RunOutcome.EXHAUSTED:
        return "continue"
    return "review"


def _artifact(run_id: str, path: Path, kind: str, created_by: str) -> ArtifactReference:
    content = path.read_text(encoding="utf-8")
    return ArtifactReference(
        artifact_id=f"{run_id}-{path.name}",
        kind=kind,
        path=str(path),
        media_type="text/markdown",
        sha256=content_hash({"content": content}),
        size_bytes=len(content.encode()),
        created_by=created_by,
    )
