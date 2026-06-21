"""ToolBroker — deterministic tool execution with policy gates."""

from __future__ import annotations

import fnmatch
import time
from pathlib import Path
from typing import Any

from loop_pilot.connectors import fetch_source as connector_fetch_source
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.tools.audit import ToolAuditEntry, audit_payload
from loop_pilot.tools.command import CommandResult, run_command
from loop_pilot.tools.file_ops import is_path_allowed, read_text, write_text
from loop_pilot.tools.git_ops import diff_summary
from loop_pilot.tools.policy import ToolPolicy


class ToolBroker:
    """Routes file, git, command, and connector requests through policy checks."""

    def __init__(self, policy: ToolPolicy | dict[str, Any] | None = None) -> None:
        if isinstance(policy, dict):
            self.policy = ToolPolicy.from_config(policy)
        elif policy is None:
            self.policy = ToolPolicy()
        else:
            self.policy = policy
        self._audit_log: list[ToolAuditEntry] = []

    @property
    def audit_log(self) -> list[ToolAuditEntry]:
        return list(self._audit_log)

    def audit_records(self) -> list[dict[str, Any]]:
        return audit_payload(self._audit_log)

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
        result = run_command(command, cwd=cwd, timeout=effective_timeout, env=env)
        self._audit_log.append(
            ToolAuditEntry(
                tool="command",
                status=result.status,
                duration_ms=result.duration_ms,
                argv=list(command),
                cwd=str(cwd),
                policy="allow",
                detail=result.error_code,
            )
        )
        return result

    def read_file(
        self,
        path: Path,
        *,
        allowed: list[str] | None = None,
        forbidden: list[str] | None = None,
    ) -> str:
        allowed = allowed or ["**"]
        forbidden = forbidden or self.policy.forbidden_paths
        start = time.monotonic()
        if not is_path_allowed(path, allowed, forbidden):
            self._record_denied("file_read", path=path)
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Read denied: {path}",
            )
        content = read_text(path, allowed=allowed, forbidden=forbidden)
        duration = int((time.monotonic() - start) * 1000)
        self._audit_log.append(
            ToolAuditEntry(
                tool="file_read",
                status="success",
                duration_ms=duration,
                path=str(path),
                policy="allow",
            )
        )
        return content

    def write_file(
        self,
        path: Path,
        content: str,
        *,
        allowed: list[str] | None = None,
        forbidden: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        allowed = allowed or ["**"]
        forbidden = forbidden or self.policy.forbidden_paths
        start = time.monotonic()
        if not is_path_allowed(path, allowed, forbidden):
            self._record_denied("file_write", path=path)
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Write denied: {path}",
            )
        if dry_run:
            duration = int((time.monotonic() - start) * 1000)
            self._audit_log.append(
                ToolAuditEntry(
                    tool="file_write",
                    status="dry_run_skipped",
                    duration_ms=duration,
                    path=str(path),
                    policy="allow",
                    dry_run=True,
                    detail=f"would_write {len(content.encode())} bytes",
                )
            )
            return {"path": str(path), "size_bytes": len(content.encode()), "dry_run": True}

        result = write_text(path, content, allowed=allowed, forbidden=forbidden)
        duration = int((time.monotonic() - start) * 1000)
        self._audit_log.append(
            ToolAuditEntry(
                tool="file_write",
                status="success",
                duration_ms=duration,
                path=str(path),
                policy="allow",
            )
        )
        return result

    def fetch_source(self, source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
        """Route connector HTTP/file reads through broker audit."""
        kind = str(source_cfg.get("kind", "local_json")).lower()
        start = time.monotonic()
        try:
            items = connector_fetch_source(source_cfg)
            status = "success"
        except (FileNotFoundError, ValueError) as exc:
            duration = int((time.monotonic() - start) * 1000)
            self._audit_log.append(
                ToolAuditEntry(
                    tool="http_get",
                    status="error",
                    duration_ms=duration,
                    path=str(source_cfg.get("path", "")),
                    source_kind=kind,
                    policy="allow",
                    detail=str(exc),
                )
            )
            raise
        duration = int((time.monotonic() - start) * 1000)
        self._audit_log.append(
            ToolAuditEntry(
                tool="http_get",
                status=status,
                duration_ms=duration,
                path=str(source_cfg.get("path", source_cfg.get("url", ""))),
                source_kind=kind,
                policy="allow",
                detail=f"{len(items)} items",
            )
        )
        return items

    def git_diff(self, worktree: Path) -> CommandResult:
        self._validate_cwd(worktree)
        if self._command_has_forbidden(["git", "diff"]):
            self._record_denied("git_diff", path=worktree)
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message="git diff blocked by policy",
            )
        result = diff_summary(worktree, timeout=self.policy.max_timeout_seconds)
        self._audit_log.append(
            ToolAuditEntry(
                tool="git_diff",
                status=result.status,
                duration_ms=result.duration_ms,
                cwd=str(worktree),
                policy="allow",
            )
        )
        return result

    def _record_denied(self, tool: str, *, path: Path | None = None) -> None:
        self._audit_log.append(
            ToolAuditEntry(
                tool=tool,
                status="blocked",
                path=str(path) if path is not None else None,
                policy="deny",
            )
        )

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
        if not self._command_head_allowed(command[0]):
            raise LoopPilotError(
                code=ErrorCode.POLICY_DENIED,
                component="tool_broker",
                message=f"Command not in allowlist: {command[0]}",
            )

    def _command_head_allowed(self, head: str) -> bool:
        allowed_lower = {c.lower() for c in self.policy.allowed_commands}
        lowered = head.lower()
        if lowered in allowed_lower:
            return True
        name = Path(head).name.lower()
        if name in allowed_lower:
            return True
        if name.startswith("python") and "python" in allowed_lower:
            return True
        return False

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
