"""Adapter creation with Mini safety guard for real integrations."""

from __future__ import annotations

from typing import Any

from loop_pilot.domain.errors import ErrorCode, LoopPilotError

REAL_ADAPTER_KINDS = frozenset({"cli", "api"})


def adapter_kind(adapter_config: dict[str, Any]) -> str:
    return str(adapter_config.get("kind", "mock")).lower()


def is_real_adapter_kind(kind: str) -> bool:
    return kind in REAL_ADAPTER_KINDS


def assert_real_adapters_allowed(kind: str, allow_real_adapters: bool) -> None:
    if is_real_adapter_kind(kind) and not allow_real_adapters:
        raise LoopPilotError(
            code=ErrorCode.POLICY_DENIED,
            component="adapter_registry",
            message=(
                "Real model adapters are disabled by runtime.allow_real_adapters=false. "
                "Mini defaults to MockAdapter only; set runtime.allow_real_adapters: true "
                "explicitly to enable CLI/API adapters."
            ),
            recommended_action="Use mock adapter or enable runtime.allow_real_adapters in config.",
        )


def validate_adapter_config(adapter_id: str, adapter_config: dict[str, Any], allow_real_adapters: bool) -> None:
    kind = adapter_kind(adapter_config)
    if kind == "mock":
        return
    assert_real_adapters_allowed(kind, allow_real_adapters)
    if adapter_id == "mock":
        return
    if not adapter_config:
        raise LoopPilotError(
            code=ErrorCode.CONFIG_INVALID,
            component="adapter_registry",
            message=f"Adapter not configured: {adapter_id}",
        )
