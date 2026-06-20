"""PaperLoop V1 working-copy helpers."""

from __future__ import annotations

import fnmatch
import shutil
from pathlib import Path


def create_paper_working_copy(
    workspace: Path,
    copy_root: Path,
    read_only_patterns: list[str] | None = None,
) -> Path:
    """Copy a paper workspace while excluding configured read-only paths."""
    if not workspace.exists():
        raise FileNotFoundError(f"Paper workspace does not exist: {workspace}")
    read_only_patterns = read_only_patterns or []
    destination = copy_root / workspace.name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    for source in workspace.rglob("*"):
        rel = source.relative_to(workspace)
        rel_text = rel.as_posix()
        if _matches_any(rel_text, read_only_patterns):
            continue
        target = destination / rel
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return destination


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
