"""MockAdapter — deterministic fixture-based responses."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


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
class AdapterResult:
    status: str
    structured_output: dict[str, Any] | None = None
    duration_ms: int = 0
    error_code: str | None = None
    stdout_artifact: dict[str, Any] | None = None
    stderr_artifact: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "structured_output": self.structured_output,
            "duration_ms": self.duration_ms,
            "error_code": self.error_code,
            "stdout_artifact": self.stdout_artifact,
            "stderr_artifact": self.stderr_artifact,
        }


class MockAdapter:
    """Returns deterministic results from fixture mock_responses."""

    def __init__(self, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = fixture_dir
        self._call_count = 0

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities()

    def healthcheck(self) -> dict[str, str]:
        return {"status": "ok", "adapter": "mock"}

    def reset(self) -> None:
        self._call_count = 0

    def execute(
        self,
        request: dict[str, Any],
        timeout: float | None = None,
        scenario: str = "default",
    ) -> AdapterResult:
        start = time.monotonic()
        self._call_count += 1

        if scenario == "timeout":
            return AdapterResult(status="timeout", duration_ms=int((time.monotonic() - start) * 1000), error_code=ErrorCode.MODEL_TIMEOUT.value)

        if scenario == "invalid_schema":
            return AdapterResult(
                status="error",
                structured_output={"unexpected": True},
                duration_ms=int((time.monotonic() - start) * 1000),
                error_code=ErrorCode.MODEL_OUTPUT_INVALID.value,
            )

        response = self._load_response(scenario)
        duration = int((time.monotonic() - start) * 1000)
        return AdapterResult(
            status=response.get("status", "success"),
            structured_output=response.get("structured_output"),
            duration_ms=duration,
            error_code=response.get("error_code"),
        )

    def _load_response(self, scenario: str) -> dict[str, Any]:
        if self.fixture_dir:
            mock_dir = self.fixture_dir / "mock_responses"
            path = mock_dir / f"{scenario}.json"
            if not path.exists():
                path = mock_dir / "default.json"
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return {"status": "success", "structured_output": {"call_index": self._call_count}}

    def normalize_error(self, error: Exception) -> LoopPilotError:
        return LoopPilotError(
            code=ErrorCode.MODEL_OUTPUT_INVALID,
            component="mock_adapter",
            message=str(error),
            retryable=False,
        )

    @property
    def call_count(self) -> int:
        return self._call_count
