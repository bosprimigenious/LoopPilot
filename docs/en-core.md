# LoopPilot — English Core Spec

Minimal interface-layer reference for AI agents, CI, and extension authors.  
For human-readable Chinese docs, see [docs/zh/README.md](zh/README.md).

## System Overview

LoopPilot is a **controlled local runtime** for three personal AI work loops:

- **InternLoop** — resolve one real dev problem with verification
- **PaperLoop** — advance one evidence-backed research/writing gap
- **DailyNewsLoop** — select high-value signals from offline snapshots into Inboxes

The runtime orchestrates state, budget, policy gates, adapters, and auditable artifacts. User-facing results are **Markdown**; machine state uses JSON/JSONL (0.1–0.3) or SQLite (0.4+).

**Canonical names:** product `LoopPilot`, CLI/PyPI `loop-pilot`, Python import `loop_pilot`.

## Adapter Concept

An **Adapter** is the boundary between LoopPilot and external model/CLI systems.

| Type | Examples | Default (0.3) |
|------|----------|---------------|
| Mock | `MockAdapter` | enabled |
| CLI | `cursor_cli` | blocked |
| API | `openai_compatible` | blocked |

**Protocol (`BaseAdapter`):**

- `capabilities()` → `AdapterCapabilities`
- `healthcheck()` → `HealthStatus` (no side effects)
- `execute(request, timeout, cancellation)` → `AdapterResult`
- `estimate_cost(request)` → `CostEstimate`
- `normalize_error(error)` → `LoopPilotError`

**Gating:** `runtime.allow_real_adapters` defaults `false`. Real adapters require config **and** CLI `--allow-real-adapters`. CI always uses Mock.

**Routing:** `ModelRouter` selects adapter by capability, data class, budget, and fallback policy. Agents cannot instantiate adapters directly.

Spec detail: [development/19-adapter-specifications.md](development/19-adapter-specifications.md), [development/37-adapter-safety-policy.md](development/37-adapter-safety-policy.md).

## Loop Definition

Each Loop is a **declarative pipeline** driven by Orchestrator:

```text
Observe → Select → Plan → Policy Check → Act → Evaluate → (Reflect → Replan) → Finalize → Report
```

| Loop | Input | Output | Budget |
|------|-------|--------|--------|
| InternLoop | workspace / fixture | dev report, diff artifacts | ~30 min, 3 rounds |
| PaperLoop | paper workspace / fixture | revision report, evidence | ~30 min, 3 rounds |
| DailyNewsLoop | source profile / fixture | daily brief, inbox candidates | ~30 min |

DailyNewsLoop **must not** directly modify code or papers; it writes to `intern-inbox.md` / `paper-inbox.md`.

Loop specs: [development/03-intern-loop.md](development/03-intern-loop.md), [development/04-paper-loop.md](development/04-paper-loop.md), [development/05-daily-news-loop.md](development/05-daily-news-loop.md).

## State Machine

**Phase** (`RunPhase`) and **outcome** (`RunOutcome`) are separate enums.

```text
CREATED → LOCKING → OBSERVING → SELECTING → PLANNING → POLICY_CHECK
  → ACTING → EVALUATING → FINALIZING → PERSISTING → REPORTING → TERMINATED

Branches:
  POLICY_CHECK → WAITING_APPROVAL | BLOCKED
  EVALUATING   → RETRYABLE (→ DIAGNOSING → REFLECTING → REPLANNING) | NEEDS_HUMAN | FATAL
  Budget/user  → EXHAUSTED | CANCELLED
```

Outcomes include: `SUCCEEDED`, `PARTIAL`, `BLOCKED`, `FAILED`, `NO_ACTION`, `DEFERRED`.

Full spec: [development/18-state-transition-spec.md](development/18-state-transition-spec.md).

## Safety Model

1. **Default deny for real adapters** — `allow_real_adapters: false`; blocked adapters raise `AdapterBlockedError`.
2. **Policy Gate** — mandatory before every write; returns `ALLOW | REQUIRE_APPROVAL | DENY`.
3. **ToolBroker (0.3)** — allowlisted file/git/command/http; audit trail; dry-run mode.
4. **Data classes** — `PUBLIC < PROJECT < SENSITIVE < SECRET`; SECRET never enters adapters.
5. **Path/command allowlists** — workspace boundaries, no auto push/deploy/commit.
6. **Secret redaction** — keys masked in trace/artifacts as `<redacted>`.
7. **Budget limits** — time, rounds, model calls; hard stop at deadline.

Mini/0.2: approval-required actions terminate as `BLOCKED` (no resume CLI).  
0.4+: persistent approval, `resume`, SQLite checkpoints.

Security detail: [development/08-security-and-recovery.md](development/08-security-and-recovery.md), [development/38-toolbroker-design.md](development/38-toolbroker-design.md).

## Version Status (this branch)

| Version | Tag / branch | Focus |
|---------|--------------|-------|
| 0.1 | done | MockAdapter, fixture dry-run |
| 0.2 | `v0.2.0a1` | controlled demo workspaces |
| 0.3 | `adapter-mvp-0.3` / `v0.3.0a1` | real adapters + ToolBroker (safety alpha; Full DoD pending MANUAL) |
| 0.4 | next | Personal Recovery & Daily Loop — see [40-personal-daily-loop-0.4-spec.md](development/40-personal-daily-loop-0.4-spec.md) |
| 1.x | planned | Personal Stable → Collaboration — see [42-1x-roadmap-personal-to-collaboration.md](development/42-1x-roadmap-personal-to-collaboration.md) |

Acceptance: [development/36-adapter-mvp-0.3-acceptance.md](development/36-adapter-mvp-0.3-acceptance.md). Chinese summary: [docs/zh/07-0.3-Adapter验收说明.md](zh/07-0.3-Adapter验收说明.md).

## Quick Commands

```bash
loop-pilot doctor
loop-pilot adapters list
loop-pilot adapters doctor
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run all --profile demo --dry-run
pytest -q
```
