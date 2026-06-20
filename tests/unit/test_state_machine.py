"""Unit tests for state machine and domain."""

from __future__ import annotations

import pytest

from loop_pilot.domain.errors import LoopPilotError
from loop_pilot.domain.states import RunOutcome, RunPhase, is_legal_transition
from loop_pilot.runtime.state_machine import StateMachine


class TestStateTransitions:
    def test_created_to_locking_is_legal(self) -> None:
        assert is_legal_transition(RunPhase.CREATED, RunPhase.LOCKING)

    def test_created_to_acting_is_forbidden(self) -> None:
        assert not is_legal_transition(RunPhase.CREATED, RunPhase.ACTING)

    def test_planning_bypass_policy_check_is_forbidden(self) -> None:
        assert not is_legal_transition(RunPhase.PLANNING, RunPhase.ACTING)

    def test_illegal_transition_raises(self) -> None:
        sm = StateMachine()
        with pytest.raises(LoopPilotError):
            sm.validate_transition(RunPhase.CREATED, RunPhase.ACTING)

    def test_phase_and_outcome_are_separate(self) -> None:
        assert RunPhase.TERMINATED.value == "TERMINATED"
        assert RunOutcome.SUCCEEDED.value == "succeeded"
        assert RunPhase.TERMINATED != RunOutcome.SUCCEEDED  # type: ignore[comparison-overlap]
