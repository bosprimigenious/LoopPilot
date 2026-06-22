"""Append-only SafetyGate audit log."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from loop_pilot.domain.models import rfc3339


@dataclass
class GateAuditRecord:
    gate_id: str
    action: str
    decision: str
    reason_code: str
    timestamp: str
    config_hash: str
    operator: str
    message: str = ""
    context: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload.get("context") is None:
            payload.pop("context", None)
        return payload


class AuditLog:
    def __init__(self, audit_dir: Path) -> None:
        self.audit_dir = audit_dir
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.audit_dir / "gate_decisions.jsonl"

    def append(
        self,
        *,
        action: str,
        decision: str,
        reason_code: str,
        config_hash: str,
        operator: str = "cli",
        message: str = "",
        context: dict[str, Any] | None = None,
    ) -> GateAuditRecord:
        record = GateAuditRecord(
            gate_id=str(uuid.uuid4()),
            action=action,
            decision=decision,
            reason_code=reason_code,
            timestamp=rfc3339(),
            config_hash=config_hash[:16],
            operator=operator,
            message=message,
            context=context,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        return record

    def list_recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()[-limit:] if line.strip()]
