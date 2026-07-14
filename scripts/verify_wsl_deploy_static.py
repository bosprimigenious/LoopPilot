#!/usr/bin/env python3
"""Static guard for the WSL deployment entrypoint."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY_SCRIPT = ROOT / "scripts" / "deploy_wsl.sh"


def _check(name: str, fn) -> tuple[str, bool, str]:
    try:
        detail = fn()
    except Exception as exc:  # noqa: BLE001
        return name, False, str(exc)
    return name, True, detail or "PASS"


def _source() -> str:
    if not DEPLOY_SCRIPT.is_file():
        raise AssertionError("scripts/deploy_wsl.sh is missing")
    return DEPLOY_SCRIPT.read_text(encoding="utf-8")


def _require_markers(source: str, markers: tuple[str, ...], *, label: str) -> None:
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise AssertionError(f"{label} missing markers: {', '.join(missing)}")


def check_options_and_env() -> str:
    source = _source()
    _require_markers(
        source,
        (
            "--repo-dir PATH",
            "--repo-url URL",
            "--skip-full-tests",
            "--skip-acceptance",
            "--skip-api-smoke",
            "--no-pull",
            "LOOPPILOT_REPO_DIR",
            "LOOPPILOT_REPO_URL",
            "LOOPPILOT_SKIP_FULL_TESTS",
            "LOOPPILOT_SKIP_ACCEPTANCE",
            "LOOPPILOT_SKIP_API_SMOKE",
            "LOOPPILOT_API_SMOKE_PORT",
            "LOOPPILOT_NO_PULL",
            "PYTHON_BIN=python3.11",
        ),
        label="usage/options",
    )
    return "documented flags and environment overrides"


def check_prerequisites() -> str:
    source = _source()
    _require_markers(
        source,
        (
            "set -Eeuo pipefail",
            "require_command git",
            'require_command "$PYTHON_BIN"',
            "check_python",
            "LoopPilot requires Python >= 3.11",
            "Python venv module is missing",
            "sudo apt-get update && sudo apt-get install -y git python3 python3-venv",
            'case "$(uname -s)"',
        ),
        label="prerequisites",
    )
    return "Linux, git, Python, venv, and apt hints"


def check_deployment_gates() -> str:
    source = _source()
    _require_markers(
        source,
        (
            "run loop-pilot doctor",
            "run loop-pilot adapters doctor",
            "run ruff check .",
            "run python scripts/verify_wsl_deploy_static.py",
            "run python scripts/verify_api_bridge_contract.py",
            "run python scripts/verify_wechat_miniprogram_static.py",
            "run python -m pytest -q",
            "run python scripts/verify_0_3_acceptance.py",
            "run python scripts/verify_0_4_acceptance.py",
            "run python scripts/verify_0_5_prep.py",
            "run loop-pilot run all --fixture-set mini --dry-run",
            "run loop-pilot status",
        ),
        label="deployment gates",
    )
    return "health, static, tests, acceptance, and CLI smoke gates"


def check_api_smoke() -> str:
    source = _source()
    _require_markers(
        source,
        (
            "api_bridge_smoke()",
            'loop-pilot api serve --host 127.0.0.1 --port "$API_SMOKE_PORT"',
            "/api/health",
            'data.get("readOnly") is True',
            'data.get("mutationsEnabled") is False',
            '"/api/reviews/{run_id}" in data.get("endpoints", [])',
            'kill "$api_pid"',
            'wait "$api_pid"',
            "API bridge smoke: OK",
        ),
        label="API smoke",
    )
    return "read-only bridge health smoke"


def check_final_output() -> str:
    source = _source()
    _require_markers(
        source,
        (
            'LOG_DIR="var/logs"',
            "wsl-deploy-$(date -u +%Y%m%dT%H%M%SZ).log",
            "LoopPilot WSL deployment verified",
            "Repository: %s",
            "Activate:   source %s/.venv/bin/activate",
            "Log file:   %s/%s",
        ),
        label="final output",
    )
    return "repo, venv, and log summary"


def main() -> int:
    checks = [
        _check("options_and_env", check_options_and_env),
        _check("prerequisites", check_prerequisites),
        _check("deployment_gates", check_deployment_gates),
        _check("api_smoke", check_api_smoke),
        _check("final_output", check_final_output),
    ]
    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print(f"wsl-deploy static: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks)")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
