"""Unified adapter registry and factory for V1 routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loop_pilot.adapters.api_model import APIModelAdapter, APIModelConfig
from loop_pilot.adapters.coding_cli import CodingCLIAdapter
from loop_pilot.adapters.mock_adapter import MockAdapter
from loop_pilot.adapters.registry import adapter_kind, assert_real_adapters_allowed
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.models.router import ModelRouter, RouterDecision


class AdapterBlockedError(LoopPilotError):
    def __init__(self, role: str, reason: str) -> None:
        super().__init__(
            code=ErrorCode.POLICY_DENIED,
            component="adapter_factory",
            message=f"Role {role} blocked: {reason}",
            retryable=False,
        )
        self.role = role
        self.reason = reason


def create_adapter(
    router: ModelRouter,
    role: str,
    *,
    fixture_dir: Path | None = None,
    artifact_dir: Path | None = None,
    data_class: str = "PROJECT",
) -> MockAdapter | CodingCLIAdapter | APIModelAdapter:
    """Resolve role via ModelRouter and instantiate the selected adapter."""
    if not router.allow_real_adapters:
        return MockAdapter(fixture_dir)
    decision = router.resolve_role(role, data_class=data_class)
    if decision.blocked or decision.adapter_id is None:
        raise AdapterBlockedError(role, decision.reason or "no capable adapter")
    return build_adapter(
        decision.adapter_id,
        router.adapter_config(decision.adapter_id),
        fixture_dir=fixture_dir,
        artifact_dir=artifact_dir,
        allow_real_adapters=router.allow_real_adapters,
    )


def build_adapter(
    adapter_id: str,
    adapter_config: dict[str, Any],
    *,
    fixture_dir: Path | None = None,
    artifact_dir: Path | None = None,
    allow_real_adapters: bool = False,
) -> MockAdapter | CodingCLIAdapter | APIModelAdapter:
    kind = adapter_kind(adapter_config)
    if kind == "mock" or adapter_id == "mock":
        return MockAdapter(fixture_dir)
    assert_real_adapters_allowed(kind, allow_real_adapters)
    if kind == "cli":
        command = adapter_config.get("command")
        if not isinstance(command, list) or not command:
            raise LoopPilotError(
                code=ErrorCode.CONFIG_INVALID,
                component="adapter_factory",
                message=f"CLI adapter {adapter_id} missing command array",
            )
        worktree = fixture_dir or Path(".")
        return CodingCLIAdapter(
            adapter_id=adapter_id,
            command=command,
            approved_worktree=worktree,
            artifact_dir=artifact_dir or Path("var/artifacts"),
            env_allowlist=list(adapter_config.get("env_allowlist", [])),
        )
    if kind == "api":
        config = APIModelConfig(
            provider=str(adapter_config.get("provider", "openai_compatible")),
            endpoint=str(adapter_config.get("endpoint", "")),
            model=str(adapter_config.get("model", "")),
            auth_env=str(adapter_config.get("auth_env", "")),
        )
        return APIModelAdapter.from_config(
            adapter_id,
            config,
            artifact_dir or Path("var/artifacts"),
        )
    return MockAdapter(fixture_dir)


def resolve_or_block(router: ModelRouter, role: str, *, data_class: str = "PROJECT") -> RouterDecision:
    """Return routing decision; callers treat blocked=True as run-level BLOCKED."""
    return router.resolve_role(role, data_class=data_class)
