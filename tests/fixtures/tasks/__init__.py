"""Sample candidate-actions for task import tests."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "candidate-actions.json"

SAMPLE = {
    "candidates": [
        {
            "target_loop": "intern",
            "priority": "high",
            "source_item_id": "repo-alpha",
            "reason": "github signal routed to intern",
            "recommended_action": "evaluate_for_intern_task",
        },
        {
            "target_loop": "paper",
            "priority": "normal",
            "source_item_id": "paper-001",
            "reason": "paper signal routed to paper",
            "recommended_action": "review_claim_evidence",
        },
    ]
}


def write_fixture(path: Path | None = None) -> Path:
    target = path or FIXTURE_PATH
    target.write_text(json.dumps(SAMPLE, indent=2), encoding="utf-8")
    return target
