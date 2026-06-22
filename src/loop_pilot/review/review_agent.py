"""Review suggestion helper — structured hints only, never auto-approves."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase


def suggest_review(record: RunRecord, run_dir: Path) -> dict[str, Any]:
    gate_path = run_dir / "gate_result.json"
    gate = "needs_review"
    if gate_path.exists():
        try:
            payload = json.loads(gate_path.read_text(encoding="utf-8"))
            gate = str(payload.get("gate", gate))
        except json.JSONDecodeError:
            pass

    recommended = "review"
    if record.outcome == RunOutcome.SUCCEEDED:
        recommended = "accept"
    elif record.outcome in {RunOutcome.BLOCKED, RunOutcome.FAILED}:
        recommended = "reject"
    elif record.phase == RunPhase.WAITING_APPROVAL:
        recommended = "continue"

    return {
        "run_id": record.run_id,
        "gate": gate,
        "recommended_action": recommended,
        "rationale": record.terminal_reason or f"phase={record.phase.value}",
        "automated": True,
        "note": "Suggestion only — human decision required via review CLI",
    }


def write_suggestion(run_dir: Path, suggestion: dict[str, Any]) -> Path:
    path = run_dir / "review_suggestion.json"
    path.write_text(json.dumps(suggestion, indent=2), encoding="utf-8")
    return path
