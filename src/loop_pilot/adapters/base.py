"""Shared V1 Adapter contract objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loop_pilot.domain.models import ArtifactReference


class AdapterStatus(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class AdapterCapabilities:
    supports_tools: bool = False
    supports_file_write: bool = False
    supports_structured_output: bool = True
    supports_streaming: bool = False
    supports_dry_run: bool = True
    max_context_tokens: int | None = None
    network_required: bool = False


@dataclass
class AdapterUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "duration_ms": self.duration_ms,
        }


@dataclass
class CostEstimate:
    estimated_cost: float | None = None
    currency: str = "USD"

    def to_dict(self) -> dict[str, Any]:
        return {"estimated_cost": self.estimated_cost, "currency": self.currency}


@dataclass
class HealthStatus:
    status: str
    adapter_id: str
    message: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "adapter_id": self.adapter_id, "message": self.message}


@dataclass
class AdapterResult:
    status: str
    structured_output: dict[str, Any] | None = None
    stdout_artifact: ArtifactReference | None = None
    stderr_artifact: ArtifactReference | None = None
    transcript_artifact: ArtifactReference | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] | AdapterUsage = field(default_factory=dict)
    error_code: str | None = None

    @property
    def duration_ms(self) -> int:
        if isinstance(self.usage, AdapterUsage):
            return self.usage.duration_ms
        return int(self.usage.get("duration_ms", 0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "structured_output": self.structured_output,
            "stdout_artifact": self.stdout_artifact.to_dict() if self.stdout_artifact else None,
            "stderr_artifact": self.stderr_artifact.to_dict() if self.stderr_artifact else None,
            "transcript_artifact": (
                self.transcript_artifact.to_dict() if self.transcript_artifact else None
            ),
            "tool_calls": self.tool_calls,
            "usage": self.usage.to_dict() if isinstance(self.usage, AdapterUsage) else self.usage,
            "duration_ms": self.duration_ms,
            "error_code": self.error_code,
        }


class BaseAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> AdapterCapabilities: ...

    @abstractmethod
    def healthcheck(self) -> HealthStatus | dict[str, str]: ...

    @abstractmethod
    def execute(
        self,
        request: dict[str, Any],
        timeout: float | None = None,
        cancellation: Any | None = None,
    ) -> AdapterResult: ...

    @abstractmethod
    def estimate_cost(self, request: dict[str, Any]) -> CostEstimate | dict[str, Any]: ...

    @abstractmethod
    def normalize_error(self, error: Exception) -> Exception: ...
