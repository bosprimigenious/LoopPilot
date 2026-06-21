"""Adapter-specific errors."""

from __future__ import annotations

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


class AdapterBlockedError(LoopPilotError):
    """Raised when ModelRouter blocks adapter selection."""

    def __init__(self, role: str, reason: str) -> None:
        super().__init__(
            code=ErrorCode.POLICY_DENIED,
            component="adapter_registry",
            message=f"Role {role} blocked: {reason}",
            retryable=False,
        )
        self.role = role
        self.reason = reason
