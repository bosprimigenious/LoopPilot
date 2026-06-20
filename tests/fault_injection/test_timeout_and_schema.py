"""Timeout and invalid schema fault injection tests."""

from __future__ import annotations

import pytest

from loop_pilot.adapters.mock_adapter import MockAdapter
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.domain.schema_validation import validate_against_schema
from loop_pilot.runtime.boundaries import TimeoutBoundary


def test_mock_adapter_timeout_is_not_success() -> None:
    adapter = MockAdapter()
    result = adapter.execute({}, scenario="timeout")
    assert result.status == "timeout"
    assert result.status != "success"
    assert result.error_code == ErrorCode.MODEL_TIMEOUT.value


def test_invalid_schema_output_rejected() -> None:
    adapter = MockAdapter()
    result = adapter.execute({}, scenario="invalid_schema")
    assert result.status == "error"
    with pytest.raises(LoopPilotError) as exc:
        validate_against_schema(
            result.structured_output or {},
            "agent-output.json",
        )
    assert exc.value.code == ErrorCode.MODEL_OUTPUT_INVALID


def test_timeout_boundary_raises() -> None:
    boundary = TimeoutBoundary()

    def slow() -> str:
        import time

        time.sleep(2)
        return "done"

    with pytest.raises(TimeoutError):
        boundary.run(slow, timeout_seconds=0.1)
