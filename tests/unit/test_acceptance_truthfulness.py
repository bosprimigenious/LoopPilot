"""Acceptance scripts must never report READY when any required check fails."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str) -> ModuleType:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "script_name",
    [
        "verify_0_4b_acceptance.py",
        "verify_0_4c_acceptance.py",
        "verify_0_4d_acceptance.py",
    ],
)
def test_ready_requires_every_recorded_check_to_pass(script_name: str) -> None:
    module = _load_script(script_name)
    results = [
        module.StepResult("static readiness", "exists", True, "present"),
        module.StepResult("runtime verification", "pytest", False, "failed"),
    ]

    assert not module._acceptance_ready(results)


@pytest.mark.parametrize(
    "script_name",
    [
        "verify_0_4b_acceptance.py",
        "verify_0_4c_acceptance.py",
        "verify_0_4d_acceptance.py",
    ],
)
def test_runtime_failure_prints_not_ready_and_returns_nonzero(
    script_name: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_script(script_name)
    results = [
        module.StepResult("static readiness", "exists", True, "present"),
        module.StepResult("runtime verification", "pytest", False, "failed"),
    ]
    monkeypatch.setattr(module, "run_acceptance", lambda repo, config_dir: results)
    monkeypatch.setattr(sys, "argv", [script_name, "--cwd", str(ROOT)])

    assert module.main() != 0
    assert "(NOT READY)" in capsys.readouterr().out


def test_0_4d_stops_when_0_4c_prerequisite_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_script("verify_0_4d_acceptance.py")
    monkeypatch.setattr(module, "_readiness_checks", lambda repo: ([], True))
    commands: list[list[str]] = []

    def fake_run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        commands.append(cmd)
        failed = cmd[1].endswith("verify_0_4c_acceptance.py")
        return subprocess.CompletedProcess(
            cmd,
            2 if failed else 0,
            stdout="# acceptance (NOT READY)" if failed else "# acceptance (READY)",
            stderr="",
        )

    monkeypatch.setattr(module, "_run", fake_run)
    results = module.run_acceptance(ROOT, config_dir="unused")

    by_name = {result.name: result for result in results}
    assert not by_name["prerequisite 0.4-c acceptance"].passed
    assert "0.4-a db migrate" not in by_name
    assert any(cmd[1].endswith("verify_0_4c_acceptance.py") for cmd in commands)
