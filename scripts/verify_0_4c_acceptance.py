#!/usr/bin/env python3
"""Run 0.4-c executable acceptance (Review Layer).

Requires 0.4-a sqlite backend and 0.4-b inbox/queue/today.
Before 0.4-c is implemented, reports readiness gate FAIL with a clear pending list.
"""

from __future__ import annotations

import argparse
import json
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
REQUIRED_MODULES = [
    "src/loop_pilot/review/__init__.py",
    "src/loop_pilot/review/store.py",
    "src/loop_pilot/review/service.py",
    "src/loop_pilot/review/review_agent.py",
    "src/loop_pilot/cli_review.py",
]
REQUIRED_CLI = ("review", "approve", "reject", "defer", "cancel", "resume")
REQUIRED_TESTS = [
    "tests/unit/test_review_store.py",
    "tests/integration/test_review_cli.py",
    "tests/unit/test_review_service_patch_gate.py",
]
BEHAVIOR_TESTS = [
    "tests/unit/test_review_service_patch_gate.py::test_patch_run_writes_needs_review_gate_before_approval",
    "tests/unit/test_review_service_patch_gate.py::test_patch_run_is_needs_review_not_completed_in_summary",
    "tests/unit/test_review_service_patch_gate.py::test_approve_patch_run_finalizes_directly",
    "tests/unit/test_review_service_patch_gate.py::test_approved_patch_run_does_not_enter_resume_requested",
    "tests/unit/test_review_service_patch_gate.py::test_rejected_patch_run_cannot_resume",
    "tests/unit/test_review_service_patch_gate.py::test_cancelled_patch_run_cannot_resume",
    "tests/unit/test_terminal_artifacts.py::test_manifest_does_not_include_self_checksum",
    "tests/unit/test_terminal_artifacts.py::test_artifact_manifest_excludes_itself",
    "tests/unit/test_terminal_artifacts.py::test_terminal_artifacts_manifest_checksums_match_final_files",
    "tests/unit/test_terminal_artifacts.py::test_intern_patch_run_does_not_overwrite_canonical_manifest",
    "tests/unit/test_summary_collector.py::test_report_path_prefers_actual_report_over_diff_summary",
    "tests/unit/test_review_store.py::test_deferred_review_item_survives_sync_until_due_date",
]


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def _display(cmd: list[str]) -> str:
    shown = ["python" if part == sys.executable else part for part in cmd]
    if shown[:3] == ["python", "-m", "loop_pilot.cli"]:
        shown = ["loop-pilot", *shown[3:]]
    return " ".join(shown)


def _loop_pilot(*args: str, config_dir: str) -> list[str]:
    return [sys.executable, "-m", "loop_pilot.cli", "--config-dir", config_dir, *args]


def _cli_has_command(repo: Path, name: str) -> bool:
    proc = _run([sys.executable, "-m", "loop_pilot.cli", name, "--help"], cwd=repo)
    return proc.returncode == 0 and "Error: No such command" not in (proc.stdout + proc.stderr)


def _readiness_checks(repo: Path) -> tuple[list[StepResult], bool]:
    results: list[StepResult] = []
    ready = True

    def record(name: str, cmd: str, passed: bool, summary: str, notes: list[str] | None = None) -> None:
        nonlocal ready
        if not passed:
            ready = False
        results.append(StepResult(name, cmd, passed, summary, notes or []))

    for rel in REQUIRED_MODULES:
        path = repo / rel
        record(f"module {rel}", f"exists {rel}", path.is_file(), "present" if path.is_file() else "missing")

    for rel in REQUIRED_TESTS:
        path = repo / rel
        record(f"test {rel}", f"exists {rel}", path.is_file(), "present" if path.is_file() else "missing")

    cli_py = repo / "src/loop_pilot/cli.py"
    wired = cli_py.is_file() and ("cli_review" in cli_py.read_text(encoding="utf-8"))
    record(
        "CLI wired in cli.py",
        "grep cli.py for cli_review",
        wired,
        "registered" if wired else "cli_review not wired in cli.py",
    )

    for cmd_name in REQUIRED_CLI:
        ok = _cli_has_command(repo, cmd_name)
        record(f"CLI {cmd_name}", f"loop-pilot {cmd_name} --help", ok, "registered" if ok else "not registered")

    migrations = repo / "src/loop_pilot/storage/migrations.py"
    if migrations.is_file():
        text = migrations.read_text(encoding="utf-8")
        has_review = "review_items" in text
        has_v4 = "CURRENT_SCHEMA_VERSION = 4" in text or "_migrate_v4" in text
        record(
            "migration v4 review_items",
            "grep migrations.py",
            has_review and has_v4,
            "v4 with review_items" if has_review and has_v4 else "missing v4 or review_items",
        )
    else:
        record("migrations.py", "exists", False, "missing")

    return results, ready


