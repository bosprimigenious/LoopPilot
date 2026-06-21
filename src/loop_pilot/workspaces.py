"""Workspace resolution for Practical MVP 0.2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


@dataclass(frozen=True)
class WorkspaceSpec:
    workspace_id: str
    root: Path
    allowed_paths: list[str]
    forbidden_paths: list[str]
    allow_write: bool = False
    draft_file: str = "draft.md"
    references_file: str = "references.bib"


def resolve_workspace(
    workspaces: dict[str, Any],
    workspace_ref: str | None,
    *,
    loop_type: str | None = None,
) -> WorkspaceSpec | None:
    """Resolve a workspace id or path to a WorkspaceSpec."""
    if not workspace_ref:
        return None

    ref = workspace_ref.strip()
    if ref in workspaces:
        cfg = workspaces[ref]
        if not isinstance(cfg, dict):
            raise LoopPilotError(
                code=ErrorCode.CONFIG_INVALID,
                component="config.workspaces",
                message=f"Workspace config invalid for {ref}",
            )
        root = Path(str(cfg.get("root", ref)))
        return WorkspaceSpec(
            workspace_id=ref,
            root=root,
            allowed_paths=list(cfg.get("allowed_paths", [])),
            forbidden_paths=list(cfg.get("forbidden_paths", [])),
            allow_write=bool(cfg.get("allow_write", False)),
            draft_file=str(cfg.get("draft_file", "draft.md")),
            references_file=str(cfg.get("references_file", "references.bib")),
        )

    path = Path(ref)
    if path.exists():
        workspace_id = path.name
        defaults = _default_paths(loop_type)
        return WorkspaceSpec(
            workspace_id=workspace_id,
            root=path,
            allowed_paths=defaults["allowed_paths"],
            forbidden_paths=defaults["forbidden_paths"],
            allow_write=False,
        )

    raise LoopPilotError(
        code=ErrorCode.CONFIG_INVALID,
        component="config.workspaces",
        message=f"Unknown workspace: {workspace_ref}",
    )


def _default_paths(loop_type: str | None) -> dict[str, list[str]]:
    if loop_type == "paper":
        return {
            "allowed_paths": ["draft.md", "references.bib", "notes/**"],
            "forbidden_paths": ["experiments/raw/**"],
        }
    return {
        "allowed_paths": ["src/**", "tests/**"],
        "forbidden_paths": [".env*", "secrets/**"],
    }
