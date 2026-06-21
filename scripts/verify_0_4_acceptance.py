#!/usr/bin/env python3
"""Aggregate Truthful 0.4 Milestone A acceptance gate.

Only this script may report full 0.4 READY. Component scripts may report IMPLEMENTED.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StepResult:
    name: str
    command: str
    passed: bool
    summary: str
    notes: list[str] = field(default_factory=list)


def _acceptance_ready(results: list[StepResult]) -> bool:
    return bool(results) and all(result.passed for result in results)


DEFAULT_CONFIG_DIR = "tests/fixtures/acceptance_0_4a/config"
COMPONENT_SCRIPTS = (
    ("verify_0_3_acceptance.py", False),
    ("verify_0_4b_acceptance.py", True),
    ("verify_0_4c_acceptance.py", True),
    ("verify_0_4d_acceptance.py", True),
)


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _display(cmd: list[str]) -> str:
    shown = ["python" if part == sys.executable else part for part in cmd]
    return " ".join(shown)


def _venv_env(repo: Path) -> dict[str, str]:
    env = os.environ.copy()
    scripts = repo / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    if scripts.is_dir():
        env["PATH"] = f"{scripts}{os.pathsep}{env.get('PATH', '')}"
    return env


def _record(
    results: list[StepResult],
    name: str,
    cmd: list[str],
    proc: subprocess.CompletedProcess[str],
    *,
    expect_ready: bool = False,
) -> None:
    output = (proc.stdout or "") + (proc.stderr or "")
    passed = proc.returncode == 0
    if expect_ready and "(NOT READY)" in output:
        passed = False
    if expect_ready and "(READY)" not in output and proc.returncode == 0:
        passed = False
    summary = output.strip().splitlines()[-1] if output.strip() else f"rc={proc.returncode}"
    results.append(StepResult(name, _display(cmd), passed, summary))


def run_acceptance(repo: Path, *, config_dir: str) -> list[StepResult]:
    results: list[StepResult] = []
    env = _venv_env(repo)

    for name, cmd in [
        ("ruff check", [sys.executable, "-m", "ruff", "check", "."]),
        ("pytest full suite", [sys.executable, "-m", "pytest", "-q"]),
    ]:
        proc = _run(cmd, cwd=repo, env=env)
        _record(results, name, cmd, proc)

    for script, expect_ready in COMPONENT_SCRIPTS:
        cmd = [sys.executable, str(repo / "scripts" / script)]
        proc = _run(cmd, cwd=repo, env=env)
        _record(results, script, cmd, proc, expect_ready=expect_ready)

    matrix_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_db_ops.py",
        "tests/unit/test_migration_matrix.py",
        "-q",
        "-k",
        "migrate or dry_run",
    ]
    proc = _run(matrix_cmd, cwd=repo, env=env)
    _record(results, "migration matrix tests", matrix_cmd, proc)

    artifact_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_error_artifacts.py",
        "tests/unit/test_terminal_artifacts.py",
        "-q",
    ]
    proc = _run(artifact_cmd, cwd=repo, env=env)
    _record(results, "failure-artifact contract", artifact_cmd, proc)

    recovery_cmd = [sys.executable, "-m", "pytest", "tests/integration/test_v1_recovery.py", "-q"]
    proc = _run(recovery_cmd, cwd=repo, env=env)
    _record(results, "recovery/resume suite", recovery_cmd, proc)

    anti_cheat_cmd = [sys.executable, "-m", "pytest", "tests/unit/test_acceptance_truthfulness.py", "-q"]
    proc = _run(anti_cheat_cmd, cwd=repo, env=env)
    _record(results, "truthful-acceptance anti-cheat", anti_cheat_cmd, proc)

    review_cmd = [sys.executable, "-m", "pytest", "tests/integration/test_review_cli.py", "-q"]
    proc = _run(review_cmd, cwd=repo, env=env)
    _record(results, "0.4-c review CLI", review_cmd, proc)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Truthful 0.4 aggregate acceptance gate")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--config-dir", default=DEFAULT_CONFIG_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo = args.cwd.resolve()
    if not (repo / "scripts" / "verify_0_4_acceptance.py").is_file():
        print("verify_0_4_acceptance.py missing", file=sys.stderr)
        return 2

    results = run_acceptance(repo, config_dir=args.config_dir)
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    ready = _acceptance_ready(results)

    if args.json:
        payload = {
            "ready": ready,
            "passed": passed,
            "total": total,
            "results": [
                {"name": r.name, "passed": r.passed, "command": r.command, "summary": r.summary}
                for r in results
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        status = "READY" if ready else "NOT READY"
        print(f"# Truthful 0.4 aggregate acceptance ({status}): {passed}/{total} passed\n")
        for r in results:
            mark = "PASS" if r.passed else "FAIL"
            print(f"[{mark}] {r.name}")
            print(f"  $ {r.command}")
            print(f"  {r.summary}")

    if not ready:
        return 2
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
