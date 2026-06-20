"""MockAdapter tests."""

from __future__ import annotations

from loop_pilot.adapters.mock_adapter import MockAdapter
from loop_pilot.domain.errors import ErrorCode


class TestMockAdapter:
    def test_deterministic_response(self) -> None:
        adapter = MockAdapter()
        r1 = adapter.execute({})
        r2 = adapter.execute({})
        assert r1.status == "success"
        assert r2.status == "success"
        assert adapter.call_count == 2

    def test_timeout_scenario(self) -> None:
        adapter = MockAdapter()
        result = adapter.execute({}, scenario="timeout")
        assert result.status == "timeout"
        assert result.error_code == ErrorCode.MODEL_TIMEOUT.value

    def test_invalid_schema_scenario(self) -> None:
        adapter = MockAdapter()
        result = adapter.execute({}, scenario="invalid_schema")
        assert result.status == "error"
        assert result.error_code == ErrorCode.MODEL_OUTPUT_INVALID.value
