"""Core domain models for LoopPilot Mini."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from loop_pilot.domain.states import RunOutcome, RunPhase


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def rfc3339(dt: datetime | None = None) -> str:
    if dt is None:
        dt = utc_now()
    return dt.astimezone(timezone.utc).isoformat()


def content_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class ArtifactReference:
    artifact_id: str
    kind: str
    path: str
    media_type: str
    sha256: str
    size_bytes: int
    created_by: str
    contains_sensitive_data: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BudgetSnapshot:
    max_duration_minutes: int = 30
    max_rounds: int = 3
    max_model_calls: int = 8
    remaining_minutes: float = 30.0
    remaining_rounds: int = 3
    remaining_model_calls: int = 8
    model_calls_used: int = 0
    rounds_used: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunRequest:
    run_id: str
    loop_type: str
    trigger: str = "manual"
    objective: str | None = None
    workspace_id: str = "default"
    config_snapshot_hash: str = ""
    parent_run_id: str | None = None
    requested_by: str = "owner"
    fixture: str | None = None
    workspace: str | None = None
    source_profile: str | None = None
    review_only: bool = False
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunRecord:
    run_id: str
    attempt_id: int = 1
    phase: RunPhase = RunPhase.CREATED
    outcome: RunOutcome | None = None
    loop_type: str = ""
    started_at: str = field(default_factory=rfc3339)
    soft_deadline_at: str = ""
    hard_deadline_at: str = ""
    finished_at: str | None = None
    current_round: int = 0
    budgets: BudgetSnapshot = field(default_factory=BudgetSnapshot)
    workspace_snapshot: ArtifactReference | None = None
    last_checkpoint_id: str | None = None
    terminal_reason: str | None = None
    report_status: str = "pending"
    review_status: str | None = None
    fixture: str | None = None
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["phase"] = self.phase.value
        data["outcome"] = self.outcome.value if self.outcome else None
        if self.workspace_snapshot:
            data["workspace_snapshot"] = self.workspace_snapshot.to_dict()
        data["budgets"] = self.budgets.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunRecord:
        budgets_data = data.get("budgets", {})
        ws = data.get("workspace_snapshot")
        return cls(
            run_id=data["run_id"],
            attempt_id=data.get("attempt_id", 1),
            phase=RunPhase(data["phase"]),
            outcome=RunOutcome(data["outcome"]) if data.get("outcome") else None,
            loop_type=data.get("loop_type", ""),
            started_at=data.get("started_at", rfc3339()),
            soft_deadline_at=data.get("soft_deadline_at", ""),
            hard_deadline_at=data.get("hard_deadline_at", ""),
            finished_at=data.get("finished_at"),
            current_round=data.get("current_round", 0),
            budgets=BudgetSnapshot(**budgets_data) if budgets_data else BudgetSnapshot(),
            workspace_snapshot=ArtifactReference(**ws) if ws else None,
            last_checkpoint_id=data.get("last_checkpoint_id"),
            terminal_reason=data.get("terminal_reason"),
            report_status=data.get("report_status", "pending"),
            review_status=data.get("review_status"),
            fixture=data.get("fixture"),
            dry_run=data.get("dry_run", False),
        )


@dataclass
class RoundRecord:
    round_id: int
    state_before: str
    decision: str
    reason_code: str
    started_at: str = field(default_factory=rfc3339)
    finished_at: str = ""
    plan_artifact: ArtifactReference | None = None
    input_artifacts: list[ArtifactReference] = field(default_factory=list)
    output_artifacts: list[ArtifactReference] = field(default_factory=list)
    evaluation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.plan_artifact:
            data["plan_artifact"] = self.plan_artifact.to_dict()
        data["input_artifacts"] = [a.to_dict() for a in self.input_artifacts]
        data["output_artifacts"] = [a.to_dict() for a in self.output_artifacts]
        return data


@dataclass
class EvaluationResult:
    evaluation_id: str
    verdict: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    blocking_findings: list[dict[str, Any]] = field(default_factory=list)
    non_blocking_findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactManifest:
    run_id: str
    artifacts: list[ArtifactReference] = field(default_factory=list)
    terminal_outcome: str | None = None
    created_at: str = field(default_factory=rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "terminal_outcome": self.terminal_outcome,
            "created_at": self.created_at,
        }
