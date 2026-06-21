"""ToolBroker — deterministic tool execution with policy gates."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.tools.command import CommandResult, run_command
from loop_pilot.tools.file_ops import is_path_allowed, read_text, write_text
from loop_pilot.tools.git_ops import diff_summary
from loop_pilot.tools.policy import ToolPolicy


class ToolBroker:
    """Routes file, git, and command requests through policy checks."""

    def __init__(self, policy: ToolPolicy | dict[str, Any] | None = None) -> None:
        if isinstance(policy, dict):
            self.policy = ToolPolicy.from_config(policy)
        elif policy is None:
            self.policy = ToolPolicy()
        else:
            self.policy = policy

    def run_command(
        self,
        command: list[str],
        *,
        cwd: Path,
        timeout: float | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        self._validate_command(command)
        self._validate_cwd(cwd)
        effective_timeout = min(
            timeout or self.policy.max_timeout_seconds,
            self.policy.max_timeout_seconds,
        )
        return run_command(command, cwd=cwd, timeout=effective_timeout, env=env)

    def read_file(self, path: Path, *, allowed: list[str] | None = None, forbidden: list[str] | None = None) -> str:
        allowed = allowed or ["**"]
        forbidden = forbidden or self.policy.forbidden_paths
        if not is_path_allowed(path, allowed, forbidden):
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Read denied: {path}",
            )
        return read_text(path, allowed=allowed, forbidden=forbidden)

    def write_file(
        self,
        path: Path,
        content: str,
        *,
        allowed: list[str] | None = None,
        forbidden: list[str] | None = None,
    ) -> dict[str, Any]:
        allowed = allowed or ["**"]
        forbidden = forbidden or self.policy.forbidden_paths
        if not is_path_allowed(path, allowed, forbidden):
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Write denied: {path}",
            )
        return write_text(path, content, allowed=allowed, forbidden=forbidden)

    def git_diff(self, worktree: Path) -> CommandResult:
        self._validate_cwd(worktree)
        if self._command_has_forbidden(["git", "diff"]):
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message="git diff blocked by policy",
            )
        return diff_summary(worktree, timeout=self.policy.max_timeout_seconds)

    def _validate_command(self, command: list[str]) -> None:
        if not command:
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message="Empty command",
            )
        if self._command_has_forbidden(command):
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Forbidden command token in {command!r}",
            )
        head = command[0].lower()
        if head not in {c.lower() for c in self.policy.allowed_commands}:
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Command not in allowlist: {head}",
            )

    def _validate_cwd(self, cwd: Path) -> None:
        if not self.policy.cwd_roots:
            return
        resolved = cwd.resolve()
        for root in self.policy.cwd_roots:
            root_path = Path(root).resolve()
            if resolved == root_path or root_path in resolved.parents:
                return
        raise LoopPilotError(
            code=ErrorCode.POLICY_DENIED,
            component="tool_broker",
            message=f"cwd {cwd} outside allowed roots",
        )

    def _command_has_forbidden(self, command: list[str]) -> bool:
        lowered = [part.lower() for part in command]
        if len(lowered) >= 2 and lowered[0] == "git" and lowered[1] == "push":
            return True
        return any(
            fnmatch.fnmatch(part, token) or part == token
            for part in lowered
            for token in self.policy.forbidden_tokens
        )
