"""File operations with path policy enforcement."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any


def is_path_allowed(path: Path, allowed: list[str], forbidden: list[str]) -> bool:
    rel = str(path).replace("\\", "/")
    for pattern in forbidden:
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
            return False
    if not allowed:
        return True
    return any(fnmatch.fnmatch(rel, pattern) for pattern in allowed)


def read_text(path: Path, *, allowed: list[str], forbidden: list[str]) -> str:
    if not is_path_allowed(path, allowed, forbidden):
        raise PermissionError(f"Path not allowed: {path}")
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, *, allowed: list[str], forbidden: list[str]) -> dict[str, Any]:
    if not is_path_allowed(path, allowed, forbidden):
        raise PermissionError(f"Path not allowed: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path), "size_bytes": len(content.encode())}
