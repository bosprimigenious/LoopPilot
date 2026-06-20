"""Legal state transition engine."""

from __future__ import annotations

from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.domain.states import EvaluationVerdict, RunOutcome, RunPhase, is_legal_transition


class StateMachine:
    """Deterministic state machine — only Orchestrator may commit transitions."""

    def validate_transition(self, current: RunPhase, next_phase: RunPhase) -> None:
        if not is_legal_transition(current, next_phase):
            raise LoopPilotError(
                code=ErrorCode.EVALUATION_FAILED,
                component="state_machine",
                message=f"Illegal transition {current.value} -> {next_phase.value}",
                retryable=False,
                state_at_failure=current.value,
            )

    def next_after_evaluation(
        self, verdict: EvaluationVerdict, budget_ok: bool
    ) -> tuple[RunPhase, RunOutcome | None]:
        if verdict == EvaluationVerdict.PASS:
            return RunPhase.FINALIZING, RunOutcome.SUCCEEDED
        if verdict == EvaluationVerdict.FATAL:
            return RunPhase.FINALIZING, RunOutcome.FAILED
        if verdict == EvaluationVerdict.NEEDS_HUMAN:
            return RunPhase.WAITING_APPROVAL, None
        if verdict == EvaluationVerdict.RETRYABLE_FAIL:
            if budget_ok:
                return RunPhase.DIAGNOSING, None
            return RunPhase.FINALIZING, RunOutcome.EXHAUSTED
        return RunPhase.FINALIZING, RunOutcome.FAILED
