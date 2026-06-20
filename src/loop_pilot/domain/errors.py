"""Stable error taxonomy for LoopPilot Mini."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    CONFIG_INVALID = "CONFIG_INVALID"
    CONTEXT_MISSING = "CONTEXT_MISSING"
    MODEL_RATE_LIMIT = "MODEL_RATE_LIMIT"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_OUTPUT_INVALID = "MODEL_OUTPUT_INVALID"
    TOOL_FAILED = "TOOL_FAILED"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    POLICY_DENIED = "POLICY_DENIED"
    EVALUATION_FAILED = "EVALUATION_FAILED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_SCHEMA_CHANGED = "SOURCE_SCHEMA_CHANGED"
    STORAGE_FAILED = "STORAGE_FAILED"
    WORKSPACE_CHANGED = "WORKSPACE_CHANGED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    REPORT_RENDER_FAILED = "REPORT_RENDER_FAILED"


RETRYABLE_CODES: frozenset[ErrorCode] = frozenset(
    {
        ErrorCode.MODEL_RATE_LIMIT,
        ErrorCode.MODEL_TIMEOUT,
        ErrorCode.MODEL_OUTPUT_INVALID,
        ErrorCode.TOOL_FAILED,
        ErrorCode.TOOL_TIMEOUT,
        ErrorCode.EVALUATION_FAILED,
    }
)


@dataclass
class LoopPilotError(Exception):
    code: ErrorCode
    component: str
    message: str
    retryable: bool = False
    attempt: int = 1
    evidence: list[dict[str, Any]] = field(default_factory=list)
    state_at_failure: str | None = None
    recommended_action: str = ""
    caused_by: str | None = None

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.component}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_id": f"{self.code.value}-{self.component}-{self.attempt}",
            "code": self.code.value,
            "component": self.component,
            "message": self.message,
            "retryable": self.retryable,
            "attempt": self.attempt,
            "evidence": self.evidence,
            "state_at_failure": self.state_at_failure,
            "recommended_action": self.recommended_action,
            "caused_by": self.caused_by,
        }
