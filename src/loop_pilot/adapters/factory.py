"""Unified adapter registry and factory for 0.3 routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loop_pilot.adapters.cursor_cli import CursorCLIAdapter
from loop_pilot.adapters.errors import AdapterBlockedError
from loop_pilot.adapters.mock_adapter import MockAdapter
from loop_pilot.adapters.openai_compatible import OpenAICompatibleAdapter, OpenAICompatibleConfig
from loop_pilot.adapters.preflight import validate_adapter_run
from loop_pilot.adapters.registry import adapter_kind, assert_real_adapters_allowed, is_real_adapter_kind
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.models.router import ModelRouter, RouterDecision


def create_adapter(
    router: ModelRouter,
    role: str,
    *,
    fixture_dir: Path | None = None,
    artifact_dir: Path | None = None,
    data_class: str = "PROJECT",
    adapter_override: str | None = None,
) -> MockAdapter | CursorCLIAdapter | OpenAICompatibleAdapter:
    """Resolve role via ModelRouter and instantiate the selected adapter."""
    if adapter_override:
        adapter_config = router.adapter_config(adapter_override)
        kind = adapter_kind(adapter_config)
        if is_real_adapter_kind(kind) and not router.allow_real_adapters:
            raise AdapterBlockedError(role, f"adapter {adapter_override} blocked by allow_real_adapters=false")
        validate_adapter_run(
            adapter_override,
            adapter_config,
            allow_real_adapters=router.allow_real_adapters,
        )
        return build_adapter(
            adapter_override,
            adapter_config,
            fixture_dir=fixture_dir,
            artifact_dir=artifact_dir,
            allow_real_adapters=router.allow_real_adapters,
        )

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
) -> MockAdapter | CursorCLIAdapter | OpenAICompatibleAdapter:
    kind = adapter_kind(adapter_config)
    if kind == "mock" or adapter_id == "mock":
        return MockAdapter(fixture_dir)
    assert_real_adapters_allowed(kind, allow_real_adapters)
    if kind in {"cli", "cursor_cli"}:
        command = adapter_config.get("command")
        if not isinstance(command, list) or not command:
            raise LoopPilotError(
                code=ErrorCode.CONFIG_INVALID,
                component="adapter_factory",
                message=f"CLI adapter {adapter_id} missing command array",
            )
        worktree = fixture_dir or Path(".")
        timeout = float(adapter_config.get("timeout_seconds", 900))
        return CursorCLIAdapter(
            adapter_id=adapter_id,
            command=command,
            approved_worktree=worktree,
            artifact_dir=artifact_dir or Path("var/artifacts"),
            timeout_seconds=timeout,
            env_allowlist=list(adapter_config.get("env_allowlist", [])),
        )
    if kind in {"api", "openai_compatible"}:
        config = OpenAICompatibleConfig(
            provider=str(adapter_config.get("provider", "openai_compatible")),
            endpoint=str(adapter_config.get("endpoint", "")),
            model=str(adapter_config.get("model", "")),
            auth_env=adapter_config.get("auth_env"),
            timeout_seconds=int(adapter_config.get("timeout_seconds", 60)),
        )
        return OpenAICompatibleAdapter.from_config(
            adapter_id,
            config,
            artifact_dir or Path("var/artifacts"),
        )
    return MockAdapter(fixture_dir)


def resolve_or_block(router: ModelRouter, role: str, *, data_class: str = "PROJECT") -> RouterDecision:
    """Return routing decision; callers treat blocked=True as run-level BLOCKED."""
    return router.resolve_role(role, data_class=data_class)


def list_adapters(models_config: dict[str, Any]) -> list[dict[str, Any]]:
    adapters = models_config.get("adapters", {})
    entries: list[dict[str, Any]] = []
    for adapter_id, cfg in adapters.items():
        kind = adapter_kind(cfg if isinstance(cfg, dict) else {})
        entries.append(
            {
                "id": adapter_id,
                "kind": kind,
                "real": is_real_adapter_kind(kind),
                "timeout_seconds": (cfg or {}).get("timeout_seconds"),
            }
        )
    return entries
