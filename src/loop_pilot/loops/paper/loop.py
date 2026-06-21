"""PaperLoop Mini — unsupported claim with trusted citation fixture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from loop_pilot.adapters.factory import AdapterBlockedError, create_adapter
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
from loop_pilot.loops.fixture_validation import validate_paper_fixture, validate_paper_workspace
from loop_pilot.loops.paper.bibtex import assess_citation_support, parse_bibtex
from loop_pilot.loops.paper.workspace import create_paper_working_copy
from loop_pilot.models.router import ModelRouter
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.human_review import (
    recommended_for_outcome,
    write_next_actions,
    write_next_research_tasks,
    write_review_required,
)
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.state_machine import StateMachine
from loop_pilot.runtime.trace import TraceWriter
from loop_pilot.workspaces import WorkspaceSpec


class PaperLoop:
    FIXTURE_ROOT = Path("tests/fixtures/paper")
    UNSUPPORTED_MARKERS = ("significantly outperforms all baselines", "state-of-the-art on every benchmark")

    def __init__(
        self,
        artifact_dir: Path,
        policy: PolicyEngine,
        renderer: ReportRenderer,
        budget_manager: BudgetManager | None = None,
        router: ModelRouter | None = None,
    ) -> None:
        self.artifact_dir = artifact_dir
        self.policy = policy
        self.renderer = renderer
        self.budget_manager = budget_manager or BudgetManager(BudgetPolicy(max_model_calls=12))
        self.router = router or ModelRouter({"roles": {}, "adapters": {"mock": {"kind": "mock"}}})
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
        _ = resume_from
        read_only_patterns = ["experiments/raw/**"]
        draft_file = "paper.md"
        references_file = "references.bib"

        if workspace_spec is not None:
            fixture_dir = workspace_spec.root
            record.fixture = workspace_spec.workspace_id
            draft_file = workspace_spec.draft_file
            references_file = workspace_spec.references_file
            read_only_patterns = workspace_spec.forbidden_paths or read_only_patterns
            validation = validate_paper_workspace(
                workspace_spec.root,
                draft_file=draft_file,
                references_file=references_file,
            )
        else:
            fixture_name = request.fixture or "unsupported_claim"
            fixture_dir = self.FIXTURE_ROOT / fixture_name
            validation = validate_paper_fixture(fixture_dir)

        run_dir = self.artifact_dir / "paper" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")
        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []
        try:
            adapter = create_adapter(
                self.router,
                "analysis_medium",
                fixture_dir=fixture_dir,
                artifact_dir=self.artifact_dir,
            )
        except AdapterBlockedError as exc:
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = exc.message
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        if not validation.ok:
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = validation.blocked_reason
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        self._enter_observing(record, trace)
        for phase in (
            RunPhase.SELECTING,
            RunPhase.PLANNING,
            RunPhase.POLICY_CHECK,
        ):
            self._transition(record, phase, trace)

        if workspace_spec is not None:
            paper_path = fixture_dir / draft_file
            citations_path = fixture_dir / references_file
            working_copy: Path | None = None
            if not request.dry_run and not request.review_only:
                try:
                    working_copy = create_paper_working_copy(
                        fixture_dir,
                        run_dir / "working-copy",
                        read_only_patterns=read_only_patterns,
                    )
                    paper_path = working_copy / draft_file
                    citations_path = working_copy / references_file
                except FileNotFoundError:
                    pass
        else:
            paper_path = fixture_dir / "input" / "paper.md"
            citations_path = fixture_dir / "input" / "references.bib"
            working_copy = None
            if not request.dry_run and not request.review_only:
                try:
                    working_copy = create_paper_working_copy(
                        fixture_dir / "input",
                        run_dir / "working-copy",
                        read_only_patterns=read_only_patterns,
                    )
                    paper_path = working_copy / "paper.md"
                    citations_path = working_copy / "references.bib"
                except FileNotFoundError:
                    pass

        paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
        citations = citations_path.read_text(encoding="utf-8") if citations_path.exists() else ""

        claims = self._extract_claims(paper_text)
        evidence_map = self._map_evidence(claims, citations, adapter)

        self._transition(record, RunPhase.ACTING, trace)
        self.budget_manager.consume_round(record)
        self.budget_manager.consume_model_call(record)

        revised_text, revisions = self._revise_claims(paper_text, evidence_map, request.dry_run)
        revised_path = run_dir / "paper-revised.md"
        if not request.dry_run and not request.review_only:
            revised_path.write_text(revised_text, encoding="utf-8")

        self._transition(record, RunPhase.EVALUATING, trace)
        evaluation = self._run_checks(paper_text, revised_text, evidence_map)

        round_record = RoundRecord(
            round_id=1,
            state_before=RunPhase.ACTING.value,
            decision=evaluation.verdict,
            reason_code="claim_evidence",
            finished_at=rfc3339(),
            evaluation_id=evaluation.evaluation_id,
        )
        rounds.append(round_record)

        record.outcome, record.terminal_reason = self._resolve_outcome(
            evaluation, revised_text, evidence_map
        )

        evidence_artifact = self._save_json(run_dir, "evidence-map.json", evidence_map, "claim_evidence_checker")
        artifacts.append(evidence_artifact)

        manifest_rel = f"paper/{record.run_id}/artifact-manifest.json"
        report_body = {
            "claims_found": str(len(claims)),
            "revisions": "; ".join(revisions) or "none",
            "source_required": "yes" if "SOURCE REQUIRED" in revised_text else "no",
        }
        report_path = run_dir / "paper-development-report.md"
        self.renderer.write_report(
            report_path, "paper/paper-development-report.md", record, report_body, manifest_rel
        )
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-paper-report",
                kind="report",
                path=str(report_path),
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
                rationale=record.terminal_reason or "Review claim-evidence mapping before publishing.",
                checklist=[
                    "Confirm SOURCE REQUIRED markers are acceptable",
                    "Add missing citations or experiments",
                    "Reject unsupported claims if no evidence exists",
                ],
            )
        )
        research_tasks = [
            "Collect benchmark numbers supporting performance claims",
            "Add citations for unsupported statements",
        ]
        if record.outcome == RunOutcome.PARTIAL:
            artifacts.append(write_next_research_tasks(run_dir, record, research_tasks))
        artifacts.append(
            write_next_actions(
                run_dir,
                record,
                research_tasks if record.outcome == RunOutcome.PARTIAL else ["Review revised draft"],
            )
        )

        return self._finalize(record, trace, run_dir, artifacts, rounds)

    def _extract_claims(self, paper_text: str) -> list[dict[str, str]]:
        claims: list[dict[str, str]] = []
        for idx, line in enumerate(paper_text.splitlines(), start=1):
            for marker in self.UNSUPPORTED_MARKERS:
                if marker.lower() in line.lower():
                    claims.append({"claim_id": f"claim-{idx}", "text": line.strip(), "line": str(idx)})
        if not claims and "outperforms" in paper_text.lower():
            claims.append({"claim_id": "claim-1", "text": "Unsupported performance claim", "line": "1"})
        return claims

    def _map_evidence(
        self, claims: list[dict[str, str]], citations: str, adapter: Any
    ) -> list[dict[str, object]]:
        adapter.execute({"role": "research"})
        mapped: list[dict[str, object]] = []
        entries = parse_bibtex(citations)
        for claim in claims:
            supporting_keys: list[str] = []
            support = "unsupported"
            for key, entry in entries.items():
                assessed = assess_citation_support(claim["text"], entry)
                if assessed in {"supported", "partial"}:
                    supporting_keys.append(key)
                    support = assessed
                    break
            mapped.append(
                {
                    "claim_id": claim["claim_id"],
                    "text": claim["text"],
                    "evidence_ids": supporting_keys,
                    "support_status": support,
                }
            )
        return mapped

    def _revise_claims(
        self, paper_text: str, evidence_map: list[dict[str, object]], dry_run: bool
    ) -> tuple[str, list[str]]:
        revisions: list[str] = []
        text = paper_text
        for item in evidence_map:
            if item.get("support_status") == "unsupported":
                original = str(item["text"])
                replacement = "This claim requires additional evidence before inclusion. [SOURCE REQUIRED]"
                if original in text:
                    text = text.replace(original, replacement)
                    revisions.append(f"Marked SOURCE REQUIRED: {item['claim_id']}")
            elif item.get("support_status") == "partial":
                original = str(item["text"])
                evidence_ids = item.get("evidence_ids") or []
                citation = str(evidence_ids[0]) if evidence_ids else "SOURCE REQUIRED"
                qualified = original.replace(
                    "significantly outperforms all baselines",
                    f"shows competitive results on selected benchmarks ({citation})",
                )
                if qualified != original:
                    text = text.replace(original, qualified)
                    revisions.append(f"Qualified claim: {item['claim_id']}")
        if dry_run:
            revisions.append("Dry-run: revision simulated")
        return text, revisions

    def _run_checks(
        self, original: str, revised: str, evidence_map: list[dict[str, object]]
    ) -> EvaluationResult:
        checks = [
            {"check_id": "structure", "status": "pass", "message": "Document structure valid", "evidence": []},
            {
                "check_id": "claim_evidence",
                "status": "pass",
                "message": "Claims mapped to evidence",
                "evidence": [],
            },
            {
                "check_id": "consistency",
                "status": "pass" if "fake" not in revised.lower() else "fail",
                "message": "No fabricated citations",
                "evidence": [],
            },
        ]
        unsupported = [e for e in evidence_map if e.get("support_status") == "unsupported"]
        has_source_required = "SOURCE REQUIRED" in revised

        if "fake" in revised.lower():
            verdict = EvaluationVerdict.FATAL.value
            checks[2]["status"] = "fail"
        elif unsupported and not has_source_required:
            verdict = EvaluationVerdict.FATAL.value
            checks[1]["status"] = "fail"
            checks[1]["message"] = "Missing citation, experiment, or source"
        elif has_source_required:
            verdict = EvaluationVerdict.NEEDS_HUMAN.value
            checks[1]["status"] = "warn"
            checks[1]["message"] = "Some claims marked SOURCE REQUIRED"
        else:
            verdict = EvaluationVerdict.PASS.value

        return EvaluationResult(
            evaluation_id="paper-eval-01",
            verdict=verdict,
            checks=checks,
            blocking_findings=[{"claim_id": e["claim_id"]} for e in unsupported] if unsupported else [],
        )

    def _resolve_outcome(
        self,
        evaluation: EvaluationResult,
        revised_text: str,
        evidence_map: list[dict[str, object]],
    ) -> tuple[RunOutcome, str]:
        has_source_required = "SOURCE REQUIRED" in revised_text
        if "fake" in revised_text.lower():
            return RunOutcome.FAILED, "Fabricated or inconsistent content detected"
        if evaluation.verdict == EvaluationVerdict.FATAL.value:
            unsupported = [e for e in evidence_map if e.get("support_status") == "unsupported"]
            if unsupported and not has_source_required:
                return RunOutcome.BLOCKED, "Missing citation, experiment, or source evidence"
            return RunOutcome.FAILED, "Claim-evidence evaluation failed"
        if has_source_required:
            return RunOutcome.PARTIAL, "Claim requires additional source"
        if evaluation.verdict == EvaluationVerdict.PASS.value:
            return RunOutcome.SUCCEEDED, "Claims supported by fixture evidence"
        return RunOutcome.PARTIAL, "Claim evidence incomplete"

    def _save_json(self, run_dir: Path, name: str, data: object, created_by: str) -> ArtifactReference:
        path = run_dir / name
        content = json.dumps(data, indent=2)
        path.write_text(content, encoding="utf-8")
        return ArtifactReference(
            artifact_id=f"{run_dir.name}-{name}",
            kind="evaluation",
            path=str(path),
            media_type="application/json",
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
        trace.append({"event": "state_transition", "phase": phase.value})
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
        for phase in (RunPhase.FINALIZING, RunPhase.PERSISTING, RunPhase.REPORTING):
            self._transition(record, phase, trace)
        record.phase = RunPhase.TERMINATED
        record.finished_at = rfc3339()
        record.report_status = "generated"

        manifest = ArtifactManifest(
            run_id=record.run_id,
            artifacts=artifacts,
            terminal_outcome=record.outcome.value if record.outcome else None,
        )
        (run_dir / "artifact-manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        return record, manifest, rounds
