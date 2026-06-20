"""InternLoop Mini — synthetic Git fixture with real pytest."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from loop_pilot.adapters.mock_adapter import MockAdapter
from loop_pilot.domain.models import (
    ArtifactManifest,
    ArtifactReference,
    EvaluationResult,
    RoundRecord,
    RunRecord,
    RunRequest,
    content_hash,
    rfc3339,
)
from loop_pilot.domain.states import EvaluationVerdict, RunOutcome, RunPhase
from loop_pilot.loops.fixture_validation import validate_intern_fixture
from loop_pilot.loops.intern.workspace import cleanup_workspace, git_diff_summary, prepare_git_worktree
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.state_machine import StateMachine
from loop_pilot.runtime.trace import TraceWriter


class InternLoop:
    FIXTURE_ROOT = Path("tests/fixtures/intern")

    def __init__(
        self,
        artifact_dir: Path,
        policy: PolicyEngine,
        renderer: ReportRenderer,
        budget_manager: BudgetManager | None = None,
    ) -> None:
        self.artifact_dir = artifact_dir
        self.policy = policy
        self.renderer = renderer
        self.budget_manager = budget_manager or BudgetManager(BudgetPolicy(max_model_calls=8))
        self.state_machine = StateMachine()

    def run(self, request: RunRequest, record: RunRecord) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        record.dry_run = request.dry_run
        record.fixture = request.fixture
        fixture_name = request.fixture or "simple_python_bug"
        fixture_dir = self.FIXTURE_ROOT / fixture_name
        run_dir = self.artifact_dir / "intern" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")

        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []
        adapter = MockAdapter(fixture_dir)

        validation = validate_intern_fixture(fixture_dir)
        if not validation.ok:
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = validation.blocked_reason
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        self._enter_observing(record, trace)
        self._transition(record, RunPhase.SELECTING, trace)
        self._transition(record, RunPhase.PLANNING, trace)

        allowed_paths = ["src/**", "tests/**"]
        forbidden_paths = [".env*", "secrets/**"]
        plan_target = "src/calculator.py"
        if fixture_name == "unsafe_path_change":
            plan_target = ".env.local"

        self._transition(record, RunPhase.POLICY_CHECK, trace)
        decision = self.policy.check_write(plan_target, allowed_paths, forbidden_paths, request.dry_run)
        if not decision.allowed:
            record.terminal_reason = f"{decision.rule_id}: {decision.message}"
            return self._finalize_blocked(record, trace, run_dir, record.terminal_reason, artifacts, rounds)

        work_dir: Path | None = None
        temp_root: Path | None = None
        try:
            work_dir, temp_root = self._prepare_workspace(fixture_dir, request.dry_run)
            tests_passed = False
            max_rounds = record.budgets.max_rounds

            for round_num in range(1, max_rounds + 1):
                self.budget_manager.consume_round(record)
                round_started = rfc3339()

                try:
                    self._transition(record, RunPhase.ACTING, trace)
                    adapter.execute({"role": "coding", "round": round_num})
                    self.budget_manager.consume_model_call(record)

                    if round_num >= 2 and not request.dry_run and work_dir:
                        self._apply_fix(work_dir)

                    self._transition(record, RunPhase.EVALUATING, trace)
                    test_report = self._run_pytest(work_dir, request.dry_run, fixture_dir, round_num)
                except (InterruptedError, TimeoutError, OSError) as exc:
                    record.outcome = RunOutcome.FAILED
                    record.terminal_reason = f"ACTING interrupted: {exc}"
                    trace.append({"event": "interrupted", "round": round_num, "error": str(exc)})
                    return self._finalize(record, trace, run_dir, artifacts, rounds)
                test_artifact = self._save_text(run_dir, f"test-report-round-{round_num:02d}.md", test_report, "test_runner")
                artifacts.append(test_artifact)

                evaluation = self._evaluate_tests(test_report, round_num)
                round_record = RoundRecord(
                    round_id=round_num,
                    state_before=RunPhase.ACTING.value,
                    decision=evaluation.verdict,
                    reason_code=evaluation.checks[0]["check_id"] if evaluation.checks else "none",
                    started_at=round_started,
                    finished_at=rfc3339(),
                    evaluation_id=evaluation.evaluation_id,
                    output_artifacts=[test_artifact],
                )
                rounds.append(round_record)
                trace.append({"event": "round_complete", "round": round_record.to_dict()})

                if evaluation.verdict == EvaluationVerdict.PASS.value:
                    tests_passed = True
                    break

                if evaluation.verdict == EvaluationVerdict.RETRYABLE_FAIL.value:
                    if not self.budget_manager.can_retry(record):
                        record.outcome = RunOutcome.EXHAUSTED
                        break
                    self._transition(record, RunPhase.DIAGNOSING, trace)
                    self._transition(record, RunPhase.REFLECTING, trace)
                    self._transition(record, RunPhase.REPLANNING, trace)
                    self._transition(record, RunPhase.POLICY_CHECK, trace)
                    continue

                record.outcome = RunOutcome.FAILED
                break

            if tests_passed:
                record.outcome = RunOutcome.SUCCEEDED
                record.terminal_reason = "All tests passed after controlled fix"
            elif record.outcome is None:
                record.outcome = RunOutcome.FAILED
                record.terminal_reason = "Tests did not pass within budget"

            diff_summary = self._build_diff_summary(work_dir, request.dry_run)
            diff_artifact = self._save_text(run_dir, "diff-summary.md", diff_summary, "worker")
            artifacts.append(diff_artifact)

            manifest_rel = f"intern/{record.run_id}/artifact-manifest.json"
            report_body = {
                "problem": "Predefined failing test in calculator.add",
                "resolved": "yes" if tests_passed else "no",
                "evidence": diff_summary[:200],
                "next_action": "Review development-report" if tests_passed else "Manual fix required",
            }
            report_path = run_dir / "development-report.md"
            self.renderer.write_report(report_path, "intern/development-report.md", record, report_body, manifest_rel)
            artifacts.append(
                ArtifactReference(
                    artifact_id=f"{record.run_id}-development-report",
                    kind="report",
                    path=str(report_path.relative_to(self.artifact_dir.parent) if self.artifact_dir.parent in report_path.parents else report_path),
                    media_type="text/markdown",
                    sha256=content_hash({"path": str(report_path)}),
                    size_bytes=report_path.stat().st_size if report_path.exists() else 0,
                    created_by="reporting",
                )
            )

            return self._finalize(record, trace, run_dir, artifacts, rounds)

        finally:
            cleanup_workspace(temp_root)

    def _prepare_workspace(self, fixture_dir: Path, dry_run: bool) -> tuple[Path, Path | None]:
        return prepare_git_worktree(fixture_dir / "input", dry_run)

    def _apply_fix(self, work_dir: Path) -> None:
        target = work_dir / "src" / "calculator.py"
        if not target.exists():
            return
        content = target.read_text(encoding="utf-8")
        if "return a - b" in content and "def add" in content:
            target.write_text(content.replace("return a - b", "return a + b", 1), encoding="utf-8")

    def _run_pytest(self, work_dir: Path | None, dry_run: bool, fixture_dir: Path, round_num: int) -> str:
        if dry_run:
            if round_num == 1:
                return "exit_code=1\n\nstdout:\n1 failed\n\nstderr:\nAssertionError"
            expected = fixture_dir / "expected" / "test-report-round-02.md"
            if expected.exists():
                return expected.read_text(encoding="utf-8")
            return "DRY_RUN: pytest simulated PASS"
        if work_dir is None:
            return "exit_code=1\n\nstdout:\nno workspace\n"

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return f"exit_code={result.returncode}\n\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"

    def _evaluate_tests(self, test_report: str, round_num: int) -> EvaluationResult:
        passed = "passed" in test_report.lower() and "failed" not in test_report.lower()
        passed = passed or "exit_code=0" in test_report or "1 passed" in test_report
        if passed:
            verdict = EvaluationVerdict.PASS.value
        elif round_num < 2:
            verdict = EvaluationVerdict.RETRYABLE_FAIL.value
        else:
            verdict = EvaluationVerdict.FATAL.value

        return EvaluationResult(
            evaluation_id=f"eval-{round_num:02d}",
            verdict=verdict,
            checks=[
                {
                    "check_id": "pytest",
                    "status": "pass" if passed else "fail",
                    "message": "pytest result",
                    "evidence": [],
                }
            ],
        )

    def _build_diff_summary(self, work_dir: Path | None, dry_run: bool) -> str:
        if dry_run or work_dir is None:
            return "Dry-run: would patch src/calculator.py (a - b -> a + b)"
        return git_diff_summary(work_dir)

    def _save_text(self, run_dir: Path, name: str, content: str, created_by: str) -> ArtifactReference:
        path = run_dir / name
        path.write_text(content, encoding="utf-8")
        return ArtifactReference(
            artifact_id=f"{run_dir.name}-{name}",
            kind="log",
            path=str(path),
            media_type="text/markdown",
            sha256=content_hash({"content": content}),
            size_bytes=len(content.encode()),
            created_by=created_by,
        )

    def _enter_observing(self, record: RunRecord, trace: TraceWriter) -> None:
        if record.phase == RunPhase.CREATED:
            self._transition(record, RunPhase.LOCKING, trace)
        if record.phase == RunPhase.LOCKING:
            self._transition(record, RunPhase.OBSERVING, trace)

    def _transition(self, record: RunRecord, phase: RunPhase, trace: TraceWriter) -> None:
        self.state_machine.validate_transition(record.phase, phase)
        record.phase = phase
        trace.append({"event": "state_transition", "phase": phase.value, "run_id": record.run_id})

    def _finalize(
        self,
        record: RunRecord,
        trace: TraceWriter,
        run_dir: Path,
        artifacts: list[ArtifactReference],
        rounds: list[RoundRecord],
    ) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        self._transition(record, RunPhase.FINALIZING, trace)
        self._transition(record, RunPhase.PERSISTING, trace)
        self._transition(record, RunPhase.REPORTING, trace)
        record.phase = RunPhase.TERMINATED
        record.finished_at = rfc3339()
        record.report_status = "generated"
        trace.append({"event": "terminated", "outcome": record.outcome.value if record.outcome else None})

        manifest = ArtifactManifest(
            run_id=record.run_id,
            artifacts=artifacts,
            terminal_outcome=record.outcome.value if record.outcome else None,
        )
        manifest_path = run_dir / "artifact-manifest.json"
        manifest_path.write_text(
            __import__("json").dumps(manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        return record, manifest, rounds

    def _finalize_blocked(
        self,
        record: RunRecord,
        trace: TraceWriter,
        run_dir: Path,
        reason: str,
        artifacts: list[ArtifactReference],
        rounds: list[RoundRecord],
    ) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        record.outcome = RunOutcome.BLOCKED
        record.terminal_reason = reason
        return self._finalize(record, trace, run_dir, artifacts, rounds)
