"""Anti-cheat tests for verify_0_4_acceptance.py."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _load_script() -> ModuleType:
    path = ROOT / "scripts" / "verify_0_4_acceptance.py"
    spec = importlib.util.spec_from_file_location("verify_0_4_acceptance", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_ready_when_pytest_fails() -> None:
    module = _load_script()
    results = [
        module.StepResult("ruff check", "ruff", True, "ok"),
        module.StepResult("pytest full suite", "pytest", False, "failed"),
    ]
    assert not module._acceptance_ready(results)


def test_verify_script_exists() -> None:
    assert (ROOT / "scripts" / "verify_0_4_acceptance.py").is_file()


def test_verify_0_4_imports_without_package_install() -> None:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_0_4_acceptance.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "Truthful 0.4 aggregate acceptance gate" in proc.stdout


def test_verify_0_4_returns_nonzero_when_prereq_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_script()

    def fake_run(
        cmd: list[str],
        *,
        cwd: Path,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if "ruff" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")
        return subprocess.CompletedProcess(cmd, 1, stdout="FAILED", stderr="")

    monkeypatch.setattr(module, "_run", fake_run)
    results = module.run_acceptance(ROOT, config_dir="unused")
    assert not module._acceptance_ready(results)
