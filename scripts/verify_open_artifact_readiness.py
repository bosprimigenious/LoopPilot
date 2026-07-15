#!/usr/bin/env python3
"""Static guard for A-level paper artifact and open-source readiness."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _check(name: str, fn) -> tuple[str, bool, str]:
    try:
        detail = fn()
    except Exception as exc:  # noqa: BLE001
        return name, False, str(exc)
    return name, True, detail or "PASS"


def _read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"{relative} is missing")
    return path.read_text(encoding="utf-8")


def _require_markers(source: str, markers: tuple[str, ...], *, label: str) -> None:
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise AssertionError(f"{label} missing markers: {', '.join(missing)}")


def check_root_governance_docs() -> str:
    contributing = _read("CONTRIBUTING.md")
    governance = _read("GOVERNANCE.md")
    conduct = _read("CODE_OF_CONDUCT.md")
    security = _read("SECURITY.md")
    license_text = _read("LICENSE")
    _require_markers(
        contributing,
        (
            "Local Setup",
            "Validation Before a Pull Request",
            "Safety Boundaries",
            "SafetyGate",
            "ReviewService",
        ),
        label="CONTRIBUTING.md",
    )
    _require_markers(
        governance,
        (
            "Release Gate",
            "Safety Policy Changes",
            "Artifact Claim Admission",
            "commit",
            "environment",
        ),
        label="GOVERNANCE.md",
    )
    _require_markers(
        conduct,
        (
            "Expected Behavior",
            "Unacceptable Behavior",
            "Reporting",
            "Preserve safety gates",
        ),
        label="CODE_OF_CONDUCT.md",
    )
    _require_markers(
        security,
        ("Never commit", "Required controls before real execution", "human approval"),
        label="SECURITY.md",
    )
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise AssertionError("LICENSE must be Apache-2.0 text")
    return "license, security, contribution, conduct, and governance docs"


def check_readme_artifact_path() -> str:
    source = _read("README.md")
    _require_markers(
        source,
        (
            "bash scripts/deploy_wsl.sh",
            "loop-pilot api serve --host 127.0.0.1 --port 7860",
            "python scripts/verify_open_artifact_readiness.py",
            "python scripts/build_artifact_review_bundle.py",
            "python scripts/verify_wsl_deploy_static.py",
            "python scripts/verify_api_bridge_contract.py",
            "python scripts/verify_wechat_miniprogram_static.py",
            "CONTRIBUTING.md",
            "GOVERNANCE.md",
            "CODE_OF_CONDUCT.md",
        ),
        label="README.md artifact path",
    )
    return "README advertises WSL, API, mobile, governance, and validation"


def check_paper_standard_docs() -> str:
    standard = _read("paper/aa-open-source-standard.md")
    direction = _read("paper/direction.md")
    outline = _read("paper/outline.md")
    _require_markers(
        standard,
        (
            "A-level",
            "Dual gate",
            "Paper gate",
            "Open-source gate",
            "Artifact review bundle",
        ),
        label="paper standard",
    )
    _require_markers(
        direction,
        (
            "terminal-trust layer",
            "A-conference bar",
            "fault-injection",
            "without private credentials",
        ),
        label="paper direction",
    )
    _require_markers(
        outline,
        (
            "Mature Systems Direction",
            "artifact-readiness gate",
            "fault-injection map",
        ),
        label="paper outline",
    )
    return "paper standard, direction, and outline aligned"


def check_fault_injection_map() -> str:
    source = _read("paper/tables/pr8-fault-injection-map.md")
    bench = _read("scripts/run_failure_injection_bench.py")
    for fault_id in (f"FI-{index}" for index in range(1, 10)):
        if fault_id not in source:
            raise AssertionError(f"fault map missing {fault_id}")
        if f'"{fault_id}"' not in bench:
            raise AssertionError(f"bench harness missing {fault_id}")
    _require_markers(
        source,
        (
            "Injected fault",
            "Terminal lie type",
            "Oracle / guard",
            "Expected block",
            "scripts/run_failure_injection_bench.py",
        ),
        label="PR #8 fault map",
    )
    _require_markers(
        bench,
        ("--execute-oracles", "oracle_command", "expected_block", "observed_status"),
        label="failure-injection bench harness",
    )
    return "PR #8 findings mapped to FI-1..FI-9 and bench harness"


def check_artifact_bundle_generator() -> str:
    source = _read("paper/aa-open-source-standard.md")
    generator = _read("scripts/build_artifact_review_bundle.py")
    if "- [x] Artifact review bundle can be generated" not in source:
        raise AssertionError("artifact review bundle gate must be checked once generator exists")
    _require_markers(
        generator,
        (
            "git-tracked files only",
            "private_credentials_required",
            "VALIDATION_COMMANDS",
            "run_failure_injection_bench.py --execute-oracles",
            "tarfile.open",
        ),
        label="artifact review bundle generator",
    )
    return "clean-checkout artifact bundle generator exists"


def main() -> int:
    checks = [
        _check("root_governance_docs", check_root_governance_docs),
        _check("readme_artifact_path", check_readme_artifact_path),
        _check("paper_standard_docs", check_paper_standard_docs),
        _check("fault_injection_map", check_fault_injection_map),
        _check("artifact_bundle_generator", check_artifact_bundle_generator),
    ]
    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print(f"open-artifact readiness: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks)")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
