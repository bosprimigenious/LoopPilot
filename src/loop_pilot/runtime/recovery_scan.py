"""Recovery scan for stale, interrupted, and blocked runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.recovery import build_recovery_plan
from loop_pilot.storage.base import StateStore


@dataclass
class RecoveryFinding:
    run_id: str
    loop_type: str
    phase: str
    outcome: str | None
    category: str
    recommended_action: str
    reason: str


def scan_recovery(
    store: StateStore,
    *,
    lock_dir: Path,
    stale_after: timedelta = timedelta(hours=24),
) -> list[RecoveryFinding]:
    if not store.supports_v1_features():
        return []

    findings: list[RecoveryFinding] = []
    now = datetime.now(timezone.utc)
    runs = store.list_runs(limit=500)

    for record in runs:
        phase = record.phase
        outcome = record.outcome.value if record.outcome else None

        if phase == RunPhase.TERMINATED:
            if outcome == RunOutcome.FAILED.value:
                findings.append(
                    RecoveryFinding(
                        run_id=record.run_id,
                        loop_type=record.loop_type,
                        phase=phase.value,
                        outcome=outcome,
                        category="failed_run",
                        recommended_action="review_or_resume",
                        reason="run terminated with FAILED outcome",
                    )
                )
            continue

        if phase == RunPhase.WAITING_APPROVAL:
            findings.append(
                RecoveryFinding(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    phase=phase.value,
                    outcome=outcome,
                    category="waiting_approval",
                    recommended_action="needs_human",
                    reason="awaiting user approval",
                )
            )
            continue

        if phase == RunPhase.ACTING:
            findings.append(
                RecoveryFinding(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    phase=phase.value,
                    outcome=outcome,
                    category="acting_interrupted",
                    recommended_action="manual_review_required",
                    reason="ACTING phase interrupted; do not auto-resume",
                )
            )
            continue

        if phase in {RunPhase.REPORTING, RunPhase.PERSISTING, RunPhase.FINALIZING}:
            findings.append(
                RecoveryFinding(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    phase=phase.value,
                    outcome=outcome,
                    category="interrupted_run",
                    recommended_action="manual_review_required",
                    reason=f"run interrupted during {phase.value}",
                )
            )
            continue

        if outcome is None and phase != RunPhase.TERMINATED:
            plan = build_recovery_plan(store, record.run_id)
            action = "resume" if plan and plan.can_resume else "manual_review_required"
            reason = plan.reason if plan else "non-terminal run without outcome"
            findings.append(
                RecoveryFinding(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    phase=phase.value,
                    outcome=outcome,
                    category="interrupted_run",
                    recommended_action=action,
                    reason=reason,
                )
            )

        started_at = _parse_timestamp(record.started_at)
        if started_at and now - started_at > stale_after and phase != RunPhase.TERMINATED:
            findings.append(
                RecoveryFinding(
                    run_id=record.run_id,
                    loop_type=record.loop_type,
                    phase=phase.value,
                    outcome=outcome,
                    category="stale_run",
                    recommended_action="manual_review_required",
                    reason=f"no progress since {started_at.isoformat()}",
                )
            )

    findings.extend(_scan_stale_locks(lock_dir))
    return _dedupe_findings(findings)


def _scan_stale_locks(lock_dir: Path) -> list[RecoveryFinding]:
    if not lock_dir.exists():
        return []

    findings: list[RecoveryFinding] = []
    for lock_path in sorted(lock_dir.glob("*.lock")):
        holder = lock_path.read_text(encoding="utf-8").strip() or "unknown"
        findings.append(
            RecoveryFinding(
                run_id=holder,
                loop_type="lock",
                phase="LOCKED",
                outcome=None,
                category="stale_lock",
                recommended_action="blocked",
                reason=f"lock file present: {lock_path.name}",
            )
        )
    return findings


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _dedupe_findings(findings: list[RecoveryFinding]) -> list[RecoveryFinding]:
    seen: set[tuple[str, str]] = set()
    unique: list[RecoveryFinding] = []
    for finding in findings:
        key = (finding.run_id, finding.category)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique
