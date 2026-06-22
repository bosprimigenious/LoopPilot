#!/usr/bin/env python3
"""Run 0.4-b executable acceptance (inbox / queue / today).

Requires 0.4-a sqlite backend. Safe for CI when implemented: uses fixture config
and temp-friendly paths under tests/fixtures/acceptance_0_4a/config.

Before 0.4-b is implemented, reports readiness gate FAIL with a clear pending list.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
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
    "src/loop_pilot/tasks/__init__.py",
    "src/loop_pilot/tasks/store.py",
    "src/loop_pilot/tasks/inbox_service.py",
    "src/loop_pilot/tasks/queue_service.py",
    "src/loop_pilot/tasks/today_service.py",
    "src/loop_pilot/cli_tasks.py",
]
REQUIRED_CLI_GROUPS = ("inbox", "queue", "today")
REQUIRED_TABLES = ("inbox_items", "queue_items")
OPTIONAL_TABLES = ("today_items",)
REQUIRED_TEST_FILES = (
    "tests/unit/test_inbox_queue.py",
    "tests/unit/test_inbox_store.py",
)
REQUIRED_INTEGRATION_TESTS = (
    "tests/integration/test_inbox_cli.py",
    "tests/integration/test_queue_cli.py",
    "tests/integration/test_daily_news_to_inbox.py",
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


def _schema_tables(db_path: Path) -> set[str]:
    if not db_path.is_file():
        return set()
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def _cli_registered_in_main(repo: Path) -> bool:
    cli_py = repo / "src/loop_pilot/cli.py"
    if not cli_py.is_file():
        return False
    text = cli_py.read_text(encoding="utf-8")
    return "cli_tasks" in text or "add_command(inbox" in text


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

    unit_test = next((repo / p for p in REQUIRED_TEST_FILES if (repo / p).is_file()), None)
    if unit_test is None:
        record("unit tests (inbox/queue)", "exists test_inbox_*", False, "missing")
    else:
        record("unit tests", f"exists {unit_test.relative_to(repo)}", True, "present")

    integration_count = sum(1 for p in REQUIRED_INTEGRATION_TESTS if (repo / p).is_file())
    record(
        "integration tests",
        f"{integration_count}/{len(REQUIRED_INTEGRATION_TESTS)} present",
        integration_count >= 2,
        f"found {integration_count} integration test modules",
    )

    wired = _cli_registered_in_main(repo)
    record(
        "CLI wired in cli.py",
        "grep cli.py for cli_tasks",
        wired,
        "registered" if wired else "cli_tasks.py exists but not add_command'd in cli.py",
    )

    for cmd_name in REQUIRED_CLI_GROUPS:
        ok = _cli_has_command(repo, cmd_name)
        record(f"CLI {cmd_name}", f"loop-pilot {cmd_name} --help", ok, "registered" if ok else "not registered")

    migrations = repo / "src/loop_pilot/storage/migrations.py"
    if migrations.is_file():
        text = migrations.read_text(encoding="utf-8")
        has_inbox = "inbox_items" in text
        has_v2 = "CURRENT_SCHEMA_VERSION = 2" in text or "_migrate_v2" in text
        record(
            "migration v2 inbox/queue",
            "grep migrations.py",
            has_inbox and has_v2,
            "v2 with inbox_items" if has_inbox and has_v2 else "missing v2 or inbox_items",
        )
    else:
        record("migrations.py", "exists", False, "missing")

    daily_news = repo / "src/loop_pilot/loops/daily_news/loop.py"
    import_test = repo / "tests/integration/test_daily_news_to_inbox.py"
    if daily_news.is_file():
        text = daily_news.read_text(encoding="utf-8")
        loop_dual_write = "DailyNewsImporter" in text or "TaskStore" in text
        import_cli = (repo / "src/loop_pilot/cli_tasks.py").is_file() and "import-daily-news" in (
            repo / "src/loop_pilot/cli_tasks.py"
        ).read_text(encoding="utf-8")
        ok = loop_dual_write or (import_cli and import_test.is_file())
        record(
            "DailyNews -> inbox path",
            "loop dual-write or inbox import-daily-news + test",
            ok,
            "loop integrated" if loop_dual_write else "import-daily-news CLI + integration test",
        )

    return results, ready


def _extract_inbox_id(output: str) -> str | None:
    for pattern in (
        r"Inbox item created:\s*(\S+)",
        r"\b(inb_[a-f0-9]+)\b",
        r"\b(inbox-[a-f0-9-]+)\b",
        r"\bid:\s*(\S+)",
        r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b",
    ):
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def run_acceptance(repo: Path, *, config_dir: str) -> list[StepResult]:
    results: list[StepResult] = []
    readiness, ready = _readiness_checks(repo)
    results.extend(readiness)

    def record(name: str, cmd: list[str], passed: bool, summary: str, notes: list[str] | None = None) -> None:
        results.append(StepResult(name, _display(cmd), passed, summary, notes or []))

    if not ready:
        record(
            "0.4-b readiness gate",
            [sys.executable, "-c", "readiness"],
            False,
            "NOT READY — implement 0.4-b before full acceptance",
            [
                "Wire cli_tasks (inbox/queue/today) into src/loop_pilot/cli.py via app.add_command",
                "Add tests/unit/test_inbox_queue.py; update test_db_ops for schema v2",
                "Integrate DailyNews candidate-actions -> SQLite inbox (dual-write with artifact)",
                "Run full acceptance commands in docs/development/44-personal-daily-loop-0.4b-acceptance.md",
            ],
        )
        return results

    record("0.4-b readiness gate", [sys.executable, "-c", "readiness"], True, "all prerequisites present")

    # 0.4-a regression on sqlite config
    for name, args in [
        ("0.4-a db migrate", ("db", "migrate")),
        ("0.4-a db verify", ("db", "verify")),
    ]:
        cmd = _loop_pilot(*args, config_dir=config_dir)
        proc = _run(cmd, cwd=repo)
        ok = proc.returncode == 0 and "error" not in (proc.stdout + proc.stderr).lower()[:200]
        record(name, cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cfg_path = repo / config_dir / "loop-pilot.yaml"
    db_path = repo / "var/state/loop_pilot.db"
    if cfg_path.is_file():
        import yaml

        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        sqlite_rel = cfg.get("runtime", {}).get("sqlite_path", "var/state/loop_pilot.db")
        db_path = repo / sqlite_rel

    tables = _schema_tables(db_path)
    missing_tables = [t for t in REQUIRED_TABLES if t not in tables]
    record(
        "schema tables",
        [sys.executable, "-c", f"tables in {db_path}"],
        not missing_tables,
        f"tables={sorted(tables)}" if not missing_tables else f"missing: {missing_tables}",
    )

    # Task flow
    cmd = _loop_pilot("inbox", "add", "fix login test", "--source", "manual", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    inbox_id = _extract_inbox_id(proc.stdout + proc.stderr)
    record(
        "inbox add",
        cmd,
        proc.returncode == 0 and inbox_id is not None,
        f"id={inbox_id}, rc={proc.returncode}",
    )

    cmd = _loop_pilot("inbox", "list", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    listed = inbox_id and inbox_id in (proc.stdout + proc.stderr) if inbox_id else False
    record("inbox list", cmd, proc.returncode == 0 and listed, f"listed={listed}, rc={proc.returncode}")

    if inbox_id:
        cmd = _loop_pilot("queue", "promote", inbox_id, config_dir=config_dir)
        proc = _run(cmd, cwd=repo)
        queue_id_match = re.search(r"que_[a-f0-9]+", proc.stdout + proc.stderr)
        queue_id = queue_id_match.group(0) if queue_id_match else None
        record("queue promote", cmd, proc.returncode == 0, proc.stdout.strip() or f"rc={proc.returncode}")
    else:
        queue_id = None

    cmd = _loop_pilot("queue", "list", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    output = proc.stdout + proc.stderr
    in_queue = queue_id and queue_id in output if queue_id else proc.returncode == 0 and "queued" in output.lower()
    record("queue list", cmd, proc.returncode == 0 and in_queue, f"in_queue={in_queue}, rc={proc.returncode}")

    cmd = _loop_pilot("today", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    record("today", cmd, proc.returncode == 0 and bool(proc.stdout.strip()), proc.stdout.strip()[:120] or f"rc={proc.returncode}")

    cmd = [sys.executable, "-m", "pytest", "-q", "tests/", "-k", "inbox or queue or today"]
    proc = _run(cmd, cwd=repo)
    record("pytest inbox/queue/today", cmd, proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = [sys.executable, "-m", "ruff", "check", str(repo)]
    proc = _run(cmd, cwd=repo)
    record("ruff check", cmd, proc.returncode == 0, "OK" if proc.returncode == 0 else (proc.stderr or proc.stdout or f"rc={proc.returncode}")[:120])

    cmd = _loop_pilot("doctor", config_dir=config_dir)
    proc = _run(cmd, cwd=repo)
    record("doctor (sqlite)", cmd, proc.returncode == 0, proc.stdout.strip().splitlines()[0] if proc.stdout else f"rc={proc.returncode}")

    # JSON backend must not fake-success inbox commands
    cmd = [sys.executable, "-m", "loop_pilot.cli", "inbox", "list"]
    proc = _run(cmd, cwd=repo)
    json_ok = proc.returncode != 0 or "No such command" in (proc.stdout + proc.stderr)
    record(
        "json backend no fake inbox",
        _display(cmd),
        json_ok,
        "not registered or clear error" if json_ok else "unexpected success on json backend",
    )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="0.4-b executable acceptance (inbox/queue/today)")
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
        print(f"# 0.4-b acceptance ({status}): {passed}/{total} passed\n")
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
