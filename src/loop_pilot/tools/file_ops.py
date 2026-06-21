"""File operations with path policy enforcement."""

from __future__ import annotations

import fnmatch
from pathlib import Path, PurePosixPath
from typing import Any


def _path_candidates(path: Path) -> list[str]:
    rel = str(path).replace("\\", "/")
    candidates = [rel, path.name]
    parts = path.parts
    for idx in range(len(parts)):
        candidates.append("/".join(parts[idx:]).replace("\\", "/"))
    return candidates


def _glob_match(candidate: str, pattern: str) -> bool:
    if pattern == "**":
        return True
    normalized = candidate.replace("\\", "/")
    if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(Path(normalized).name, pattern):
        return True
    return PurePosixPath(normalized).match(pattern)


def is_path_allowed(path: Path, allowed: list[str], forbidden: list[str]) -> bool:
    candidates = _path_candidates(path)
    for pattern in forbidden:
        if any(_glob_match(candidate, pattern) for candidate in candidates):
            return False
    if not allowed:
        return True
    return any(_glob_match(candidate, pattern) for candidate in candidates for pattern in allowed)


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
