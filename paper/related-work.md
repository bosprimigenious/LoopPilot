# Related Work

LoopPilot sits at the intersection of agent orchestration, completion admission, agent safety, enterprise governance, and personal automation. We position LoopPilot through **completion admission control** and **terminal lies**—not as another orchestration framework.

---

## Agent orchestration and multi-agent runtimes

LangGraph, CrewAI, AutoGen, and similar systems optimize the **Task Loop**: planning, tool nodes, and conversation handoffs. They typically expose hooks for human approval but rarely define evidence-carrying runs, checksum-sealed manifests, or durable review queues as mandatory outcomes.

**Differentiation:** Orchestration is **necessary but insufficient**. LangGraph interrupt/resume resembles `WAITING_APPROVAL`, but LoopPilot elevates admission to a first-class concern with sealed evidence bundles and summary truthfulness. A LangGraph graph may run inside LoopPilot's Task Loop; LoopPilot governs the full Three-Loop lifecycle.

See also: `related-work/agent-runtimes.md`.

---

## Verify-gated completion

Recent agent-runtime research treats task completion as admission control: a run claims "done" only after executable verification passes.

**Differentiation:** Verify-gated completion focuses on **verifier admission** at the step level. LoopPilot focuses on **lifecycle honesty across days**—review state, sealed artifacts, summaries, and recovery. A patch may pass local tests yet remain `needs_review` until human approve; conversely, governance oracles must catch false terminal claims even when tests pass. The two approaches are complementary.

---

## SafeAgent and agent safety benchmarks

SafeAgent-style systems and benchmarks (e.g., SafeAgentBench) protect **actions** from unsafe inputs—blocking harmful tool use, malicious requests, or unsafe embodied plans.

**Differentiation:** LoopPilot protects **terminal claims** from false trusted state. A run may execute only safe actions yet still commit a terminal lie if the runtime marks it completed while `gate_result.json` reads `needs_review`. Action safety and admission honesty address orthogonal failure classes.

---

## Governance by Construction

Enterprise frameworks (Governance by Construction, SARC, five-plane runtime governance) embed policy checkpoints—intent guards, tool approvals, human-in-the-loop gates, output formatters—into compound workflows with ops teams and compliance auditors.

**Differentiation:** LoopPilot targets **single-user daily automation consistency** without an ops layer: defer persistence, manifest sealing, summary truthfulness, and recovery scans for personal habit formation. Enterprise governance by construction assumes platform teams; personal automation must be self-governing at the runtime.

---

## Software-engineering and coding agents

SWE-agent, Devin-style copilots, and SWE-bench optimize patch correctness and repository navigation.

**Differentiation:** High pass@k does not prevent terminal lies if weekly summaries falsely mark unapproved patches complete. LoopPilot's failure taxonomy is orthogonal to patch quality.

See also: `related-work/software-engineering-agents.md`.

---

## Human-in-the-loop and gated autonomy

Enterprise RBAC and approval chains differ from personal setups requiring fail-closed defaults without ops teams.

**Differentiation:** LoopPilot instantiates gated autonomy as **runtime admission states**, not UI affordances alone. Deferred review persists in SQLite with `deferred_until`, not a session flag.

See also: `related-work/human-gated-autonomy.md`.

---

## Personal automation

Cron jobs and RSS rules automate triggers without agentic replanning or sealed terminal bundles.

**Differentiation:** LoopPilot is a daily task runtime with evidence-carrying runs and cross-day audit, not a note-taking plugin.

---

## Provenance and observability

MLflow and OpenTelemetry emphasize reproducible metrics and spans at fleet scale.

**Differentiation:** LoopPilot trades cluster telemetry for **personal recoverability**: one run directory, one manifest writer, honest traces serving admission control.

---

## Summary table (for paper §Related Work)

| Category | Representative systems | LoopPilot difference |
|----------|------------------------|----------------------|
| Orchestration | LangGraph, CrewAI, AutoGen | Three-Loop model; CAC; evidence-carrying runs |
| Verify-gated completion | Verifier admission runtimes | Lifecycle honesty across days |
| Action safety | SafeAgentBench, SafeArena | Terminal claim honesty vs action safety |
| Enterprise governance | Governance by Construction, SARC | Single-user daily consistency without ops |
| SE agents | SWE-agent, coding copilots | Terminal lies orthogonal to pass@k |
| HITL autonomy | Approval UIs, RBAC | Admission as state machine |
| Personal automation | Cron, RSS rules | Agent loops + sealed bundles |
| Provenance | MLflow, OTel | Personal terminal bundle + checksum seal |
