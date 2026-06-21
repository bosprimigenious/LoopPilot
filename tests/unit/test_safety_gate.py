"""Unit tests for SafetyGate v1."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.config import LoopPilotConfig
from loop_pilot.safety.audit import AuditLog
from loop_pilot.safety.gate import SafetyGate
from loop_pilot.safety.levels import SafetyLevel
from loop_pilot.safety.policy import SafeAutonomyPolicy
from loop_pilot.safety.readiness import PREP_STAGE_BLOCKED


def _gate(*, allow_install: bool = False, tmp_path: Path) -> SafetyGate:
    return SafetyGate.from_config(
        LoopPilotConfig(
            runtime={"state_dir": str(tmp_path / "state")},
            schedule={"allow_install": allow_install},
            safety={"max_level": 3},
            config_dir=tmp_path / "config",
        )
    )


def test_schedule_install_denied_by_default(tmp_path: Path) -> None:
    result = _gate(tmp_path=tmp_path).check("schedule.install", confirm=True)
    assert result.denied and result.reason_code == PREP_STAGE_BLOCKED


def test_schedule_install_allowed_with_policy(tmp_path: Path) -> None:
    gate = _gate(allow_install=True, tmp_path=tmp_path)
    cfg = LoopPilotConfig(
        runtime={"state_dir": str(tmp_path / "state")},
        schedule={"allow_install": True},
        safety={"stage": "ready", "max_level": 3},
        config_dir=tmp_path / "config",
    )
    gate = SafetyGate.from_config(cfg)
    result = gate.check("schedule.install", confirm=True)
    assert result.allowed and gate.audit.list_recent()[-1]["decision"] == "allow"


def test_level_4_blocked(tmp_path: Path) -> None:
    gate = SafetyGate.from_config(
        LoopPilotConfig(
            runtime={"state_dir": str(tmp_path / "state")},
            safety={"stage": "ready", "max_level": 3},
        )
    )
    result = gate.check("unattended.daily", unattended=True, safe=True, level=SafetyLevel.REAL_BOUNDED)
    assert result.denied and result.reason_code == "LEVEL_4_BLOCKED"


def test_auto_approve_denied(tmp_path: Path) -> None:
    assert _gate(tmp_path=tmp_path).check("auto.approve").reason_code == "AUTO_APPROVE_FORBIDDEN"


def test_audit_log(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    audit.append(action="t", decision="deny", reason_code="T", config_hash="abc", message="m")
    assert audit.path.is_file()


def test_policy_defaults() -> None:
    policy = SafeAutonomyPolicy.from_config(LoopPilotConfig())
    assert policy.max_level == SafetyLevel.REAL_GUARDED
    assert not policy.allow_schedule_install
    assert policy.config is not None
