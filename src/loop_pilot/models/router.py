"""Deterministic model routing — not an Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loop_pilot.adapters.registry import adapter_kind, is_real_adapter_kind


DATA_CLASS_ORDER = {"PUBLIC": 0, "PROJECT": 1, "SENSITIVE": 2, "SECRET": 3}


@dataclass
class RouterDecision:
    role: str
    adapter_id: str | None
    blocked: bool = False
    reason: str = ""
    excluded: dict[str, list[str]] = field(default_factory=dict)
    fallback_used: bool = False


class ModelRouter:
    """Selects configured adapter ids by role without model reasoning."""

    def __init__(self, models_config: dict[str, Any], *, allow_real_adapters: bool = False) -> None:
        self.roles = models_config.get("roles", {})
        self.model_roles = models_config.get("model_roles", {})
        self.adapters = models_config.get("adapters", {})
        self.allow_real_adapters = allow_real_adapters

    def resolve(self, role: str) -> str:
        role_cfg = self.roles.get(role, {})
        adapter_id = role_cfg.get("adapter", "mock")
        adapter = self.adapters.get(adapter_id, {"kind": "mock"})
        kind = adapter_kind(adapter)
        if is_real_adapter_kind(kind) and not self.allow_real_adapters:
            return "mock"
        if adapter_id not in self.adapters and adapter_id != "mock":
            return "mock"
        return adapter_id

    def adapter_config(self, adapter_id: str) -> dict[str, Any]:
        return self.adapters.get(adapter_id, {"kind": "mock", "timeout_seconds": 60})

    def resolve_role(self, role: str, data_class: str = "PROJECT") -> RouterDecision:
        role_cfg = self.model_roles.get(role)
        if role_cfg is None:
            adapter_id = self.resolve(role)
            blocked, reason = self._real_adapter_block(adapter_id)
            return RouterDecision(role=role, adapter_id=adapter_id, blocked=blocked, reason=reason)

        excluded: dict[str, list[str]] = {}
        require = role_cfg.get("require", {})
        candidates = role_cfg.get("candidates", [])
        for index, adapter_id in enumerate(candidates):
            adapter = self.adapters.get(adapter_id)
            if adapter is None:
                excluded[adapter_id] = ["adapter not configured"]
                continue
            real_block = self._real_adapter_block(adapter_id, adapter)
            if real_block[0]:
                excluded[adapter_id] = [real_block[1]]
                continue
            reasons = self._exclusion_reasons(adapter, require, data_class)
            if reasons:
                excluded[adapter_id] = reasons
                continue
            return RouterDecision(
                role=role,
                adapter_id=adapter_id,
                excluded=excluded,
                fallback_used=index > 0,
            )

        no_capable = role_cfg.get("no_capable_adapter", "block")
        return RouterDecision(
            role=role,
            adapter_id=None,
            blocked=True,
            reason=f"no_capable_adapter: {no_capable}",
            excluded=excluded,
        )

    def _real_adapter_block(
        self, adapter_id: str, adapter: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        adapter = adapter if adapter is not None else self.adapters.get(adapter_id, {"kind": "mock"})
        kind = adapter_kind(adapter)
        if is_real_adapter_kind(kind) and not self.allow_real_adapters:
            return True, (
                "runtime.allow_real_adapters=false blocks real adapters in Mini; "
                "enable explicitly to use CLI/API adapters"
            )
        return False, ""

    def _exclusion_reasons(
        self,
        adapter: dict[str, Any],
        require: dict[str, Any],
        data_class: str,
    ) -> list[str]:
        reasons: list[str] = []
        capabilities = adapter.get("capabilities", {})
        capability_map = {
            "file_write": "supports_file_write",
            "tool_calls": "supports_tools",
            "tools": "supports_tools",
            "structured_output": "supports_structured_output",
            "dry_run": "supports_dry_run",
        }
        for required_name, required_value in require.items():
            if required_name == "min_context_tokens":
                min_tokens = int(required_value)
                max_tokens = int(capabilities.get("max_context_tokens", 0))
                if max_tokens < min_tokens:
                    reasons.append(f"context window {max_tokens} below required {min_tokens}")
                continue
            if required_value is not True:
                continue
            capability_name = capability_map.get(required_name, required_name)
            if capabilities.get(capability_name) is not True:
                reasons.append(f"missing {required_name}")

        health = adapter.get("health", {})
        if health.get("status") == "unhealthy":
            reasons.append("adapter unhealthy")

        if data_class == "SECRET":
            reasons.append("SECRET data is never routed to models")
        else:
            max_class = adapter.get("data_policy", {}).get("max_data_class", "PROJECT")
            if DATA_CLASS_ORDER.get(data_class, 1) > DATA_CLASS_ORDER.get(max_class, 1):
                reasons.append(f"data class {data_class} exceeds adapter policy {max_class}")
        return reasons
