#!/usr/bin/env python3
"""Truthful gate for 0.5-prep fail-closed safety scaffolding."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _check(name: str, fn) -> tuple[str, bool, str]:
    try:
        fn()
        return (name, True, "PASS")
    except Exception as exc:  # noqa: BLE001
        return (name, False, str(exc))


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    def imports() -> None:
        for mod in (
            "loop_pilot.safety.readiness",
            "loop_pilot.safety.gate",
            "loop_pilot.safety.levels",
            "loop_pilot.cli_safety",
            "loop_pilot.scheduler.install_status",
        ):
            importlib.import_module(mod)

    checks.append(_check("imports", imports))

    def prep_blocks() -> None:
        from loop_pilot.config import LoopPilotConfig
        from loop_pilot.safety.gate import SafetyGate
        from loop_pilot.safety.readiness import PREP_STAGE_BLOCKED

        cfg = LoopPilotConfig(safety={"stage": "prep"}, runtime={"state_dir": "var/state"})
        result = SafetyGate.from_config(cfg).check("schedule.install", confirm=True)
        assert result.denied and result.reason_code == PREP_STAGE_BLOCKED

    checks.append(_check("prep_blocks_schedule_install", prep_blocks))

    def pytest_subset() -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_0_5_prep_safety.py",
                "tests/unit/test_safety_gate.py",
                "tests/integration/test_schedule_install.py",
                "tests/unit/test_review_store.py",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout + proc.stderr)

    checks.append(_check("pytest_subset", pytest_subset))

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    prep_ok = passed == total
    print(f"0.5-prep: {'PASS' if prep_ok else 'FAIL'} ({passed}/{total} checks)")
    print("0.5-ready: NOT READY (requires 0.4c + readiness gate + safety.stage=ready)")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if prep_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
