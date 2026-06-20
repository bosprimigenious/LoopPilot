"""Budget manager tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy


class TestBudgetManager:
    def test_exhausted_when_rounds_depleted(self) -> None:
        mgr = BudgetManager(BudgetPolicy(max_rounds=1))
        record = RunRecord(run_id="test-001", loop_type="intern")
        record.budgets = mgr.create_snapshot()
        mgr.consume_round(record)
        assert record.budgets.remaining_rounds == 0
        outcome = mgr.check_exhausted(record)
        assert outcome == RunOutcome.EXHAUSTED

    def test_soft_deadline_produces_partial(self) -> None:
        mgr = BudgetManager(BudgetPolicy())
        started = datetime.now(timezone.utc) - timedelta(minutes=27)
        record = RunRecord(run_id="test-002", loop_type="intern")
        soft, hard = mgr.compute_deadlines(started)
        record.soft_deadline_at = soft
        record.hard_deadline_at = hard
        outcome = mgr.check_exhausted(record)
        assert outcome == RunOutcome.PARTIAL
