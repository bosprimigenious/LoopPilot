"""SafetyGate — evaluate dangerous actions before side effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loop_pilot.config import LoopPilotConfig
from loop_pilot.safety.audit import AuditLog
from loop_pilot.safety.levels import SafetyLevel
from loop_pilot.safety.policy import SafeAutonomyPolicy
from loop_pilot.safety.readiness import PREP_STAGE_BLOCKED, is_prep_stage, prep_block_message


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    decision: str
    reason_code: str
    message: str
    level: SafetyLevel | None = None
    audit_path: str | None = None

    @property
    def denied(self) -> bool:
        return not self.allowed


class SafetyGate:
    def __init__(
        self,
        *,
        policy: SafeAutonomyPolicy,
        audit: AuditLog,
        config_hash: str,
        operator: str = "cli",
    ) -> None:
        self.policy = policy
        self.audit = audit
        self.config_hash = config_hash
        self.operator = operator

    @classmethod
    def from_config(cls, config: LoopPilotConfig, *, operator: str = "cli") -> SafetyGate:
        return cls(
            policy=SafeAutonomyPolicy.from_config(config),
            audit=AuditLog(config.state_dir / "audit"),
            config_hash=config.snapshot_hash(),
            operator=operator,
        )

    def check(self, action: str, **context: Any) -> GateResult:
        if action == "auto.approve":
            return self._deny(action, "AUTO_APPROVE_FORBIDDEN", "auto-approve is never allowed", context)
        if is_prep_stage(self.policy.config):
            if action in {"schedule.install", "schedule.uninstall", "unattended.daily"}:
                return self._deny(
                    action,
                    PREP_STAGE_BLOCKED,
                    prep_block_message(action),
                    context,
                )
        if action == "schedule.install":
            return self._check_schedule_install(context)
        if action == "schedule.uninstall":
            return self._check_schedule_uninstall(context)
        if action == "unattended.daily":
            return self._check_unattended_daily(context)
        if action == "adapter.invoke":
            return self._check_adapter_invoke(context)
        return self._deny(action, "UNKNOWN_ACTION", f"unknown action: {action}", context)

    def _check_schedule_uninstall(self, context: dict[str, Any]) -> GateResult:
        if not self.policy.allow_schedule_install:
            return self._deny(
                "schedule.uninstall",
                "SCHEDULE_INSTALL_DISABLED",
                "schedule.allow_install is false in config",
                context,
            )
        if self.policy.require_confirm_schedule and not context.get("confirm"):
            return self._deny(
                "schedule.uninstall",
                "CONFIRM_REQUIRED",
                "pass --confirm-schedule to acknowledge OS scheduler mutation",
                context,
            )
        return self._allow(
            "schedule.uninstall",
            "SCHEDULE_UNINSTALL_ALLOWED",
            "schedule uninstall permitted by policy",
            context,
        )

    def _check_schedule_install(self, context: dict[str, Any]) -> GateResult:
        if not self.policy.allow_schedule_install:
            return self._deny("schedule.install", "SCHEDULE_INSTALL_DISABLED", "schedule.allow_install is false in config", context)
        if self.policy.require_confirm_schedule and not context.get("confirm"):
            return self._deny("schedule.install", "CONFIRM_REQUIRED", "pass --confirm-schedule to acknowledge OS scheduler write", context)
        return self._allow("schedule.install", "SCHEDULE_INSTALL_ALLOWED", "schedule install permitted by policy", context)

    def _check_unattended_daily(self, context: dict[str, Any]) -> GateResult:
        level = SafetyLevel.parse(context.get("level", SafetyLevel.OBSERVE))
        if is_prep_stage(self.policy.config) and level >= SafetyLevel.REAL_GUARDED:
            return self._deny(
                "unattended.daily",
                PREP_STAGE_BLOCKED,
                prep_block_message("unattended.daily level 3+"),
                context,
                level=level,
            )
        if self.policy.require_unattended_safe:
            if context.get("unattended") and not context.get("safe"):
                return self._deny("unattended.daily", "UNATTENDED_REQUIRES_SAFE", "--unattended requires --safe", context)
            if not context.get("unattended") and not context.get("dry_run"):
                return self._deny("unattended.daily", "LIVE_DAILY_REQUIRES_UNATTENDED_SAFE", "live daily run requires --unattended --safe", context)
        if level == SafetyLevel.REAL_BOUNDED:
            return self._deny("unattended.daily", "LEVEL_4_BLOCKED", "level 4 blocked by default safe policy", context, level=level)
        if not self.policy.allows_level(level):
            return self._deny("unattended.daily", "LEVEL_EXCEEDS_MAX", f"level {level.value} exceeds policy max {self.policy.max_level.value}", context, level=level)
        return self._allow("unattended.daily", "UNATTENDED_SAFE_ALLOWED", f"unattended safe daily allowed at level {level.value}", context, level=level)

    def _check_adapter_invoke(self, context: dict[str, Any]) -> GateResult:
        level = SafetyLevel.parse(context.get("level", SafetyLevel.OBSERVE))
        if is_prep_stage(self.policy.config) and level >= SafetyLevel.REAL_GUARDED:
            return self._deny(
                "adapter.invoke",
                PREP_STAGE_BLOCKED,
                prep_block_message("adapter.invoke level 3+"),
                context,
                level=level,
            )
        if level <= SafetyLevel.MOCK_EXECUTE:
            return self._deny("adapter.invoke", "ADAPTER_BLOCKED_IN_SAFE_PROFILE", "adapters disabled in safe profile", context, level=level)
        return self._allow("adapter.invoke", "ADAPTER_ALLOWED", "adapter invoke permitted at guarded level", context, level=level)

    def _allow(self, action: str, reason_code: str, message: str, context: dict[str, Any], *, level: SafetyLevel | None = None) -> GateResult:
        self.audit.append(action=action, decision="allow", reason_code=reason_code, config_hash=self.config_hash, operator=self.operator, message=message, context=context or None)
        return GateResult(True, "allow", reason_code, message, level, str(self.audit.path))

    def _deny(self, action: str, reason_code: str, message: str, context: dict[str, Any], *, level: SafetyLevel | None = None) -> GateResult:
        self.audit.append(action=action, decision="deny", reason_code=reason_code, config_hash=self.config_hash, operator=self.operator, message=message, context=context or None)
        return GateResult(False, "deny", reason_code, message, level, str(self.audit.path))
