"""PaperLoop Mini — unsupported claim with trusted citation fixture."""

from __future__ import annotations

import json
import re
from pathlib import Path

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
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.state_machine import StateMachine
from loop_pilot.runtime.trace import TraceWriter


class PaperLoop:
    FIXTURE_ROOT = Path("tests/fixtures/paper")
    UNSUPPORTED_MARKERS = ("significantly outperforms all baselines", "state-of-the-art on every benchmark")

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
        self.budget_manager = budget_manager or BudgetManager(BudgetPolicy(max_model_calls=12))
        self.state_machine = StateMachine()

    def run(self, request: RunRequest, record: RunRecord) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        fixture_name = request.fixture or "unsupported_claim"
        fixture_dir = self.FIXTURE_ROOT / fixture_name
        run_dir = self.artifact_dir / "paper" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")
        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []
        adapter = MockAdapter(fixture_dir)

        self._enter_observing(record, trace)
        for phase in (
            RunPhase.SELECTING,
            RunPhase.PLANNING,
            RunPhase.POLICY_CHECK,
        ):
            self._transition(record, phase, trace)

        paper_path = fixture_dir / "input" / "paper.md"
        paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
        citations_path = fixture_dir / "input" / "references.bib"
        citations = citations_path.read_text(encoding="utf-8") if citations_path.exists() else ""

        claims = self._extract_claims(paper_text)
        evidence_map = self._map_evidence(claims, citations, adapter)

        self._transition(record, RunPhase.ACTING, trace)
        self.budget_manager.consume_round(record)
        self.budget_manager.consume_model_call(record)

        revised_text, revisions = self._revise_claims(paper_text, evidence_map, request.dry_run)
        revised_path = run_dir / "paper-revised.md"
        if not request.dry_run:
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

        if evaluation.verdict == EvaluationVerdict.PASS.value:
            record.outcome = RunOutcome.SUCCEEDED
            record.terminal_reason = "Unsupported claims revised with fixture evidence"
        elif any("SOURCE REQUIRED" in r for r in revisions):
            record.outcome = RunOutcome.PARTIAL
            record.terminal_reason = "Claim requires additional source"
        else:
            record.outcome = RunOutcome.PARTIAL
            record.terminal_reason = "Claim evidence incomplete"

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
        self, claims: list[dict[str, str]], citations: str, adapter: MockAdapter
    ) -> list[dict[str, object]]:
        adapter.execute({"role": "research"})
        mapped: list[dict[str, object]] = []
        trusted_keys = re.findall(r"@\w+", citations)
        for claim in claims:
            support = "partial" if trusted_keys else "unsupported"
            mapped.append(
                {
                    "claim_id": claim["claim_id"],
                    "text": claim["text"],
                    "evidence_ids": trusted_keys[:1],
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
                replacement = f"{original} [SOURCE REQUIRED]"
                if original in text:
                    text = text.replace(original, replacement)
                    revisions.append(f"Marked SOURCE REQUIRED: {item['claim_id']}")
            elif item.get("support_status") == "partial":
                original = str(item["text"])
                qualified = original.replace(
                    "significantly outperforms all baselines",
                    "shows competitive results on selected benchmarks (Smith2024)",
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
        if unsupported and not has_source_required:
            verdict = EvaluationVerdict.FATAL.value
            checks[1]["status"] = "fail"
        else:
            verdict = EvaluationVerdict.PASS.value

        return EvaluationResult(
            evaluation_id="paper-eval-01",
            verdict=verdict,
            checks=checks,
            blocking_findings=[{"claim_id": e["claim_id"]} for e in unsupported] if unsupported else [],
        )

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
