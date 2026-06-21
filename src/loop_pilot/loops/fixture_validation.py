"""Fixture existence and structure validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FixtureValidation:
    ok: bool
    missing: list[str]
    message: str = ""

    @property
    def blocked_reason(self) -> str:
        return f"Fixture invalid: {', '.join(self.missing)}" if self.missing else self.message


def _missing(paths: list[Path]) -> list[str]:
    return [str(p) for p in paths if not p.exists()]


def validate_intern_workspace(workspace_root: Path) -> FixtureValidation:
    required = [
        workspace_root / "src",
        workspace_root / "mock_responses",
    ]
    missing = _missing(required)
    return FixtureValidation(ok=not missing, missing=missing)


def validate_paper_workspace(workspace_root: Path, *, draft_file: str, references_file: str) -> FixtureValidation:
    required = [
        workspace_root / draft_file,
        workspace_root / references_file,
        workspace_root / "mock_responses",
    ]
    missing = _missing(required)
    return FixtureValidation(ok=not missing, missing=missing)


def validate_intern_fixture(fixture_dir: Path) -> FixtureValidation:
    required = [
        fixture_dir / "README.md",
        fixture_dir / "input",
        fixture_dir / "mock_responses",
    ]
    missing = _missing(required)
    if fixture_dir.name != "unsafe_path_change":
        missing.extend(_missing([fixture_dir / "input" / "src"]))
    return FixtureValidation(ok=not missing, missing=missing)


def validate_paper_fixture(fixture_dir: Path) -> FixtureValidation:
    required = [
        fixture_dir / "README.md",
        fixture_dir / "input" / "paper.md",
        fixture_dir / "input" / "references.bib",
        fixture_dir / "mock_responses",
    ]
    missing = _missing(required)
    return FixtureValidation(ok=not missing, missing=missing)


def validate_daily_news_fixture(fixture_dir: Path) -> FixtureValidation:
    required = [
        fixture_dir / "README.md",
        fixture_dir / "input" / "snapshots",
        fixture_dir / "config" / "daily_news.yaml",
        fixture_dir / "mock_responses",
    ]
    missing = _missing(required)
    snap_dir = fixture_dir / "input" / "snapshots"
    if snap_dir.exists() and not any(snap_dir.glob("*.json")):
        missing.append(str(snap_dir / "*.json"))
    return FixtureValidation(ok=not missing, missing=missing)
