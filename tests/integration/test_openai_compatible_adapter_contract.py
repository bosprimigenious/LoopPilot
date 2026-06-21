"""OpenAICompatibleAdapter contract tests with mock HTTP."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.adapters.base import AdapterStatus
from loop_pilot.adapters.openai_compatible import OpenAICompatibleAdapter, OpenAICompatibleConfig
from loop_pilot.domain.errors import ErrorCode


def test_openai_compatible_maps_schema_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_http(_payload: dict, _headers: dict) -> dict:
        return {"choices": [{"message": {"content": "not json"}}]}

    config = OpenAICompatibleConfig(
        provider="openai_compatible",
        endpoint="https://example.invalid/v1/chat/completions",
        model="fixture",
        auth_env="LOOPPILOT_TEST_KEY",
    )
    adapter = OpenAICompatibleAdapter.from_config(
        "test-api",
        config,
        tmp_path / "artifacts",
        http_client=fake_http,
    )

    missing = adapter.execute({"messages": []})
    assert missing.status == AdapterStatus.ERROR.value
    assert missing.error_code == ErrorCode.CONFIG_INVALID.value

    monkeypatch.setenv("LOOPPILOT_TEST_KEY", "fixture-key")
    invalid = adapter.execute({"messages": []})
    assert invalid.status == AdapterStatus.ERROR.value
    assert invalid.error_code == ErrorCode.MODEL_OUTPUT_INVALID.value


def test_openai_compatible_success_with_mock_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_http(_payload: dict, _headers: dict) -> dict:
        return {"choices": [{"message": {"content": '{"ok": true}'}}], "usage": {"input_tokens": 1}}

    monkeypatch.setenv("LOOPPILOT_TEST_KEY", "fixture-key")
    config = OpenAICompatibleConfig(
        provider="openai_compatible",
        endpoint="https://example.invalid/v1/chat/completions",
        model="fixture",
        auth_env="LOOPPILOT_TEST_KEY",
    )
    adapter = OpenAICompatibleAdapter.from_config(
        "test-api",
        config,
        tmp_path / "artifacts",
        http_client=fake_http,
    )

    result = adapter.execute({"messages": [{"role": "user", "content": "hi"}]})
    assert result.status == AdapterStatus.SUCCESS.value
    assert result.structured_output == {"ok": True}
