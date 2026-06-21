"""Summary data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loop_pilot.tasks.models import InboxItem, QueueItem


@dataclass
class RunSummaryRow:
    run_id: str
    loop_type: str
    outcome: str | None
    phase: str
    gate: str | None
    report_path: str | None


@dataclass
class ReviewSummaryRow:
    run_id: str
    loop_type: str
    reason: str
    suggested_command: str


@dataclass
class BlockedSummaryRow:
    run_id: str
    loop_type: str
    reason: str


@dataclass
class DailySummaryData:
    date: str
    timezone: str
    highlights: list[str] = field(default_factory=list)
    today_items: list[QueueItem] = field(default_factory=list)
    runs: list[RunSummaryRow] = field(default_factory=list)
    needs_review: list[ReviewSummaryRow] = field(default_factory=list)
    inbox_new: list[InboxItem] = field(default_factory=list)
    inbox_daily_news: list[InboxItem] = field(default_factory=list)
    queue_items: list[QueueItem] = field(default_factory=list)
    blocked: list[BlockedSummaryRow] = field(default_factory=list)
    tomorrow: list[str] = field(default_factory=list)
    recovery_findings: list[str] = field(default_factory=list)


@dataclass
class WeeklySummaryData:
    week: str
    start_date: str
    end_date: str
    highlights: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    loop_stats: dict[str, Any] = field(default_factory=dict)
    recommended: list[str] = field(default_factory=list)
    daily_paths: list[str] = field(default_factory=list)


@dataclass
class SummaryRecord:
    id: str
    summary_type: str
    summary_date: str
    path: str
    status: str
    run_count: int = 0
    review_count: int = 0
    blocked_count: int = 0
    inbox_count: int = 0
    created_at: str = ""
    updated_at: str = ""
