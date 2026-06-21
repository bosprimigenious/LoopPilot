"""Adapter gating tests for 0.3 safety layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.adapters.errors import AdapterBlockedError
from loop_pilot.adapters.factory import create_adapter
from loop_pilot.adapters.preflight import check_real_adapter_gate, validate_adapter_run
from loop_pilot.models.router import ModelRouter


def test_real_adapter_gate_blocks_by_default() -> None:
    reason = check_real_adapter_gate("cursor_cli", allow_real_adapters=False)
    assert reason is not None
    assert "allow_real_adapters=false" in reason


def test_create_adapter_override_blocked_when_real_disabled(tmp_path: Path) -> None:
    router = ModelRouter(
        {
            "adapters": {
                "cursor_cli": {
                    "kind": "cursor_cli",
                    "command": ["echo", "hi"],
                    "capabilities": {
                        "supports_file_write": True,
                        "supports_tools": True,
                        "supports_dry_run": True,
                    },
                },
            },
        },
        allow_real_adapters=False,
    )
    with pytest.raises(AdapterBlockedError) as exc:
        create_adapter(
            router,
            "coding_agent",
            fixture_dir=tmp_path,
            adapter_override="cursor_cli",
        )
    assert "allow_real_adapters=false" in exc.value.message


def test_validate_adapter_run_blocks_missing_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    cfg = {
        "kind": "openai_compatible",
        "endpoint": "https://example.invalid/v1/chat/completions",
        "model": "deepseek-chat",
        "auth_env": "DEEPSEEK_API_KEY",
    }
    with pytest.raises(AdapterBlockedError) as exc:
        validate_adapter_run("deepseek", cfg, allow_real_adapters=True)
    assert "missing API key" in exc.value.message
