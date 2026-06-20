"""Deterministic model routing — not an Agent."""

from __future__ import annotations

from typing import Any


class ModelRouter:
    """Selects configured adapter ids by role without model reasoning."""

    def __init__(self, models_config: dict[str, Any]) -> None:
        self.roles = models_config.get("roles", {})
        self.adapters = models_config.get("adapters", {})

    def resolve(self, role: str) -> str:
        role_cfg = self.roles.get(role, {})
        adapter_id = role_cfg.get("adapter", "mock")
        if adapter_id not in self.adapters and adapter_id != "mock":
            return "mock"
        return adapter_id

    def adapter_config(self, adapter_id: str) -> dict[str, Any]:
        return self.adapters.get(adapter_id, {"kind": "mock", "timeout_seconds": 60})