def run_acceptance(repo: Path, *, config_dir: str) -> list[StepResult]:
    results: list[StepResult] = []
    readiness, ready = _readiness_checks(repo)
    results.extend(readiness)

    def record(name: str, cmd: list[str], passed: bool, summary: str, notes: list[str] | None = None) -> None:
        results.append(StepResult(name, _display(cmd), passed, summary, notes or []))

    if not ready:
        record(
            "0.4-c readiness gate",
            [sys.executable, "-c", "readiness"],
            False,
            "NOT READY — implement 0.4-c before full acceptance",
            [
                "Add src/loop_pilot/review/ and cli_review.py; wire into cli.py",
                "Migration v4: review_items + queue indexes",
                "Implement ReviewAgent (suggestion only) and human decision CLI",
                "Add tests and run commands in docs/development/45-personal-daily-loop-0.4c-acceptance.md",
            ],
        )
        return results

    record("0.4-c readiness gate", [sys.executable, "-c", "readiness"], True, "all prerequisites present")

    for name, args in [
        ("0.4-a db migrate", ("db", "migrate")),
        ("0.4-a db verify", ("db", "verify")),
    ]:
        cmd = _loop_pilot(*args, config_dir=config_dir)
        proc = _run(cmd, cwd=repo)
        ok = proc.returncode == 0
        record(name, cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = _loop_pilot("review", "list", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    record("review list", cmd, proc.returncode == 0, proc.stdout.strip()[:120] or f"rc={proc.returncode}")

    for test_path in REQUIRED_TESTS:
        cmd = [sys.executable, "-m", "pytest", test_path, "-q"]
        proc = _run(cmd, cwd=repo)
        record(f"pytest {test_path}", cmd, proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    for test_target in BEHAVIOR_TESTS:
        cmd = [sys.executable, "-m", "pytest", test_target, "-q"]
        proc = _run(cmd, cwd=repo)
        label = test_target.rsplit("/", 1)[-1]
        record(f"behavior {label}", cmd, proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = [sys.executable, "-m", "loop_pilot.cli", "approve", "--help"]
    proc = _run(cmd, cwd=repo)
    json_ok = proc.returncode != 0 or "No such command" in (proc.stdout + proc.stderr) or "sqlite" in (proc.stdout + proc.stderr).lower()
    record(
        "json backend no fake approve",
        _display(cmd),
        json_ok,
        "not registered or sqlite guard" if json_ok else "unexpected success on default json backend",
    )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="0.4-c executable acceptance (Review Layer)")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--config-dir", default=DEFAULT_CONFIG_DIR)
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo = args.cwd.resolve()
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
                {"name": r.name, "passed": r.passed, "command": r.command, "summary": r.summary, "notes": r.notes}
                for r in results
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        status = "READY" if ready else "NOT READY"
        print(f"# 0.4-c acceptance ({status}): {passed}/{total} passed\n")
        for r in results:
            mark = "PASS" if r.passed else "FAIL"
            print(f"[{mark}] {r.name}")
            print(f"  $ {r.command}")
            print(f"  {r.summary}")
            for note in r.notes:
                print(f"  note: {note}")

    if not ready:
        return 2
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
