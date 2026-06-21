"""Cursor CLI Adapter — workspace-scoped coding CLI with safety boundaries."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any

from loop_pilot.adapters.base import (
    AdapterCapabilities,
    AdapterRequest,
    AdapterResult,
    AdapterStatus,
    BaseAdapter,
    HealthStatus,
)
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.domain.models import ArtifactReference, content_hash
from loop_pilot.runtime.boundaries import CancellationToken


class CursorCLIAdapter(BaseAdapter):
    """Controlled Cursor CLI wrapper; cwd limited to approved worktree."""

    FORBIDDEN_TOKENS = frozenset({"push", "deploy", "release", "publish", "commit"})
    FORBIDDEN_PATHS = frozenset({".env", ".env.local", "secrets"})

    def __init__(
        self,
        adapter_id: str,
        command: list[str],
        approved_worktree: Path,
        artifact_dir: Path,
        *,
        timeout_seconds: float = 900,
        env_allowlist: list[str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("command must be a non-empty argument array")
        self.adapter_id = adapter_id
        self.command = command
        self.approved_worktree = approved_worktree.resolve()
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.env_allowlist = env_allowlist or []

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            supports_tools=True,
            supports_file_write=True,
            supports_structured_output=True,
            supports_dry_run=True,
            network_required=False,
        )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(status="ok", adapter_id=self.adapter_id, message="cursor_cli configured")

    def execute(
        self,
        request: dict[str, Any] | AdapterRequest,
        timeout: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> AdapterResult:
        if isinstance(request, AdapterRequest):
            payload = request.to_dict()
        else:
            payload = dict(request)
        start = time.monotonic()
        cwd = Path(str(payload.get("cwd", self.approved_worktree))).resolve()
        effective_timeout = timeout if timeout is not None else self.timeout_seconds

        if cancellation and cancellation.is_cancelled:
            return self._error(AdapterStatus.CANCELLED.value, ErrorCode.TOOL_FAILED, start)
        if not self._is_approved_cwd(cwd):
            return self._error(AdapterStatus.ERROR.value, ErrorCode.POLICY_DENIED, start)
        if self._is_forbidden_command() or self._touches_forbidden_paths(payload):
            return self._error(AdapterStatus.ERROR.value, ErrorCode.POLICY_DENIED, start)

        if payload.get("dry_run"):
            transcript = self._write_artifact(
                "transcript-dry-run.txt",
                f"DRY_RUN command={self.command!r} cwd={cwd}\n",
                "transcript",
            )
            return AdapterResult(
                status=AdapterStatus.SUCCESS.value,
                structured_output={"dry_run": True, "adapter": self.adapter_id},
                transcript_artifact=transcript,
                usage={"duration_ms": int((time.monotonic() - start) * 1000)},
            )

        env = {key: os.environ[key] for key in self.env_allowlist if key in os.environ}
        process = subprocess.Popen(
            self.command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=effective_timeout)
            status = AdapterStatus.SUCCESS.value if process.returncode == 0 else AdapterStatus.ERROR.value
            error_code = None if process.returncode == 0 else ErrorCode.TOOL_FAILED.value
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            status = AdapterStatus.TIMEOUT.value
            error_code = ErrorCode.TOOL_TIMEOUT.value

        stdout_artifact = self._write_artifact("stdout.txt", stdout, "stdout")
        stderr_artifact = self._write_artifact("stderr.txt", stderr, "stderr")
        transcript_artifact = self._write_artifact(
            "transcript.txt",
            f"command={self.command!r}\ncwd={cwd}\nexit_code={process.returncode}\n",
            "transcript",
        )
        return AdapterResult(
            status=status,
            structured_output={"exit_code": process.returncode},
            stdout_artifact=stdout_artifact,
            stderr_artifact=stderr_artifact,
            transcript_artifact=transcript_artifact,
            usage={"duration_ms": int((time.monotonic() - start) * 1000)},
            error_code=error_code,
        )

    def estimate_cost(self, _request: dict[str, Any] | AdapterRequest) -> dict[str, int]:
        return {"cost": 0}

    def normalize_error(self, error: Exception) -> LoopPilotError:
        return LoopPilotError(
            code=ErrorCode.TOOL_FAILED,
            component=self.adapter_id,
            message=str(error),
            retryable=False,
        )

    def _is_approved_cwd(self, cwd: Path) -> bool:
        return cwd == self.approved_worktree or self.approved_worktree in cwd.parents

    def _is_forbidden_command(self) -> bool:
        lowered = [part.lower() for part in self.command]
        if len(lowered) >= 2 and lowered[0] == "git" and lowered[1] in {"push", "commit"}:
            return True
        return any(part in self.FORBIDDEN_TOKENS for part in lowered)

    def _touches_forbidden_paths(self, payload: dict[str, Any]) -> bool:
        target = str(payload.get("target_path", "")).lower()
        return any(forbidden in target for forbidden in self.FORBIDDEN_PATHS)

    def _error(self, status: str, code: ErrorCode, start: float) -> AdapterResult:
        return AdapterResult(
            status=status,
            usage={"duration_ms": int((time.monotonic() - start) * 1000)},
            error_code=code.value,
        )

    def _write_artifact(self, name: str, content: str, kind: str) -> ArtifactReference:
        path = self.artifact_dir / f"{self.adapter_id}-{name}"
        path.write_text(content, encoding="utf-8")
        rel = path.relative_to(self.artifact_dir)
        return ArtifactReference(
            artifact_id=f"{self.adapter_id}-{name}",
            kind=kind,
            path=str(rel),
            media_type="text/plain",
            sha256=content_hash({"content": content}),
            size_bytes=len(content.encode()),
            created_by=self.adapter_id,
        )
