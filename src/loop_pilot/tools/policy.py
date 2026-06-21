"""Tool execution policy definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolPolicy:
    allowed_commands: list[str] = field(default_factory=lambda: ["pytest", "python", "git"])
    forbidden_tokens: list[str] = field(default_factory=lambda: ["push", "deploy", "release", "publish"])
    forbidden_paths: list[str] = field(default_factory=lambda: [".env", "secrets/**"])
    max_timeout_seconds: float = 300.0
    cwd_roots: list[str] = field(default_factory=list)

    @classmethod
    def from_config(cls, cfg: dict[str, Any]) -> ToolPolicy:
        return cls(
            allowed_commands=list(cfg.get("allowed_commands", ["pytest", "python", "git"])),
            forbidden_tokens=list(cfg.get("forbidden_tokens", ["push", "deploy", "release", "publish"])),
            forbidden_paths=list(cfg.get("forbidden_paths", [".env", "secrets/**"])),
            max_timeout_seconds=float(cfg.get("max_timeout_seconds", 300)),
            cwd_roots=list(cfg.get("cwd_roots", [])),
        )
