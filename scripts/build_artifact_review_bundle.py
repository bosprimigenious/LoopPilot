#!/usr/bin/env python3
"""Build an offline artifact-review bundle from a clean checkout.

The bundle intentionally contains only git-tracked project files plus generated
review notes. It excludes runtime state, virtual environments, caches, secrets,
and local credentials by construction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "dist" / "artifact-review"

PRIVATE_PREFIXES = (
    "auth/",
    "secrets/",
    "tokens/",
    "private/",
    "local/",
)

PRIVATE_SUFFIXES = (
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".sqlite",
    ".sqlite3",
    ".db",
)

PRIVATE_FILENAMES = (
    "credentials.json",
    "secrets.json",
    "tokens.json",
)

REQUIRED_PATHS = (
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "CODE_OF_CONDUCT.md",
    "pyproject.toml",
    "scripts/build_artifact_review_bundle.py",
    "scripts/deploy_wsl.sh",
    "scripts/verify_open_artifact_readiness.py",
    "scripts/run_failure_injection_bench.py",
    "scripts/verify_wsl_deploy_static.py",
    "scripts/verify_api_bridge_contract.py",
    "scripts/verify_wechat_miniprogram_static.py",
    "paper/direction.md",
    "paper/aa-open-source-standard.md",
    "paper/outline.md",
    "paper/latex/main.tex",
)

VALIDATION_COMMANDS = (
    "python -m pip install -e \".[dev]\"",
    "ruff check .",
    "python scripts/verify_open_artifact_readiness.py",
    "python scripts/run_failure_injection_bench.py --execute-oracles",
    "python scripts/verify_wsl_deploy_static.py",
    "python scripts/verify_api_bridge_contract.py",
    "python scripts/verify_wechat_miniprogram_static.py",
    "pytest -q",
)


@dataclass(frozen=True)
class BundleSummary:
    commit: str
    created_utc: str
    file_count: int
    command_count: int
    archive_path: str
    archive_sha256: str


def _run_git(args: tuple[str, ...]) -> str:
    proc = subprocess.run(  # noqa: S603
        ("git", *args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def _tracked_files() -> list[str]:
    output = _run_git(("ls-files", "-z"))
    files = sorted(path for path in output.split("\0") if path)
    missing = [path for path in REQUIRED_PATHS if path not in files]
    if missing:
        raise AssertionError(f"required artifact paths are not tracked: {', '.join(missing)}")
    blocked = []
    for path in files:
        lower = path.lower()
        name = Path(path).name.lower()
        if path == ".env.example":
            continue
        if (
            lower.startswith(PRIVATE_PREFIXES)
            or lower.endswith(PRIVATE_SUFFIXES)
            or name in PRIVATE_FILENAMES
            or name.startswith("credentials.")
        ):
            blocked.append(path)
    if blocked:
        raise AssertionError(f"tracked private-looking paths refused: {', '.join(blocked)}")
    return files


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _generated_files(commit: str, files: list[str]) -> dict[str, bytes]:
    command_lines = "\n".join(f"- `{command}`" for command in VALIDATION_COMMANDS)
    included_lines = "\n".join(f"- `{path}`" for path in files)
    notes = f"""# LoopPilot Artifact Review Bundle

Commit: `{commit}`

This bundle is generated from git-tracked files only. It intentionally excludes
`.git`, `.venv`, runtime `var/` state, caches, local databases, credentials, and
private workspaces.

## Reviewer Path

1. Create a Python 3.11+ virtual environment.
2. Install the project with dev dependencies.
3. Run the validation commands in `COMMANDS.md`.
4. Inspect `paper/aa-open-source-standard.md` for the paper/open-source gate.
5. Inspect `scripts/run_failure_injection_bench.py` for PR #8 oracle evidence.

## Included Files

{included_lines}
"""
    commands = f"""# Reproducibility Commands

Run from the repository root after extracting this bundle.

{command_lines}

The fault-injection bench currently executes non-mutating oracles. It is
evidence for semantic runtime invariants, not a claim of broad injected
mutation coverage.
"""
    environment = {
        "commit": commit,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "python": ">=3.11",
        "network_required_after_checkout": False,
        "private_credentials_required": False,
        "validation_commands": list(VALIDATION_COMMANDS),
    }
    return {
        "REVIEWER_NOTES.md": notes.encode("utf-8"),
        "COMMANDS.md": commands.encode("utf-8"),
        "ENVIRONMENT.json": json.dumps(environment, indent=2).encode("utf-8") + b"\n",
    }


def build_bundle(output_dir: Path) -> BundleSummary:
    commit = _run_git(("rev-parse", "HEAD"))
    short_commit = commit[:12]
    files = _tracked_files()
    generated = _generated_files(commit, files)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"looppilot-artifact-review-{short_commit}.tar.gz"
    root_name = f"looppilot-artifact-review-{short_commit}"

    with tarfile.open(archive_path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for path in files:
            archive.add(ROOT / path, arcname=f"{root_name}/repo/{path}", recursive=False)
        for name, payload in generated.items():
            info = tarfile.TarInfo(name=f"{root_name}/artifact-review/{name}")
            info.size = len(payload)
            info.mtime = 0
            archive.addfile(info, fileobj=_BytesReader(payload))

    summary = BundleSummary(
        commit=commit,
        created_utc=datetime.now(UTC).isoformat(timespec="seconds"),
        file_count=len(files),
        command_count=len(VALIDATION_COMMANDS),
        archive_path=str(archive_path.relative_to(ROOT)),
        archive_sha256=_sha256(archive_path),
    )
    summary_path = output_dir / f"looppilot-artifact-review-{short_commit}.json"
    summary_path.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    return summary


class _BytesReader:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = len(self._payload) - self._offset
        chunk = self._payload[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for generated artifact bundle and summary JSON",
    )
    args = parser.parse_args()

    summary = build_bundle(args.output_dir)
    print("artifact review bundle: PASS")
    print(f"  archive: {summary.archive_path}")
    print(f"  sha256:  {summary.archive_sha256}")
    print(f"  files:   {summary.file_count}")
    print(f"  commands:{summary.command_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
