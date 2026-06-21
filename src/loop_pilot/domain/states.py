"""RunPhase and RunOutcome — separate types with legal transitions."""

from __future__ import annotations

from enum import Enum


class RunPhase(str, Enum):
    CREATED = "CREATED"
    LOCKING = "LOCKING"
    OBSERVING = "OBSERVING"
    SELECTING = "SELECTING"
    PLANNING = "PLANNING"
    POLICY_CHECK = "POLICY_CHECK"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    ACTING = "ACTING"
    EVALUATING = "EVALUATING"
    DIAGNOSING = "DIAGNOSING"
    REFLECTING = "REFLECTING"
    REPLANNING = "REPLANNING"
    FINALIZING = "FINALIZING"
    PERSISTING = "PERSISTING"
    REPORTING = "REPORTING"
    TERMINATED = "TERMINATED"


class RunOutcome(str, Enum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    NO_ACTION = "no_action"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    FAILED = "failed"
    EXHAUSTED = "exhausted"
    CANCELLED = "cancelled"


class EvaluationVerdict(str, Enum):
    PASS = "pass"
    RETRYABLE_FAIL = "retryable_fail"
    NEEDS_HUMAN = "needs_human"
    FATAL = "fatal"


class RoundDecision(str, Enum):
    PASS = "pass"
    RETRY = "retry"
    HUMAN = "human"
    STOP = "stop"


# Legal transitions: current_phase -> list of allowed next phases
LEGAL_TRANSITIONS: dict[RunPhase, frozenset[RunPhase]] = {
    RunPhase.CREATED: frozenset({RunPhase.LOCKING, RunPhase.FINALIZING}),
    RunPhase.LOCKING: frozenset({RunPhase.OBSERVING, RunPhase.FINALIZING}),
    RunPhase.OBSERVING: frozenset({RunPhase.SELECTING, RunPhase.FINALIZING}),
    RunPhase.SELECTING: frozenset({RunPhase.PLANNING, RunPhase.FINALIZING}),
    RunPhase.PLANNING: frozenset({RunPhase.POLICY_CHECK, RunPhase.FINALIZING}),
    RunPhase.POLICY_CHECK: frozenset(
        {RunPhase.ACTING, RunPhase.WAITING_APPROVAL, RunPhase.FINALIZING}
    ),
    RunPhase.WAITING_APPROVAL: frozenset({RunPhase.ACTING, RunPhase.FINALIZING}),
    RunPhase.ACTING: frozenset({RunPhase.EVALUATING, RunPhase.DIAGNOSING, RunPhase.FINALIZING}),
    RunPhase.EVALUATING: frozenset(
        {RunPhase.FINALIZING, RunPhase.DIAGNOSING, RunPhase.WAITING_APPROVAL}
    ),
    RunPhase.DIAGNOSING: frozenset({RunPhase.REFLECTING, RunPhase.FINALIZING}),
    RunPhase.REFLECTING: frozenset({RunPhase.REPLANNING, RunPhase.FINALIZING}),
    RunPhase.REPLANNING: frozenset({RunPhase.POLICY_CHECK, RunPhase.FINALIZING}),
    RunPhase.FINALIZING: frozenset({RunPhase.PERSISTING}),
    RunPhase.PERSISTING: frozenset({RunPhase.REPORTING}),
    RunPhase.REPORTING: frozenset({RunPhase.TERMINATED, RunPhase.WAITING_APPROVAL}),
    RunPhase.TERMINATED: frozenset(),
}

FORBIDDEN_TRANSITIONS: frozenset[tuple[RunPhase, RunPhase]] = frozenset(
    {
        (RunPhase.CREATED, RunPhase.ACTING),
        (RunPhase.PLANNING, RunPhase.ACTING),
        (RunPhase.ACTING, RunPhase.TERMINATED),
    }
)


def is_legal_transition(current: RunPhase, next_phase: RunPhase) -> bool:
    if (current, next_phase) in FORBIDDEN_TRANSITIONS:
        return False
    allowed = LEGAL_TRANSITIONS.get(current, frozenset())
    return next_phase in allowed
