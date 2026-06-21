"""Secret redaction tests for artifacts and error surfaces."""

from __future__ import annotations

from loop_pilot.adapters.openai_compatible import OpenAICompatibleAdapter
from loop_pilot.runtime.orchestrator import Orchestrator


def test_orchestrator_redacts_api_key_patterns() -> None:
    raw = "Authorization: Bearer sk-secret123 and api_key=abc"
    redacted = Orchestrator._redact_secrets(raw)
    assert "sk-secret123" not in redacted
    assert "abc" not in redacted
    assert "<redacted>" in redacted


def test_openai_compatible_redacts_bearer_tokens() -> None:
    text = "Error Bearer sk-live-token failed"
    redacted = OpenAICompatibleAdapter._redact(text)
    assert "Bearer sk-live-token" not in redacted
    assert "<redacted>" in redacted


def test_openai_compatible_redacts_response_payload() -> None:
    adapter = OpenAICompatibleAdapter(
        adapter_id="test",
        endpoint="https://example.invalid/v1/chat/completions",
        model="m",
        auth_env=None,
        artifact_dir=__import__("pathlib").Path("."),
    )
    payload = {"usage": {"prompt_tokens": 1}, "model": "m"}
    redacted = adapter._redact_response(payload)
    assert redacted == payload
