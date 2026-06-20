"""Policy Gate — mandatory before every write action."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PolicyDecision:
    allowed: bool
    rule_id: str
    message: str
    requires_approval: bool = False


class PolicyEngine:
    def __init__(self, policies: dict[str, Any] | None = None) -> None:
        self.policies = policies or {}

    def check_write(
        self,
        target_path: str,
        allowed_paths: list[str],
        forbidden_paths: list[str],
        dry_run: bool = False,
    ) -> PolicyDecision:
        if dry_run:
            return PolicyDecision(
                allowed=True,
                rule_id="DRY_RUN",
                message="Dry-run mode: write simulated only",
            )

        normalized = target_path.replace("\\", "/")

        for pattern in forbidden_paths:
            if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(
                Path(normalized).name, pattern
            ):
                return PolicyDecision(
                    allowed=False,
                    rule_id="FORBIDDEN_PATH",
                    message=f"Path forbidden by policy: {target_path}",
                )

        if allowed_paths:
            matched = any(fnmatch.fnmatch(normalized, p) for p in allowed_paths)
            if not matched:
                return PolicyDecision(
                    allowed=False,
                    rule_id="PATH_NOT_ALLOWED",
                    message=f"Path not in allowed list: {target_path}",
                    requires_approval=True,
                )

        return PolicyDecision(
            allowed=True,
            rule_id="PATH_OK",
            message="Write permitted",
        )

    def check_command(self, command: list[str], forbidden_commands: list[str] | None = None) -> PolicyDecision:
        forbidden = forbidden_commands or ["git push", "git commit", "deploy"]
        joined = " ".join(command).lower()
        for fc in forbidden:
            if fc.lower() in joined:
                return PolicyDecision(
                    allowed=False,
                    rule_id="FORBIDDEN_COMMAND",
                    message=f"Command forbidden: {joined}",
                )
        return PolicyDecision(allowed=True, rule_id="COMMAND_OK", message="Command permitted")
