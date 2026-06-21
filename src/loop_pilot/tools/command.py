"""Command execution helpers for ToolBroker."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loop_pilot.domain.errors import ErrorCode


@dataclass
class CommandResult:
    status: str
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "error_code": self.error_code,
        }


def run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout: float,
    env: dict[str, str] | None = None,
) -> CommandResult:
    start = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        duration = int((time.monotonic() - start) * 1000)
        if process.returncode == 0:
            return CommandResult("success", process.returncode, stdout, stderr, duration)
        return CommandResult(
            "error",
            process.returncode,
            stdout,
            stderr,
            duration,
            error_code=ErrorCode.TOOL_FAILED.value,
        )
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        duration = int((time.monotonic() - start) * 1000)
        return CommandResult(
            "timeout",
            None,
            stdout,
            stderr,
            duration,
            error_code=ErrorCode.TOOL_TIMEOUT.value,
        )
