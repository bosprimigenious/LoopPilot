"""Tests for runtime.allow_real_adapters safety switch."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.adapters.registry import assert_real_adapters_allowed
from loop_pilot.config import default_config_dict, load_config
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.models.router import ModelRouter


def test_default_config_disallows_real_adapters() -> None:
    runtime = default_config_dict()["runtime"]
    assert runtime["allow_real_adapters"] is False


def test_assert_real_adapters_allowed_blocks_cli_and_api() -> None:
    with pytest.raises(LoopPilotError) as exc:
        assert_real_adapters_allowed("cli", allow_real_adapters=False)
    assert exc.value.code == ErrorCode.POLICY_DENIED
    assert "allow_real_adapters" in exc.value.message


def test_model_router_blocks_real_adapters_by_default() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["configured_coding_cli", "mock"],
                    "require": {"file_write": True, "tool_calls": True, "dry_run": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "configured_coding_cli": {
                    "kind": "cli",
                    "capabilities": {
                        "supports_file_write": True,
                        "supports_tools": True,
                        "supports_dry_run": True,
                    },
                },
                "mock": {
                    "kind": "mock",
                    "capabilities": {
                        "supports_file_write": False,
                        "supports_tools": False,
                        "supports_dry_run": True,
                    },
                },
            },
        },
        allow_real_adapters=False,
    )

    decision = router.resolve_role("coding_agent")

    assert decision.blocked is True
    assert decision.adapter_id is None
    assert "allow_real_adapters" in decision.excluded["configured_coding_cli"][0]


def test_model_router_allows_real_adapters_when_enabled() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["configured_coding_cli"],
                    "require": {"file_write": True, "tool_calls": True, "dry_run": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "configured_coding_cli": {
                    "kind": "cli",
                    "capabilities": {
                        "supports_file_write": True,
                        "supports_tools": True,
                        "supports_dry_run": True,
                    },
                },
            },
        },
        allow_real_adapters=True,
    )

    decision = router.resolve_role("coding_agent")
    assert decision.blocked is False
    assert decision.adapter_id == "configured_coding_cli"


def test_create_adapter_uses_mock_when_real_adapters_disabled(tmp_path: Path) -> None:
    from loop_pilot.adapters.factory import create_adapter

    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["configured_coding_cli"],
                    "require": {"file_write": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "configured_coding_cli": {"kind": "cli", "command": ["echo", "hi"]},
            },
        },
        allow_real_adapters=False,
    )
    adapter = create_adapter(router, "coding_agent", fixture_dir=tmp_path)
    assert adapter.__class__.__name__ == "MockAdapter"


def test_load_config_reads_allow_real_adapters(tmp_path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "runtime:\n  allow_real_adapters: false\n  state_backend: json\n",
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")

    cfg = load_config(config_dir)
    assert cfg.allow_real_adapters is False
