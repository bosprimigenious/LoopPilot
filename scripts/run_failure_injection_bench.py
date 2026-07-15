#!/usr/bin/env python3
"""PR #8 semantic runtime CI bench harness.

This first harness binds each PR #8 fault-injection row to the executable
oracle that guards it today. It does not yet mutate source code or historical
commits; use the output as failure-driven design evidence, not broad benchmark
results.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTEST = (sys.executable, "-m", "pytest")


@dataclass(frozen=True)
class FaultCase:
    fault_id: str
    injected_fault: str
    terminal_lie_type: str
    oracle_command: tuple[str, ...]
    expected_block: str
    evidence_status: str = "oracle-bound"


CASES: tuple[FaultCase, ...] = (
    FaultCase(
        "FI-1",
        "Patch run finalizes succeeded while gate_result remains needs_review.",
        "False completion",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_review_service_patch_gate.py::test_patch_run_phase_is_waiting_approval_before_approve",
            "tests/unit/test_review_service_patch_gate.py::test_patch_run_writes_needs_review_gate_before_approval",
            "tests/unit/test_review_service_patch_gate.py::test_patch_run_is_needs_review_not_completed_in_summary",
        ),
        "Run held at WAITING_APPROVAL/PARTIAL and excluded from Completed summary.",
    ),
    FaultCase(
        "FI-2",
        "Manifest is written before all final artifacts exist.",
        "Evidence drift",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_terminal_artifacts.py::test_terminal_artifacts_manifest_checksums_match_final_files",
        ),
        "Finalizer recomputes disk state before sealing checksums.",
    ),
    FaultCase(
        "FI-3",
        "artifact-manifest.json appears inside its own artifact list.",
        "Evidence drift",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_terminal_artifacts.py::test_manifest_does_not_include_self_checksum",
            "tests/unit/test_terminal_artifacts.py::test_artifact_manifest_excludes_itself",
        ),
        "Manifest self-entry is rejected.",
    ),
    FaultCase(
        "FI-4",
        "diff-summary.md is promoted as the canonical human report.",
        "Report misdirection",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_summary_collector.py::test_report_path_prefers_actual_report_over_diff_summary",
        ),
        "Summary picks canonical loop report or manifest report entry.",
    ),
    FaultCase(
        "FI-5",
        "review_suggestion.json is written after artifact finalization.",
        "Evidence drift",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_review_service_patch_gate.py::test_review_suggestion_included_in_final_manifest",
        ),
        "Review suggestion is written before finalizer and appears in manifest.",
    ),
    FaultCase(
        "FI-6",
        "Terminal trace is appended before review gating downgrades outcome.",
        "Trace dishonesty",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_terminal_artifacts.py::test_patch_run_trace_reflects_needs_review_not_succeeded",
        ),
        "Trace records post-gate PARTIAL/WAITING_APPROVAL state.",
    ),
    FaultCase(
        "FI-7",
        "Deferred review item is reset to pending during sync.",
        "Human decision erasure",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_review_store.py::test_deferred_review_item_survives_sync_until_due_date",
        ),
        "deferred_until survives sync; terminal decisions remain terminal.",
    ),
    FaultCase(
        "FI-8",
        "Approved patch run becomes resume_requested instead of terminal success.",
        "Recovery misclassification",
        (
            *PYTEST,
            "-q",
            "tests/unit/test_review_service_patch_gate.py::test_approve_patch_run_finalizes_directly",
            "tests/unit/test_review_service_patch_gate.py::test_approved_patch_run_does_not_enter_resume_requested",
        ),
        "Approve directly admits terminal success; resume rejects finalized run.",
    ),
    FaultCase(
        "FI-9",
        "Prep-stage schedule install or unattended daily is allowed.",
        "Boundary violation",
        (sys.executable, "scripts/verify_0_5_prep.py"),
        "Prep stage denies schedule install and unattended paths.",
    ),
)


def _case_rows(*, execute_oracles: bool) -> list[dict]:
    rows: list[dict] = []
    for case in CASES:
        row = asdict(case)
        row["oracle_command"] = list(case.oracle_command)
        row["observed_status"] = "not_run"
        row["returncode"] = None
        row["stdout_tail"] = ""
        row["stderr_tail"] = ""
        if execute_oracles:
            proc = subprocess.run(  # noqa: S603
                case.oracle_command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            row["returncode"] = proc.returncode
            row["observed_status"] = "pass" if proc.returncode == 0 else "fail"
            row["stdout_tail"] = "\n".join(proc.stdout.splitlines()[-6:])
            row["stderr_tail"] = "\n".join(proc.stderr.splitlines()[-6:])
        rows.append(row)
    return rows


def _print_text(rows: list[dict], *, execute_oracles: bool) -> None:
    mode = "oracle execution" if execute_oracles else "plan only"
    print(f"failure-injection bench: {mode} ({len(rows)} cases)")
    for row in rows:
        command = " ".join(row["oracle_command"])
        print(f"  {row['observed_status'].upper():8} {row['fault_id']}: {row['terminal_lie_type']}")
        print(f"           oracle: {command}")
        print(f"           block:  {row['expected_block']}")
        if execute_oracles and row["observed_status"] == "fail":
            if row["stdout_tail"]:
                print(f"           stdout: {row['stdout_tail']}")
            if row["stderr_tail"]:
                print(f"           stderr: {row['stderr_tail']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-oracles",
        action="store_true",
        help="run the non-mutating oracle commands bound to each fault case",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    rows = _case_rows(execute_oracles=args.execute_oracles)
    if args.json:
        print(json.dumps({"cases": rows}, indent=2))
    else:
        _print_text(rows, execute_oracles=args.execute_oracles)
    return 0 if all(row["observed_status"] != "fail" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
