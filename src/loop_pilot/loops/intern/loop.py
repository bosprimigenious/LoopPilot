"""InternLoop Mini — synthetic Git fixture with real pytest."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

from loop_pilot.adapters.blocked_trace import append_adapter_blocked_event, adapter_trace_artifact_ref
from loop_pilot.adapters.errors import AdapterBlockedError
from loop_pilot.adapters.factory import create_adapter
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
from loop_pilot.loops.fixture_validation import validate_intern_fixture, validate_intern_workspace
from loop_pilot.loops.intern.workspace import (
    cleanup_workspace,
    create_approved_worktree,
    git_diff_summary,
    prepare_git_worktree,
)
from loop_pilot.models.router import ModelRouter
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.review.service import mark_patch_run_waiting_review
from loop_pilot.reporting.human_review import (
    recommended_for_outcome,
    write_next_actions,
    write_review_required,
)
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.state_machine import StateMachine
from loop_pilot.runtime.terminal_artifacts import finalize_terminal_artifacts
from loop_pilot.runtime.trace import TraceWriter
from loop_pilot.tools.broker import ToolBroker
from loop_pilot.tools.policy import ToolPolicy
from loop_pilot.workspaces import WorkspaceSpec


class InternLoop:
    FIXTURE_ROOT = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "intern"

    @classmethod
    def _resolve_fixture_root(cls) -> Path:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "tests" / "fixtures" / "intern"
            if candidate.is_dir():
                return candidate
        cwd_candidate = Path("tests/fixtures/intern")
        if cwd_candidate.is_dir():
            return cwd_candidate
        return cls.FIXTURE_ROOT

    def __init__(
        self,
        artifact_dir: Path,
        policy: PolicyEngine,
        renderer: ReportRenderer,
        budget_manager: BudgetManager | None = None,
        router: ModelRouter | None = None,
        tool_broker: ToolBroker | None = None,
    ) -> None:
        self.artifact_dir = artifact_dir
        self.policy = policy
        self.renderer = renderer
        self.budget_manager = budget_manager or BudgetManager(BudgetPolicy(max_model_calls=8))
        self.router = router or ModelRouter({"roles": {}, "adapters": {"mock": {"kind": "mock"}}})
        self.tool_broker = tool_broker or ToolBroker(
            ToolPolicy(allowed_commands=["pytest", "python", "git"])
        )
        self.state_machine = StateMachine()

    def run(
        self,
        request: RunRequest,
        record: RunRecord,
        *,
        phase_hook: Callable[[RunRecord], None] | None = None,
        resume_from: dict[str, Any] | None = None,
        workspace_spec: WorkspaceSpec | None = None,
    ) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        self._phase_hook = phase_hook
        record.dry_run = request.dry_run
        record.fixture = request.fixture
        workspace_root: Path | None = None
        expected_dir: Path | None = None
        fixture_name = request.fixture or "simple_python_bug"

        if workspace_spec is not None:
            workspace_root = workspace_spec.root
            fixture_dir = workspace_root
            record.fixture = workspace_spec.workspace_id
            validation = validate_intern_workspace(workspace_root)
            allowed_paths = workspace_spec.allowed_paths
            forbidden_paths = workspace_spec.forbidden_paths
            plan_target = "src/calculator.py"
            expected_dir = workspace_root / "expected"
        else:
            fixture_dir = self._resolve_fixture_root() / fixture_name
            validation = validate_intern_fixture(fixture_dir)
            allowed_paths = ["src/**", "tests/**"]
            forbidden_paths = [".env*", "secrets/**"]
            plan_target = "src/calculator.py"
            if fixture_name == "unsafe_path_change":
                plan_target = ".env.local"

        run_dir = self.artifact_dir / "intern" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")
        adapter_trace = TraceWriter(run_dir / "adapter-call-trace.jsonl")

        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []
        try:
            adapter = create_adapter(
                self.router,
                "coding_agent",
                fixture_dir=fixture_dir,
                artifact_dir=self.artifact_dir,
                adapter_override=request.adapter_override,
            )
        except AdapterBlockedError as exc:
            append_adapter_blocked_event(
                adapter_trace,
                blocked_reason=exc.reason,
                dry_run=request.dry_run,
                allow_real_adapters=self.router.allow_real_adapters,
                adapter_id=request.adapter_override,
            )
            artifacts.append(adapter_trace_artifact_ref(run_dir, record.run_id))
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = exc.message
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        if not validation.ok:
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = validation.blocked_reason
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        resume_phase = RunPhase(resume_from["phase"]) if resume_from else None
        resume_payload = resume_from.get("payload", {}) if resume_from else {}
        start_round = int(resume_payload.get("current_round", 1)) or 1
        skip_to_acting = resume_phase in {RunPhase.WAITING_APPROVAL, RunPhase.ACTING, RunPhase.EVALUATING}
        if resume_payload.get("event") == "interrupted" and resume_payload.get("resume_allowed"):
            resume_phase = RunPhase.ACTING
            skip_to_acting = True
        if resume_phase == RunPhase.EVALUATING and resume_payload.get("event") == "interrupted":
            resume_phase = RunPhase.ACTING
            skip_to_acting = True

        if skip_to_acting:
            if resume_phase == RunPhase.WAITING_APPROVAL:
                self._transition(record, RunPhase.ACTING, trace)
            start_round = max(start_round, 1)
        else:
            self._enter_observing(record, trace)
            self._transition(record, RunPhase.SELECTING, trace)
            self._transition(record, RunPhase.PLANNING, trace)

        if not skip_to_acting:
            self._transition(record, RunPhase.POLICY_CHECK, trace)
            decision = self.policy.check_write(plan_target, allowed_paths, forbidden_paths, request.dry_run)
            if not decision.allowed:
                record.terminal_reason = f"{decision.rule_id}: {decision.message}"
                return self._finalize_blocked(record, trace, run_dir, record.terminal_reason, artifacts, rounds)

        work_dir: Path | None = None
        temp_root: Path | None = None
        try:
            work_dir, temp_root = self._prepare_workspace(
                fixture_dir, request.dry_run, workspace_spec=workspace_spec
            )
            tests_passed = False
            max_rounds = record.budgets.max_rounds

            for round_num in range(start_round, max_rounds + 1):
                self.budget_manager.consume_round(record)
                round_started = rfc3339()
                record.current_round = round_num

                try:
                    if record.phase != RunPhase.ACTING:
                        self._transition(record, RunPhase.ACTING, trace)
                    elif self._phase_hook is not None:
                        self._phase_hook(record)
                    adapter_result = adapter.execute({"role": "coding", "round": round_num, "dry_run": request.dry_run})
                    self.budget_manager.consume_model_call(record)
                    adapter_trace.append(
                        {
                            "event": "adapter_call",
                            "round": round_num,
                            "status": adapter_result.status,
                            "duration_ms": adapter_result.duration_ms,
                        }
                    )

                    if round_num >= 2 and self._should_apply_controlled_fix(request, work_dir):
                        self._apply_fix(work_dir)

                    self._transition(record, RunPhase.EVALUATING, trace)
                    test_report = self._run_pytest(
                        work_dir, request.dry_run, fixture_dir, round_num, expected_dir=expected_dir
                    )
                except (InterruptedError, TimeoutError, OSError) as exc:
                    record.current_round = round_num
                    record.outcome = RunOutcome.FAILED
                    record.terminal_reason = f"ACTING interrupted: {exc}"
                    trace.append({"event": "interrupted", "round": round_num, "error": str(exc)})
                    return self._finalize(record, trace, run_dir, artifacts, rounds)
                test_artifact = self._save_text(run_dir, f"test-report-round-{round_num:02d}.md", test_report, "test_runner")
                artifacts.append(test_artifact)

                evaluation = self._evaluate_tests(
                    test_report,
                    round_num,
                    can_retry=self.budget_manager.can_retry(record),
                )
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
                    if self._should_apply_controlled_fix(request, work_dir):
                        try:
                            self._apply_fix(work_dir)
                        except (InterruptedError, TimeoutError, OSError) as exc:
                            record.outcome = RunOutcome.FAILED
                            record.terminal_reason = f"ACTING interrupted: {exc}"
                            trace.append({"event": "interrupted", "round": round_num, "error": str(exc)})
                            return self._finalize(record, trace, run_dir, artifacts, rounds)
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
            patch_artifact = self._save_text(run_dir, "patch.diff", diff_summary, "worker")
            artifacts.append(patch_artifact)

            tool_results = {
                "pytest_rounds": len(rounds),
                "adapter_calls": round_num,
                "dry_run": request.dry_run,
                "audit": self.tool_broker.audit_records(),
            }
            tool_artifact = self._save_json(run_dir, "tool-results.json", tool_results, "tool_broker")
            artifacts.append(tool_artifact)

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

            review_action = recommended_for_outcome(record.outcome)
            artifacts.append(
                write_review_required(
                    run_dir,
                    record,
                    recommended=review_action,
                    rationale=record.terminal_reason or "Review development report and test artifacts.",
                    checklist=[
                        "Verify pytest evidence matches expected fix",
                        "Confirm no forbidden paths were touched",
                        "Approve merge or request another iteration",
                    ],
                )
            )
            next_steps = (
                ["Merge fix after human approval"]
                if tests_passed
                else ["Inspect failing tests", "Apply fix manually or rerun without --review-only"]
            )
            artifacts.append(write_next_actions(run_dir, record, next_steps))

            return self._finalize(record, trace, run_dir, artifacts, rounds)

        finally:
            cleanup_workspace(temp_root)

    def _prepare_workspace(
        self,
        fixture_dir: Path,
        dry_run: bool,
        *,
        workspace_spec: WorkspaceSpec | None = None,
        intern_config: dict[str, Any] | None = None,
    ) -> tuple[Path, Path | None]:
        if workspace_spec is not None:
            root = workspace_spec.root
            if dry_run:
                return root, None
            if (root / ".git").exists():
                worktree_root = self.artifact_dir / "intern-worktrees" / workspace_spec.workspace_id
                worktree = create_approved_worktree(
                    root.resolve(),
                    worktree_root,
                    branch="HEAD",
                    worktree_name=f"run-{workspace_spec.workspace_id}",
                )
                return worktree, worktree_root
            return prepare_git_worktree(root, dry_run)

        intern_config = intern_config or {}
        workspace = Path(str(intern_config.get("workspace", "")))
        if (
            not dry_run
            and intern_config.get("use_worktree")
            and workspace.exists()
            and (workspace / ".git").exists()
        ):
            worktree_root = self.artifact_dir / "intern-worktrees" / fixture_dir.name
            worktree = create_approved_worktree(
                workspace.resolve(),
                worktree_root,
                branch=str(intern_config.get("default_branch", "HEAD")),
                worktree_name=f"run-{fixture_dir.name}",
            )
            return worktree, worktree_root
        return prepare_git_worktree(fixture_dir / "input", dry_run)

    def _should_apply_controlled_fix(self, request: RunRequest, work_dir: Path | None) -> bool:
        return bool(work_dir) and not request.dry_run and not request.review_only

    def _apply_fix(self, work_dir: Path) -> None:
        target = work_dir / "src" / "calculator.py"
        if not target.exists():
            return
        allowed = ["src/**", "tests/**"]
        forbidden = [".env*", "secrets/**"]
        content = self.tool_broker.read_file(target, allowed=allowed, forbidden=forbidden)
        if "def add" not in content:
            return
        add_block, separator, remainder = content.partition("def subtract")
        if "return a - b" not in add_block:
            return
        patched = add_block.replace("return a - b", "return a + b", 1)
        if separator:
            patched += separator + remainder
        self.tool_broker.write_file(
            target, patched, allowed=allowed, forbidden=forbidden, dry_run=False
        )
        self._clear_pycache(work_dir)

    def _clear_pycache(self, work_dir: Path) -> None:
        for cache_dir in work_dir.rglob("__pycache__"):
            shutil.rmtree(cache_dir, ignore_errors=True)

    def _run_pytest(
        self,
        work_dir: Path | None,
        dry_run: bool,
        fixture_dir: Path,
        round_num: int,
        *,
        expected_dir: Path | None = None,
    ) -> str:
        if dry_run:
            if round_num == 1:
                return "exit_code=1\n\nstdout:\n1 failed\n\nstderr:\nAssertionError"
            expected_root = expected_dir or fixture_dir / "expected"
            expected = expected_root / f"test-report-round-{round_num:02d}.md"
            if expected.exists():
                return self.tool_broker.read_file(expected, allowed=["**"])
            return "DRY_RUN: pytest simulated PASS"
        if work_dir is None:
            return "exit_code=1\n\nstdout:\nno workspace\n"

        if round_num >= 2:
            self._clear_pycache(work_dir)

        cmd_result = self.tool_broker.run_command(
            [sys.executable, "-m", "pytest", "-q"], cwd=work_dir, timeout=60
        )
        exit_code = cmd_result.exit_code if cmd_result.exit_code is not None else 1
        return (
            f"exit_code={exit_code}\n\nstdout:\n{cmd_result.stdout}\n\nstderr:\n{cmd_result.stderr}"
        )

    def _evaluate_tests(
        self,
        test_report: str,
        round_num: int,
        *,
        can_retry: bool,
    ) -> EvaluationResult:
        passed = "exit_code=0" in test_report or "1 passed" in test_report
        if not passed:
            lowered = test_report.lower()
            passed = "passed" in lowered and "failed" not in lowered
        if passed:
            verdict = EvaluationVerdict.PASS.value
        elif can_retry:
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

    def _save_json(self, run_dir: Path, name: str, data: object, created_by: str) -> ArtifactReference:
        path = run_dir / name
        content = json.dumps(data, indent=2)
        path.write_text(content, encoding="utf-8")
        return ArtifactReference(
            artifact_id=f"{run_dir.name}-{name}",
            kind="log",
            path=str(path),
            media_type="application/json",
            sha256=content_hash({"content": content}),
            size_bytes=len(content.encode()),
            created_by=created_by,
        )

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
        if phase == RunPhase.ACTING:
            record.current_round = max(record.current_round, 1)
        hook = getattr(self, "_phase_hook", None)
        if hook is not None:
            hook(record)

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
        record.finished_at = rfc3339()
        trace.append({"event": "terminated", "outcome": record.outcome.value if record.outcome else None})

        has_patch = (run_dir / "patch.diff").exists()
        patch_decided = record.review_status in {"approved", "rejected", "cancelled"}
        if has_patch and not patch_decided:
            record = mark_patch_run_waiting_review(artifact_dir=self.artifact_dir, record=record)
        else:
            record.phase = RunPhase.TERMINATED
            if record.report_status in {None, "needs_review"}:
                record.report_status = "generated"
            finalize_terminal_artifacts(run_dir, record)

        manifest_payload = json.loads((run_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
        manifest = ArtifactManifest(
            run_id=record.run_id,
            artifacts=artifacts,
            terminal_outcome=manifest_payload.get("terminal_outcome"),
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
