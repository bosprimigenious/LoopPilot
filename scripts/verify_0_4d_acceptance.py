#!/usr/bin/env python3
"""Run 0.4-d executable acceptance (Daily Summary + Schedule Preview + Daily Dry-Run).

Requires 0.4-a sqlite backend and 0.4-b inbox/queue/today.
Before 0.4-d is implemented, reports readiness gate FAIL with a clear pending list.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from loop_pilot.runtime.locks import clear_repo_runtime_locks


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
    "src/loop_pilot/summary/__init__.py",
    "src/loop_pilot/summary/collector.py",
    "src/loop_pilot/summary/renderer.py",
    "src/loop_pilot/summary/service.py",
    "src/loop_pilot/summary/store.py",
    "src/loop_pilot/scheduler/__init__.py",
    "src/loop_pilot/scheduler/printer.py",
    "src/loop_pilot/scheduler/installer.py",
    "src/loop_pilot/runtime/daily_run.py",
    "src/loop_pilot/cli_summary.py",
    "src/loop_pilot/cli_schedule.py",
]
REQUIRED_CLI_GROUPS = ("summary", "schedule")
REQUIRED_TESTS = [
    "tests/integration/test_daily_summary_cli.py",
    "tests/unit/test_summary_collector.py",
]
PREREQUISITE_SCRIPTS = (
    ("0.3", "verify_0_3_acceptance.py"),
    ("0.4-b", "verify_0_4b_acceptance.py"),
    ("0.4-c", "verify_0_4c_acceptance.py"),
)
DAILY_SECTIONS = (
    "## 1. 今日最重要结论",
    "## 2. Today",
    "## 3. Runs",
    "## 4. Needs Review",
    "## 5. Inbox Updates",
    "## 6. Blocked",
    "## 7. Tomorrow",
)


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
    if cli_py.is_file():
        text = cli_py.read_text(encoding="utf-8")
        wired_summary = "cli_summary" in text and "summary" in text
        wired_schedule = "cli_schedule" in text and "schedule" in text
        wired_daily = "run daily" in text or "daily_run" in text
        record(
            "CLI wired in cli.py",
            "grep cli.py for summary/schedule/daily",
            wired_summary and wired_schedule and wired_daily,
            "registered" if wired_summary and wired_schedule and wired_daily else "summary/schedule/daily not wired",
        )
    else:
        record("cli.py", "exists", False, "missing")

    for cmd_name in REQUIRED_CLI_GROUPS:
        ok = _cli_has_command(repo, cmd_name)
        record(f"CLI {cmd_name}", f"loop-pilot {cmd_name} --help", ok, "registered" if ok else "not registered")

    migrations = repo / "src/loop_pilot/storage/migrations.py"
    if migrations.is_file():
        text = migrations.read_text(encoding="utf-8")
        has_summaries = "summaries" in text
        record(
            "migration summaries table",
            "grep migrations.py for summaries",
            has_summaries,
            "summaries table present" if has_summaries else "missing summaries table",
        )
    else:
        record("migrations.py", "exists", False, "missing")

    return results, ready


def _extract_summary_path(output: str) -> Path | None:
    match = re.search(r"(?:Daily|Weekly) summary:\s*(.+)", output)
    if not match:
        return None
    return Path(match.group(1).strip())


def run_acceptance(repo: Path, *, config_dir: str) -> list[StepResult]:
    results: list[StepResult] = []
    clear_repo_runtime_locks(repo)
    readiness, ready = _readiness_checks(repo)
    results.extend(readiness)

    def record(name: str, cmd: list[str], passed: bool, summary: str, notes: list[str] | None = None) -> None:
        results.append(StepResult(name, cmd, passed, summary, notes or []))

    if not ready:
        record(
            "0.4-d readiness gate",
            [sys.executable, "-c", "readiness"],
            False,
            "NOT READY — implement 0.4-d before full acceptance",
            [
                "Add src/loop_pilot/summary/ and src/loop_pilot/scheduler/",
                "Wire cli_summary.py, cli_schedule.py, run daily in cli.py",
                "Migration: summaries table",
                "Add tests and run commands in docs/development/48-personal-daily-loop-0.4d-acceptance.md",
            ],
        )
        return results

    record("0.4-d readiness gate", [sys.executable, "-c", "readiness"], True, "all prerequisites present")

    clear_repo_runtime_locks(repo)
    prerequisites_passed = True
    for version, script_name in PREREQUISITE_SCRIPTS:
        clear_repo_runtime_locks(repo)
        cmd = [sys.executable, str(repo / "scripts" / script_name), "--cwd", str(repo)]
        proc = _run(cmd, cwd=repo)
        ok = proc.returncode == 0
        prerequisites_passed = prerequisites_passed and ok
        output = (proc.stdout + proc.stderr).strip().splitlines()
        record(
            f"prerequisite {version} acceptance",
            cmd,
            ok,
            output[0] if output else f"rc={proc.returncode}",
        )

    if not prerequisites_passed:
        return results

    for name, args in [
        ("0.4-a db migrate", ("db", "migrate")),
        ("0.4-a db verify", ("db", "verify")),
    ]:
        cmd = _loop_pilot(*args, config_dir=config_dir)
        proc = _run(cmd, cwd=repo)
        ok = proc.returncode == 0
        record(name, cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = _loop_pilot("summary", "today", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    ok = proc.returncode == 0 and "Daily summary:" in proc.stdout
    record("summary today", cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    daily_path = _extract_summary_path(proc.stdout)
    if daily_path and daily_path.is_file():
        content = daily_path.read_text(encoding="utf-8")
        missing = [section for section in DAILY_SECTIONS if section not in content]
        record(
            "daily-summary seven sections",
            f"read {daily_path}",
            not missing,
            "all sections present" if not missing else f"missing: {', '.join(missing)}",
        )
    else:
        record("daily-summary seven sections", "read daily-summary.md", False, "file not found")

    cmd = _loop_pilot("summary", "week", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    ok = proc.returncode == 0 and "Weekly summary:" in proc.stdout
    record("summary week", cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = _loop_pilot("schedule", "print", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    record("schedule print", cmd, proc.returncode == 0, proc.stdout.strip()[:120] or f"rc={proc.returncode}")

    cmd = _loop_pilot("schedule", "install", "--dry-run", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    no_install = "No system scheduler entries were created." in proc.stdout
    record(
        "schedule install --dry-run",
        cmd,
        proc.returncode == 0 and no_install,
        "preview only" if no_install else proc.stdout.strip()[:120] or f"rc={proc.returncode}",
    )

    cmd = _loop_pilot("run", "daily", "--dry-run", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    ok = proc.returncode == 0 and "summary:" in proc.stdout.lower()
    record("run daily --dry-run", cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    for test_path in REQUIRED_TESTS:
        cmd = [sys.executable, "-m", "pytest", test_path, "-q"]
        proc = _run(cmd, cwd=repo)
        record(
            f"pytest {test_path}",
            cmd,
            proc.returncode == 0,
            proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}",
        )

    cmd = [sys.executable, "-m", "loop_pilot.cli", "summary", "today"]
    proc = _run(cmd, cwd=repo)
    json_ok = proc.returncode != 0 or "No such command" in (proc.stdout + proc.stderr) or "sqlite" in (proc.stdout + proc.stderr).lower()
    record(
        "json backend no fake summary",
        _display(cmd),
        json_ok,
        "not registered or clear error" if json_ok else "unexpected success on default json backend",
    )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="0.4-d executable acceptance (Daily Summary + Schedule Preview)")
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
        print(f"# 0.4-d acceptance ({status}): {passed}/{total} passed\n")
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
