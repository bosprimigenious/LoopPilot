"""Time, round, and model-call budget tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from loop_pilot.domain.models import BudgetSnapshot, RunRecord
from loop_pilot.domain.states import RunOutcome


@dataclass
class BudgetPolicy:
    max_duration_minutes: int = 30
    finalization_reserve_minutes: int = 5
    max_rounds: int = 3
    max_model_calls: int = 8


class BudgetManager:
    def __init__(self, policy: BudgetPolicy) -> None:
        self.policy = policy

    def create_snapshot(self) -> BudgetSnapshot:
        return BudgetSnapshot(
            max_duration_minutes=self.policy.max_duration_minutes,
            max_rounds=self.policy.max_rounds,
            max_model_calls=self.policy.max_model_calls,
            remaining_minutes=float(self.policy.max_duration_minutes),
            remaining_rounds=self.policy.max_rounds,
            remaining_model_calls=self.policy.max_model_calls,
        )

    def compute_deadlines(self, started_at: datetime) -> tuple[str, str]:
        soft = started_at + timedelta(
            minutes=self.policy.max_duration_minutes - self.policy.finalization_reserve_minutes
        )
        hard = started_at + timedelta(minutes=self.policy.max_duration_minutes)
        return soft.isoformat(), hard.isoformat()

    def can_start_acting(self, record: RunRecord, now: datetime | None = None) -> bool:
        if record.budgets.remaining_rounds <= 0:
            return False
        if record.budgets.remaining_model_calls <= 0:
            return False
        if record.soft_deadline_at:
            now = now or datetime.now(timezone.utc)
            soft = datetime.fromisoformat(record.soft_deadline_at)
            if now >= soft:
                return False
        return True

    def can_retry(self, record: RunRecord) -> bool:
        return record.budgets.remaining_rounds > 0 and record.budgets.remaining_model_calls > 0

    def consume_round(self, record: RunRecord) -> None:
        record.budgets.rounds_used += 1
        record.budgets.remaining_rounds = max(
            0, record.budgets.max_rounds - record.budgets.rounds_used
        )
        record.current_round = record.budgets.rounds_used

    def consume_model_call(self, record: RunRecord) -> None:
        record.budgets.model_calls_used += 1
        record.budgets.remaining_model_calls = max(
            0, record.budgets.max_model_calls - record.budgets.model_calls_used
        )

    def check_exhausted(self, record: RunRecord, now: datetime | None = None) -> RunOutcome | None:
        now = now or datetime.now(timezone.utc)
        if record.hard_deadline_at:
            hard = datetime.fromisoformat(record.hard_deadline_at)
            if now >= hard:
                return RunOutcome.EXHAUSTED
        if record.budgets.remaining_rounds <= 0 or record.budgets.remaining_model_calls <= 0:
            return RunOutcome.EXHAUSTED
        if record.soft_deadline_at:
            soft = datetime.fromisoformat(record.soft_deadline_at)
            if now >= soft:
                return RunOutcome.PARTIAL
        return None
