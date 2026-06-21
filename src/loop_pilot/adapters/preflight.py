"""Adapter preflight checks before real adapter invocation."""

from __future__ import annotations

import os
import shutil
from typing import Any

from loop_pilot.adapters.errors import AdapterBlockedError
from loop_pilot.adapters.registry import adapter_kind, assert_real_adapters_allowed, is_real_adapter_kind
from loop_pilot.domain.errors import LoopPilotError


def check_real_adapter_gate(kind: str, *, allow_real_adapters: bool) -> str | None:
    """Return block reason when real adapters are disabled, else None."""
    if is_real_adapter_kind(kind) and not allow_real_adapters:
        return "real adapters disabled (runtime.allow_real_adapters=false)"
    return None


def check_adapter_credentials(adapter_config: dict[str, Any]) -> str | None:
    """Return block reason when required API key env is missing, else None."""
    auth_env = adapter_config.get("auth_env")
    if auth_env and not os.environ.get(str(auth_env)):
        return f"missing API key ({auth_env} not set)"
    return None


def check_cli_available(adapter_config: dict[str, Any]) -> str | None:
    """Return warn/block reason when CLI binary is missing, else None."""
    command = adapter_config.get("command")
    if not isinstance(command, list) or not command:
        return "CLI command not configured"
    binary = str(command[0])
    if shutil.which(binary) is None:
        return f"CLI not found in PATH: {binary}"
    return None


def validate_adapter_run(
    adapter_id: str,
    adapter_config: dict[str, Any],
    *,
    allow_real_adapters: bool,
) -> None:
    """Raise AdapterBlockedError when adapter must not run."""
    kind = adapter_kind(adapter_config)
    gate = check_real_adapter_gate(kind, allow_real_adapters=allow_real_adapters)
    if gate:
        raise AdapterBlockedError("adapter", f"{adapter_id}: {gate}")
    try:
        assert_real_adapters_allowed(kind, allow_real_adapters)
    except LoopPilotError as exc:
        raise AdapterBlockedError("adapter", f"{adapter_id}: {exc.message}") from exc
    if not is_real_adapter_kind(kind):
        return
    cred = check_adapter_credentials(adapter_config)
    if cred:
        raise AdapterBlockedError("adapter", f"{adapter_id}: {cred}")
