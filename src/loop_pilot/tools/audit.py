"""ToolBroker audit records for tool-results.json alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolAuditEntry:
    """Single broker tool invocation audit record."""

    tool: str
    status: str
    duration_ms: int = 0
    policy: str = "allow"
    argv: list[str] | None = None
    path: str | None = None
    url: str | None = None
    cwd: str | None = None
    dry_run: bool = False
    detail: str | None = None
    source_kind: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "event": "tool_call",
            "tool": self.tool,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "policy": self.policy,
        }
        if self.argv is not None:
            payload["argv"] = self.argv
        if self.path is not None:
            payload["path"] = self.path
        if self.url is not None:
            payload["url"] = self.url
        if self.cwd is not None:
            payload["cwd"] = self.cwd
        if self.dry_run:
            payload["dry_run"] = True
        if self.detail:
            payload["detail"] = self.detail
        if self.source_kind:
            payload["source_kind"] = self.source_kind
        return payload


def audit_payload(entries: list[ToolAuditEntry]) -> list[dict[str, Any]]:
    return [entry.to_dict() for entry in entries]
