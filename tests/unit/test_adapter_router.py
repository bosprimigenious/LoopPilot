"""ModelRouter adapter selection tests."""

from __future__ import annotations

from loop_pilot.adapters.factory import create_adapter
from loop_pilot.models.router import ModelRouter


def test_router_selects_mock_when_real_adapters_disabled() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["cursor_cli"],
                    "require": {"file_write": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "cursor_cli": {"kind": "cursor_cli", "command": ["echo"]},
            },
        },
        allow_real_adapters=False,
    )
    adapter = create_adapter(router, "coding_agent")
    assert adapter.__class__.__name__ == "MockAdapter"


def test_router_selects_real_adapter_when_enabled() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["cursor_cli"],
                    "require": {"file_write": True, "tool_calls": True, "dry_run": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "cursor_cli": {
                    "kind": "cursor_cli",
                    "command": ["echo"],
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
    assert decision.adapter_id == "cursor_cli"
