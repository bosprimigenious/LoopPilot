#!/usr/bin/env python3
"""Run 0.3 executable acceptance (L1+L2+L3) without real credentials.

Skips DeepSeek live calls and any command requiring --allow-real-adapters.
Safe for CI: no network, no API keys, no Cursor CLI required.
"""

from __future__ import annotations

import argparse
import json
import re
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


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def _display(cmd: list[str]) -> str:
    shown = ["python" if part == sys.executable else part for part in cmd]
    if shown[:3] == ["python", "-m", "loop_pilot.cli"]:
        shown = ["loop-pilot", *shown[3:]]
    return " ".join(shown)


def _loop_pilot(*args: str) -> list[str]:
    return [sys.executable, "-m", "loop_pilot.cli", *args]


def _outcome(output: str) -> str | None:
    match = re.search(r"completed:\s*(\w+)", output, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    if re.search(r"\b(?:intern|paper|daily_news):\s*\w+", output, re.IGNORECASE):
        return "composite"
    return None


def _check_daily_news_candidates(artifact_dir: Path, run_id_hint: str | None = None) -> tuple[bool, str]:
    base = artifact_dir / "daily-news"
    if not base.is_dir():
        return False, "var/artifacts/daily-news missing"
    dirs = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    for run_dir in dirs:
        if not run_dir.is_dir():
            continue
        required = ["intern-candidates.md", "paper-candidates.md", "candidate-actions.json"]
        missing = [name for name in required if not (run_dir / name).is_file()]
        if not missing:
            return True, f"{run_dir.name}: {', '.join(required)}"
    return False, "no daily-news run with all three candidate files"


def run_acceptance(repo: Path) -> list[StepResult]:
    results: list[StepResult] = []
    artifact_dir = repo / "var" / "artifacts"

    def record(name: str, cmd: list[str], passed: bool, summary: str, notes: list[str] | None = None) -> None:
        results.append(StepResult(name, _display(cmd), passed, summary, notes or []))

    # L1.1 Mini
    mini_cmds: list[tuple[str, list[str], str | set[str]]] = [
        ("L1.1 intern fixture", _loop_pilot("run", "intern", "--fixture", "simple_python_bug", "--dry-run"), "partial"),
        ("L1.1 paper fixture", _loop_pilot("run", "paper", "--fixture", "unsupported_claim", "--dry-run"), "partial"),
        ("L1.1 daily-news fixture", _loop_pilot("run", "daily-news", "--fixture", "github_star_snapshots", "--dry-run"), "succeeded"),
        ("L1.1 run all mini", _loop_pilot("run", "all", "--fixture-set", "mini", "--dry-run"), {"succeeded", "partial", "composite"}),
    ]
    for name, cmd, expected in mini_cmds:
        proc = _run(cmd, cwd=repo)
        outcome = _outcome(proc.stdout + proc.stderr)
        if isinstance(expected, set):
            ok = outcome in expected and proc.returncode == 0
        else:
            ok = outcome == expected and proc.returncode == 0
        record(name, cmd, ok, f"outcome={outcome}, rc={proc.returncode}")

    ok, msg = _check_daily_news_candidates(artifact_dir)
    record(
        "L1.1 daily_news candidate artifacts",
        [sys.executable, "-c", "check candidates"],
        ok,
        msg,
    )

    # L1.2 0.2 workspace
    workspace_cmds: list[tuple[str, list[str], str]] = [
        ("L1.2 intern workspace", _loop_pilot("run", "intern", "--workspace", "examples/intern_demo", "--dry-run"), "partial"),
        ("L1.2 paper workspace", _loop_pilot("run", "paper", "--workspace", "examples/paper_demo", "--dry-run"), "partial"),
        ("L1.2 daily-news demo", _loop_pilot("run", "daily-news", "--source-profile", "demo", "--dry-run"), "succeeded"),
        ("L1.2 run all demo", _loop_pilot("run", "all", "--profile", "demo", "--dry-run"), {"succeeded", "partial", "composite"}),
    ]
    for name, cmd, expected in workspace_cmds:
        proc = _run(cmd, cwd=repo)
        outcome = _outcome(proc.stdout + proc.stderr)
        ok = outcome == expected or (name.endswith("run all demo") and proc.returncode == 0 and outcome == "composite")
        record(name, cmd, ok, f"outcome={outcome}, rc={proc.returncode}")

    # L2 Adapter core
    for name, args in [
        ("L2 adapters list", ["adapters", "list"]),
        ("L2 adapters doctor", ["adapters", "doctor"]),
    ]:
        cmd = _loop_pilot(*args)
        proc = _run(cmd, cwd=repo)
        ok = proc.returncode == 0 and "mock" in proc.stdout.lower()
        record(name, cmd, ok, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    cmd = _loop_pilot("run", "intern", "--workspace", "examples/intern_demo", "--adapter", "cursor_cli", "--dry-run")
    proc = _run(cmd, cwd=repo)
    outcome = _outcome(proc.stdout + proc.stderr)
    blocked_reason = "allow_real_adapters=false" in (proc.stdout + proc.stderr).lower()
    intern_dirs = sorted((artifact_dir / "intern").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True) if (artifact_dir / "intern").is_dir() else []
    trace_ok = False
    if intern_dirs:
        trace_path = intern_dirs[0] / "adapter-call-trace.jsonl"
        trace_ok = trace_path.is_file()
    record(
        "L2 intern cursor_cli dry-run",
        cmd,
        outcome == "blocked" and blocked_reason and trace_ok,
        f"outcome={outcome}, adapter_trace={trace_ok}",
        ["blocked runs must write adapter-call-trace.jsonl with blocked_reason"],
    )

    cmd = _loop_pilot("run", "paper", "--workspace", "examples/paper_demo", "--adapter", "deepseek", "--dry-run")
    proc = _run(cmd, cwd=repo)
    outcome = _outcome(proc.stdout + proc.stderr)
    record(
        "L2 paper deepseek dry-run",
        cmd,
        outcome == "blocked",
        f"outcome={outcome} (outer gate; live key test MANUAL)",
        ["SKIP MANUAL: no DEEPSEEK_API_KEY; missing-key path needs --allow-real-adapters"],
    )

    # L3 Safety
    for name, args, expect in [
        ("L3 cursor_cli default gate", ["run", "intern", "--workspace", "examples/intern_demo", "--adapter", "cursor_cli", "--dry-run"], "blocked"),
        ("L3 deepseek default gate", ["run", "paper", "--workspace", "examples/paper_demo", "--adapter", "deepseek", "--dry-run"], "blocked"),
    ]:
        cmd = _loop_pilot(*args)
        proc = _run(cmd, cwd=repo)
        outcome = _outcome(proc.stdout + proc.stderr)
        no_trace = "traceback" not in (proc.stdout + proc.stderr).lower()
        record(name, cmd, outcome == expect and no_trace, f"outcome={outcome}, no_traceback={no_trace}")

    cmd = _loop_pilot("run", "intern", "--adapter", "fake_adapter", "--dry-run")
    proc = _run(cmd, cwd=repo)
    outcome = _outcome(proc.stdout + proc.stderr)
    no_crash = proc.returncode == 0
    blocked = outcome == "blocked" and "unknown adapter" in (proc.stdout + proc.stderr).lower()
    record(
        "L3 fake_adapter blocked",
        cmd,
        no_crash and blocked,
        f"outcome={outcome}, rc={proc.returncode}",
        ["unknown adapter must BLOCKED, not mock fallback"],
    )

    for name, cmd in [
        ("L3 pytest", [sys.executable, "-m", "pytest", "-q"]),
        ("L3 ruff", [sys.executable, "-m", "ruff", "check", "."]),
        ("L3 doctor", _loop_pilot("doctor")),
    ]:
        proc = _run(cmd, cwd=repo)
        record(name, cmd, proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout else f"rc={proc.returncode}")

    # Secret grep (env var names in messages OK; raw sk- keys not)
    state_dir = repo / "var" / "state"
    leak = False
    if state_dir.is_dir():
        for path in state_dir.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"sk-[a-f0-9]{20,}", text, re.IGNORECASE):
                leak = True
                break
    record("L3 no raw API key leak", [sys.executable, "-c", "grep secrets"], not leak, "N/A (no key set)" if not leak else "FAIL: sk- pattern found")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="0.3 executable acceptance (no credentials)")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    results = run_acceptance(args.cwd.resolve())
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    if args.json:
        payload = {
            "passed": passed,
            "total": total,
            "results": [
                {"name": r.name, "passed": r.passed, "command": r.command, "summary": r.summary, "notes": r.notes}
                for r in results
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"# 0.3 executable acceptance: {passed}/{total} passed\n")
        for r in results:
            mark = "PASS" if r.passed else "FAIL"
            print(f"[{mark}] {r.name}")
            print(f"  $ {r.command}")
            print(f"  {r.summary}")
            for note in r.notes:
                print(f"  note: {note}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
