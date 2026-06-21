"""DailyNewsLoop Mini — offline snapshot days with dedup and star delta."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from loop_pilot.adapters.blocked_trace import append_adapter_blocked_event, adapter_trace_artifact_ref
from loop_pilot.adapters.errors import AdapterBlockedError
from loop_pilot.adapters.factory import create_adapter
from loop_pilot.domain.models import (
    ArtifactManifest,
    ArtifactReference,
    RoundRecord,
    RunRecord,
    RunRequest,
    content_hash,
    rfc3339,
)
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.loops.fixture_validation import validate_daily_news_fixture
from loop_pilot.models.router import ModelRouter
from loop_pilot.reporting.human_review import write_next_actions, write_review_required
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.runtime.budgets import BudgetManager, BudgetPolicy
from loop_pilot.runtime.state_machine import StateMachine
from loop_pilot.runtime.trace import TraceWriter
from loop_pilot.tools.broker import ToolBroker


class DailyNewsLoop:
    FIXTURE_ROOT = Path("tests/fixtures/daily_news")

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
        self.budget_manager = budget_manager or BudgetManager(BudgetPolicy(max_model_calls=6))
        self.router = router or ModelRouter({"roles": {}, "adapters": {"mock": {"kind": "mock"}}})
        self.tool_broker = tool_broker or ToolBroker()
        self.state_machine = StateMachine()

    def run(
        self,
        request: RunRequest,
        record: RunRecord,
        snapshot_day: str = "day2",
        *,
        phase_hook: Callable[[RunRecord], None] | None = None,
        resume_from: dict[str, Any] | None = None,
        source_profile: dict[str, Any] | None = None,
        adapter_override: str | None = None,
    ) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        self._phase_hook = phase_hook
        _ = resume_from
        if request.source_profile and source_profile is not None:
            return self._run_source_profile(
                request,
                record,
                source_profile,
                phase_hook=phase_hook,
                adapter_override=adapter_override or request.adapter_override,
            )
        fixture_name = request.fixture or "github_star_snapshots"
        fixture_dir = self.FIXTURE_ROOT / fixture_name
        run_dir = self.artifact_dir / "daily-news" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")
        adapter_trace = TraceWriter(run_dir / "adapter-call-trace.jsonl")
        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []
        try:
            adapter = create_adapter(
                self.router,
                "analysis_medium",
                fixture_dir=fixture_dir,
                artifact_dir=self.artifact_dir,
                adapter_override=adapter_override or request.adapter_override,
            )
        except AdapterBlockedError as exc:
            append_adapter_blocked_event(
                adapter_trace,
                blocked_reason=exc.reason,
                dry_run=request.dry_run,
                allow_real_adapters=self.router.allow_real_adapters,
                adapter_id=adapter_override or request.adapter_override,
            )
            artifacts.append(adapter_trace_artifact_ref(run_dir, record.run_id))
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = exc.message
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        validation = validate_daily_news_fixture(fixture_dir)
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
            RunPhase.ACTING,
            RunPhase.EVALUATING,
        ):
            self._transition(record, phase, trace)

        self.budget_manager.consume_round(record)
        adapter.execute({"role": "screening"})

        config = self._load_fixture_config(fixture_dir)
        max_items = config.get("categories", {}).get("github", {}).get("max_items", 3)
        min_confidence = config.get("minimum_confidence", "medium")

        raw_items = self._load_snapshots(fixture_dir, snapshot_day)
        normalized = self._normalize_items(raw_items)
        deduped = self._deduplicate(normalized)
        filtered = self._filter_low_confidence(deduped, min_confidence)
        ranked_github = self._rank_github(filtered, fixture_dir, snapshot_day)
        github_items = [i for i in ranked_github if i.get("category", "github") in self.INTERN_CATEGORIES][:max_items]
        paper_items = [
            i
            for i in filtered
            if i.get("category", "") in self.PAPER_CATEGORIES and i.get("confidence") == "high"
        ]
        seen_urls = {i.get("canonical_url") for i in github_items}
        ranked = github_items + [i for i in paper_items if i.get("canonical_url") not in seen_urls]

        high_confidence = [item for item in ranked if item.get("confidence") == "high"]
        intern_candidates, paper_candidates, candidate_actions = self._route_candidates(high_confidence)
        record.outcome = RunOutcome.SUCCEEDED
        record.terminal_reason = f"Processed {len(ranked)} items from {snapshot_day}"

        items_artifact = self._save_json(run_dir, "processed-items.json", ranked, "normalizer")
        artifacts.append(items_artifact)

        manifest_rel = f"daily-news/{record.run_id}/artifact-manifest.json"
        report_body = {
            "snapshot_day": snapshot_day,
            "item_count": str(len(ranked)),
            "inbox_candidates": str(len(high_confidence)),
            "intern_candidates": str(len(intern_candidates)),
            "paper_candidates": str(len(paper_candidates)),
            "star_delta_computed": "yes" if snapshot_day == "day2" else "no",
        }
        report_path = run_dir / "daily-news-report.md"
        self.renderer.write_report(
            report_path, "daily_news/daily-news-report.md", record, report_body, manifest_rel
        )
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-daily-news-report",
                kind="report",
                path=str(report_path),
                media_type="text/markdown",
                sha256=content_hash({"path": str(report_path)}),
                size_bytes=report_path.stat().st_size if report_path.exists() else 0,
                created_by="reporting",
            )
        )

        intern_path = run_dir / "intern-candidates.md"
        intern_content = self._render_candidate_list("Intern", intern_candidates)
        intern_path.write_text(intern_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-intern-candidates",
                kind="draft",
                path=str(intern_path),
                media_type="text/markdown",
                sha256=content_hash({"content": intern_content}),
                size_bytes=len(intern_content.encode()),
                created_by="router",
            )
        )

        paper_path = run_dir / "paper-candidates.md"
        paper_content = self._render_candidate_list("Paper", paper_candidates)
        paper_path.write_text(paper_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-paper-candidates",
                kind="draft",
                path=str(paper_path),
                media_type="text/markdown",
                sha256=content_hash({"content": paper_content}),
                size_bytes=len(paper_content.encode()),
                created_by="router",
            )
        )

        actions_path = run_dir / "candidate-actions.json"
        actions_content = json.dumps({"candidates": candidate_actions}, indent=2)
        actions_path.write_text(actions_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-candidate-actions",
                kind="source",
                path=str(actions_path),
                media_type="application/json",
                sha256=content_hash({"content": actions_content}),
                size_bytes=len(actions_content.encode()),
                created_by="router",
            )
        )

        artifacts.extend(self._write_human_review(run_dir, record, intern_candidates, paper_candidates))
        artifacts.append(
            self._save_json(
                run_dir,
                "tool-results.json",
                {"dry_run": request.dry_run, "audit": self.tool_broker.audit_records()},
                "tool_broker",
            )
        )

        rounds.append(
            RoundRecord(
                round_id=1,
                state_before=RunPhase.ACTING.value,
                decision="pass",
                reason_code="daily_news_complete",
                finished_at=rfc3339(),
            )
        )

        return self._finalize(record, trace, run_dir, artifacts, rounds)

    def _run_source_profile(
        self,
        request: RunRequest,
        record: RunRecord,
        profile_cfg: dict[str, Any],
        *,
        phase_hook: Callable[[RunRecord], None] | None = None,
        adapter_override: str | None = None,
    ) -> tuple[RunRecord, ArtifactManifest, list[RoundRecord]]:
        self._phase_hook = phase_hook
        record.fixture = request.source_profile
        run_dir = self.artifact_dir / "daily-news" / record.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl")
        adapter_trace = TraceWriter(run_dir / "adapter-call-trace.jsonl")
        rounds: list[RoundRecord] = []
        artifacts: list[ArtifactReference] = []

        demo_fixture = Path("examples/daily_news_demo")
        try:
            adapter = create_adapter(
                self.router,
                "analysis_medium",
                fixture_dir=demo_fixture if demo_fixture.exists() else None,
                artifact_dir=self.artifact_dir,
                adapter_override=adapter_override or request.adapter_override,
            )
        except AdapterBlockedError as exc:
            append_adapter_blocked_event(
                adapter_trace,
                blocked_reason=exc.reason,
                dry_run=request.dry_run,
                allow_real_adapters=self.router.allow_real_adapters,
                adapter_id=adapter_override or request.adapter_override,
            )
            artifacts.append(adapter_trace_artifact_ref(run_dir, record.run_id))
            self._enter_observing(record, trace)
            record.outcome = RunOutcome.BLOCKED
            record.terminal_reason = exc.message
            return self._finalize(record, trace, run_dir, artifacts, rounds)

        self._enter_observing(record, trace)
        for phase in (
            RunPhase.SELECTING,
            RunPhase.PLANNING,
            RunPhase.POLICY_CHECK,
            RunPhase.ACTING,
            RunPhase.EVALUATING,
        ):
            self._transition(record, phase, trace)

        self.budget_manager.consume_round(record)
        adapter.execute({"role": "screening"})

        min_confidence = str(profile_cfg.get("minimum_confidence", "medium"))
        raw_items: list[dict] = []
        for source_cfg in profile_cfg.get("sources", []):
            if not source_cfg.get("enabled", True):
                continue
            try:
                raw_items.extend(self.tool_broker.fetch_source(source_cfg))
            except (FileNotFoundError, ValueError):
                continue

        normalized = self._normalize_items(raw_items)
        deduped = self._deduplicate(normalized)
        filtered = self._filter_low_confidence(deduped, min_confidence)
        for item in filtered:
            item.setdefault("rank_label", "demo_local_source")
            item["star_delta_24h"] = None

        high_confidence = [item for item in filtered if item.get("confidence") == "high"]
        intern_candidates, paper_candidates, candidate_actions = self._route_candidates(high_confidence)
        record.outcome = RunOutcome.SUCCEEDED
        record.terminal_reason = f"Processed {len(filtered)} items from profile {request.source_profile}"

        artifacts.append(self._save_json(run_dir, "processed-items.json", filtered, "normalizer"))
        manifest_rel = f"daily-news/{record.run_id}/artifact-manifest.json"
        report_body = {
            "snapshot_day": request.source_profile or "demo",
            "item_count": str(len(filtered)),
            "inbox_candidates": str(len(high_confidence)),
            "intern_candidates": str(len(intern_candidates)),
            "paper_candidates": str(len(paper_candidates)),
            "star_delta_computed": "no",
        }
        report_path = run_dir / "daily-news-report.md"
        self.renderer.write_report(
            report_path, "daily_news/daily-news-report.md", record, report_body, manifest_rel
        )
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-daily-news-report",
                kind="report",
                path=str(report_path),
                media_type="text/markdown",
                sha256=content_hash({"path": str(report_path)}),
                size_bytes=report_path.stat().st_size if report_path.exists() else 0,
                created_by="reporting",
            )
        )

        intern_path = run_dir / "intern-candidates.md"
        intern_content = self._render_candidate_list("Intern", intern_candidates)
        intern_path.write_text(intern_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-intern-candidates",
                kind="draft",
                path=str(intern_path),
                media_type="text/markdown",
                sha256=content_hash({"content": intern_content}),
                size_bytes=len(intern_content.encode()),
                created_by="router",
            )
        )

        paper_path = run_dir / "paper-candidates.md"
        paper_content = self._render_candidate_list("Paper", paper_candidates)
        paper_path.write_text(paper_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-paper-candidates",
                kind="draft",
                path=str(paper_path),
                media_type="text/markdown",
                sha256=content_hash({"content": paper_content}),
                size_bytes=len(paper_content.encode()),
                created_by="router",
            )
        )

        actions_path = run_dir / "candidate-actions.json"
        actions_content = json.dumps({"candidates": candidate_actions}, indent=2)
        actions_path.write_text(actions_content, encoding="utf-8")
        artifacts.append(
            ArtifactReference(
                artifact_id=f"{record.run_id}-candidate-actions",
                kind="source",
                path=str(actions_path),
                media_type="application/json",
                sha256=content_hash({"content": actions_content}),
                size_bytes=len(actions_content.encode()),
                created_by="router",
            )
        )
        artifacts.extend(self._write_human_review(run_dir, record, intern_candidates, paper_candidates))
        artifacts.append(
            self._save_json(
                run_dir,
                "tool-results.json",
                {"dry_run": request.dry_run, "audit": self.tool_broker.audit_records()},
                "tool_broker",
            )
        )

        rounds.append(
            RoundRecord(
                round_id=1,
                state_before=RunPhase.ACTING.value,
                decision="pass",
                reason_code="daily_news_complete",
                finished_at=rfc3339(),
            )
        )
        return self._finalize(record, trace, run_dir, artifacts, rounds)

    def _write_human_review(
        self,
        run_dir: Path,
        record: RunRecord,
        intern_candidates: list[dict],
        paper_candidates: list[dict],
    ) -> list[ArtifactReference]:
        return [
            write_review_required(
                run_dir,
                record,
                recommended="continue",
                rationale="Review routed candidates before spawning intern or paper runs.",
                checklist=[
                    "Accept intern candidates worth investigating",
                    "Accept paper candidates needing evidence review",
                    "Reject low-value noise items",
                ],
            ),
            write_next_actions(
                run_dir,
                record,
                [
                    f"Review {len(intern_candidates)} intern candidate(s)",
                    f"Review {len(paper_candidates)} paper candidate(s)",
                    "Use candidate-actions.json for routing decisions",
                ],
            ),
        ]

    def _load_fixture_config(self, fixture_dir: Path) -> dict:
        path = fixture_dir / "config" / "daily_news.yaml"
        if not path.exists():
            return {"categories": {"github": {"max_items": 3}}, "minimum_confidence": "medium"}
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _load_snapshots(self, fixture_dir: Path, day: str) -> list[dict]:
        snap_dir = fixture_dir / "input" / "snapshots"
        items: list[dict] = []
        for path in sorted(snap_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_snapshot_file"] = path.name
            if day == "day1" and "day1" in path.name:
                items.extend(data.get("repositories", []))
            elif day == "day2" and "day2" in path.name:
                items.extend(data.get("repositories", []))
            elif day not in ("day1", "day2"):
                items.extend(data.get("repositories", []))
        if not items:
            for path in sorted(snap_dir.glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                items.extend(data.get("repositories", []))
        dup_path = fixture_dir / "input" / "duplicate_event.json"
        if dup_path.exists():
            items.extend(json.loads(dup_path.read_text(encoding="utf-8")).get("items", []))
        low_path = fixture_dir / "input" / "low_confidence.json"
        if low_path.exists():
            items.extend(json.loads(low_path.read_text(encoding="utf-8")).get("items", []))
        paper_path = fixture_dir / "input" / "paper_signal.json"
        if paper_path.exists():
            items.extend(json.loads(paper_path.read_text(encoding="utf-8")).get("items", []))
        return items

    def _normalize_items(self, raw: list[dict]) -> list[dict]:
        normalized: list[dict] = []
        for item in raw:
            normalized.append(
                {
                    "source_item_id": item.get("repo_id") or item.get("source_item_id", "unknown"),
                    "canonical_url": item.get("url", ""),
                    "source_id": item.get("source_id", "github"),
                    "source_tier": item.get("tier", "B"),
                    "title": item.get("name", item.get("title", "")),
                    "published_at": item.get("published_at"),
                    "event_at": item.get("event_at"),
                    "stars": item.get("stars"),
                    "confidence": item.get("confidence", "medium"),
                    "category": item.get("category", "github"),
                    "content_hash": content_hash(item),
                }
            )
        return normalized

    def _deduplicate(self, items: list[dict]) -> list[dict]:
        seen: set[str] = set()
        result: list[dict] = []
        for item in items:
            key = item.get("canonical_url") or item.get("title")
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    def _filter_low_confidence(self, items: list[dict], min_confidence: str) -> list[dict]:
        order = {"low": 0, "medium": 1, "high": 2}
        threshold = order.get(min_confidence, 1)
        return [i for i in items if order.get(i.get("confidence", "medium"), 1) >= threshold]

    def _rank_github(self, items: list[dict], fixture_dir: Path, day: str) -> list[dict]:
        if day == "day1":
            for item in items:
                item["rank_label"] = "candidate_hot_repo"
                item["star_delta_24h"] = None
            return sorted(items, key=lambda x: x.get("stars") or 0, reverse=True)

        day1_path = fixture_dir / "input" / "snapshots" / "github_day1.json"
        prev: dict[str, int] = {}
        if day1_path.exists():
            for repo in json.loads(day1_path.read_text(encoding="utf-8")).get("repositories", []):
                prev[repo["repo_id"]] = repo.get("stars", 0)

        ranked: list[dict] = []
        for item in items:
            repo_id = item.get("source_item_id")
            current = item.get("stars")
            if current is None:
                item["star_delta_24h"] = None
            elif repo_id in prev:
                item["star_delta_24h"] = current - prev[repo_id]
            else:
                item["star_delta_24h"] = None
            item["rank_label"] = "star_delta_ranked" if item.get("star_delta_24h") is not None else "candidate_hot_repo"
            ranked.append(item)

        return sorted(
            ranked,
            key=lambda x: (x.get("star_delta_24h") is not None, x.get("star_delta_24h") or 0),
            reverse=True,
        )

    def load_local_source_set(self, source_set: Path, min_confidence: str = "medium") -> list[dict]:
        """Load offline/local DailyNews items and apply confidence filtering."""
        items_path = source_set / "items.json"
        if not items_path.exists():
            raise FileNotFoundError(f"Local source set missing items.json: {source_set}")
        raw_items = json.loads(items_path.read_text(encoding="utf-8")).get("items", [])
        normalized = self._normalize_items(raw_items)
        return self._filter_low_confidence(normalized, min_confidence)

    INTERN_CATEGORIES = frozenset({"github", "engineering", "dependency", "tooling", "security"})
    PAPER_CATEGORIES = frozenset({"paper", "benchmark", "dataset", "research", "controversy"})

    def _route_candidates(
        self, items: list[dict]
    ) -> tuple[list[dict], list[dict], list[dict[str, str]]]:
        intern_candidates: list[dict] = []
        paper_candidates: list[dict] = []
        actions: list[dict[str, str]] = []

        for item in items:
            category = str(item.get("category", "github")).lower()
            target_loop = self._target_loop_for_category(category)
            candidate = dict(item)
            candidate["target_loop"] = target_loop
            if target_loop == "paper":
                paper_candidates.append(candidate)
                recommended_action = "review_claim_evidence"
            else:
                intern_candidates.append(candidate)
                recommended_action = "evaluate_for_intern_task"

            actions.append(
                {
                    "target_loop": target_loop,
                    "priority": "high" if item.get("confidence") == "high" else "normal",
                    "source_item_id": str(item.get("source_item_id", "unknown")),
                    "reason": f"{category} signal routed to {target_loop}",
                    "recommended_action": recommended_action,
                }
            )
        return intern_candidates, paper_candidates, actions

    def _target_loop_for_category(self, category: str) -> str:
        if category in self.PAPER_CATEGORIES:
            return "paper"
        if category in self.INTERN_CATEGORIES:
            return "intern"
        return "intern"

    def _render_candidate_list(self, loop_name: str, candidates: list[dict]) -> str:
        lines = [f"# {loop_name} Inbox Candidates", ""]
        for item in candidates:
            lines.append(
                f"- [{item.get('confidence', 'medium')}] {item.get('title')} -> {item.get('canonical_url')}"
            )
        if len(lines) == 2:
            lines.append("- No high-confidence candidates")
        return "\n".join(lines)

    def route_inbox(self, items: list[dict]) -> str:
        """Render high-confidence candidates for Intern/Paper inbox routing."""
        intern_candidates, paper_candidates, _ = self._route_candidates(
            [item for item in items if item.get("confidence") == "high"]
        )
        sections = [
            self._render_candidate_list("Intern", intern_candidates),
            "",
            self._render_candidate_list("Paper", paper_candidates),
        ]
        return "\n".join(sections)

    def _render_inbox(self, candidates: list[dict]) -> str:
        return self._render_candidate_list("Intern", candidates)

    def _save_json(self, run_dir: Path, name: str, data: object, created_by: str) -> ArtifactReference:
        path = run_dir / name
        content = json.dumps(data, indent=2)
        path.write_text(content, encoding="utf-8")
        return ArtifactReference(
            artifact_id=f"{run_dir.name}-{name}",
            kind="source",
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
