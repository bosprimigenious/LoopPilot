"""Adapter doctor — health and readiness diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loop_pilot.adapters.factory import list_adapters
from loop_pilot.adapters.preflight import (
    check_adapter_credentials,
    check_cli_available,
    check_real_adapter_gate,
)
from loop_pilot.adapters.registry import adapter_kind
from loop_pilot.models.router import ModelRouter


@dataclass
class AdapterDiagnosis:
    adapter_id: str
    kind: str
    status: str  # ok | warn | blocked
    message: str
    enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "kind": self.kind,
            "status": self.status,
            "message": self.message,
            "enabled": self.enabled,
        }


def diagnose_adapters(
    models_config: dict[str, Any],
    *,
    allow_real_adapters: bool,
) -> list[AdapterDiagnosis]:
    router = ModelRouter(models_config, allow_real_adapters=allow_real_adapters)
    results: list[AdapterDiagnosis] = []
    for entry in list_adapters(models_config):
        adapter_id = str(entry["id"])
        cfg = router.adapter_config(adapter_id)
        kind = adapter_kind(cfg)
        is_real = bool(entry.get("real"))
        enabled = (not is_real) or allow_real_adapters

        if kind == "mock":
            results.append(
                AdapterDiagnosis(adapter_id, kind, "ok", "MockAdapter always available", enabled)
            )
            continue

        gate = check_real_adapter_gate(kind, allow_real_adapters=allow_real_adapters)
        if gate:
            results.append(AdapterDiagnosis(adapter_id, kind, "blocked", gate, False))
            continue

        cred = check_adapter_credentials(cfg)
        if cred:
            results.append(AdapterDiagnosis(adapter_id, kind, "blocked", cred, True))
            continue

        if kind in {"cli", "cursor_cli"}:
            cli_issue = check_cli_available(cfg)
            if cli_issue:
                results.append(AdapterDiagnosis(adapter_id, kind, "warn", cli_issue, True))
                continue

        results.append(AdapterDiagnosis(adapter_id, kind, "ok", "configured and ready", True))
    return results
