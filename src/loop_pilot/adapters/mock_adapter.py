"""MockAdapter — deterministic fixture-based responses."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from loop_pilot.adapters.base import AdapterCapabilities, AdapterResult, AdapterStatus
from loop_pilot.domain.errors import ErrorCode, LoopPilotError


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
            return AdapterResult(
                status=AdapterStatus.TIMEOUT.value,
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
                error_code=ErrorCode.MODEL_TIMEOUT.value,
            )

        if scenario == "invalid_schema":
            return AdapterResult(
                status=AdapterStatus.ERROR.value,
                structured_output={"unexpected": True},
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
                error_code=ErrorCode.MODEL_OUTPUT_INVALID.value,
            )

        if scenario == "cancelled":
            return AdapterResult(
                status=AdapterStatus.CANCELLED.value,
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
                error_code=ErrorCode.TOOL_FAILED.value,
            )

        if scenario == "rate_limit":
            return AdapterResult(
                status=AdapterStatus.ERROR.value,
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
                error_code=ErrorCode.MODEL_RATE_LIMIT.value,
            )

        if scenario == "refusal":
            return AdapterResult(
                status=AdapterStatus.ERROR.value,
                structured_output={"refusal": True},
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
                error_code=ErrorCode.POLICY_DENIED.value,
            )

        if scenario == "dry_run" or request.get("dry_run"):
            return AdapterResult(
                status=AdapterStatus.SUCCESS.value,
                structured_output={"dry_run": True, "call_index": self._call_count},
                usage={"duration_ms": int((time.monotonic() - start) * 1000), "input_tokens": 0, "output_tokens": 0},
            )

        if scenario == "redaction":
            return AdapterResult(
                status=AdapterStatus.SUCCESS.value,
                structured_output={"secret": "<redacted>", "call_index": self._call_count},
                usage={"duration_ms": int((time.monotonic() - start) * 1000), "cost": 0.0},
            )

        response = self._load_response(scenario)
        duration = int((time.monotonic() - start) * 1000)
        return AdapterResult(
            status=response.get("status", "success"),
            structured_output=response.get("structured_output"),
            usage={"duration_ms": duration},
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
