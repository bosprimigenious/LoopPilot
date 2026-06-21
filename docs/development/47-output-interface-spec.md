# 47 Output Interface Specification — Human MD vs Machine JSON

> **Authority:** Canonical per-run artifact layout and dual-layer output model for LoopPilot runs.  
> **Related:** [17-data-contracts.md](17-data-contracts.md) (object contracts), [07-data-and-reports.md](07-data-and-reports.md) (storage and report policy), [23-human-review-protocol.md](23-human-review-protocol.md) (review decisions).  
> **Chinese guide:** [../zh/13-输出接口-人看MD机器看JSON.md](../zh/13-输出接口-人看MD机器看JSON.md)

---

## 1. Core principle

```text
Human-facing: Markdown (.md)
Machine-facing: JSON / JSONL
```

- **Humans** read Markdown reports, review pages, and daily summaries.
- **Machines** (CI, acceptance scripts, external evaluators such as [agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner)) judge runs via structured JSON/JSONL.
- Markdown must not be parsed as the source of truth for run outcome, gate verdict, or review state.
- JSON artifacts must not replace human-readable narrative; every completed run still produces `report.md`.

---

## 2. Two-layer output model

| Layer | Format | Audience | Examples |
|-------|--------|----------|----------|
| **Human** | Markdown (YAML front matter per [17-data-contracts.md §12](17-data-contracts.md)) | Owner, collaborators | `report.md`, `review_required.md`, `next_actions.md`, `daily-summary.md` |
| **Machine** | JSON / JSONL | Runtime, SQLite sync, CI, evaluators | `artifact-manifest.json`, `run_meta.json`, `gate_result.json`, `tool-results.json`, `loop_trace.jsonl` |

Cross-link rule: `artifact-manifest.json` lists every file with `human_readable: true|false`. Human pages reference machine evidence by path; machine records reference human pages in `artifact_refs` where applicable.

---

## 3. Canonical per-run directory layout

```text
var/artifacts/<loop>/<run-id>/
├── artifact-manifest.json      # index of all artifacts (machine)
├── run_meta.json               # run identity, config snapshot, terminal outcome (machine)
├── loop_trace.jsonl            # append-only phase/round events (machine)
├── tool-results.json           # ToolBroker audit (machine, when tools run)
├── adapter-call-trace.jsonl    # Adapter calls / blocked (machine, when adapter used)
├── gate_result.json            # evaluator gate verdict (machine, review / eval runs)
├── report.md                   # primary human summary
├── review_required.md          # human review entry point
├── next_actions.md             # human follow-up list
└── review_suggestion.json      # machine review hint (when run enters review)
```

**Daily aggregate (0.4-d, not per-run):**

```text
var/artifacts/daily/<YYYY-MM-DD>/daily-summary.md
```

`<loop>` is one of `intern`, `paper`, `daily-news`. `<run-id>` matches `RunRecord.run_id`.

**Legacy aliases (pre-0.4-c writers):** `trace.jsonl` → `loop_trace.jsonl`; `review-required.md` → `review_required.md`; `next-actions.md` → `next_actions.md`. New writers MUST use canonical names; readers SHOULD accept both until migration completes.

**Note on date grouping:** [07-data-and-reports.md §7](07-data-and-reports.md) describes an optional `YYYY-MM-DD/` prefix for retention browsing. The canonical path above is authoritative for artifact contracts; date prefixes are organizational only and must not change manifest-relative paths inside a run directory.

---

## 4. Per-file purpose

| File | Layer | Purpose |
|------|-------|---------|
| `artifact-manifest.json` | Machine | Single index of all artifacts; terminal outcome; retention hints; `human_readable` per entry |
| `run_meta.json` | Machine | Stable run header: `run_id`, `loop_type`, `attempt_id`, timestamps, `config_snapshot_hash`, terminal `outcome`, `phase` |
| `loop_trace.jsonl` | Machine | Append-only audit: state transitions, rounds, interrupts, termination |
| `tool-results.json` | Machine | ToolBroker events, policy decisions, durations (required when any tool runs) |
| `adapter-call-trace.jsonl` | Machine | Adapter request/response metadata, blocked reasons (required when adapter path executes) |
| `gate_result.json` | Machine | External or internal evaluator gate: `pass` \| `needs_review` \| `blocked` |
| `report.md` | Human | Loop-specific summary with fixed section headings; links to evidence paths |
| `review_required.md` | Human | Review entry: recommended action, rationale, checklist (mandatory for 0.4-c review queue) |
| `next_actions.md` | Human | Actionable follow-ups for owner or inbox routing |
| `review_suggestion.json` | Machine | Structured mirror of review recommendation for CLI/automation |
| `daily-summary.md` | Human | Cross-loop day rollup (0.4-d); lives under `daily/<date>/`, not inside a single run |

Loop-specific extras (e.g. `patch.diff`, `proposed-revision.md`, `candidate-actions.json`) MUST be listed in `artifact-manifest.json` but are defined in loop sub-specs ([03-intern-loop.md](03-intern-loop.md), [04-paper-loop.md](04-paper-loop.md), [05-daily-news-loop.md](05-daily-news-loop.md)).

---

## 5. `gate_result.json` schema (example)

Minimal contract for evaluator integration (full schema: [schemas/gate_result.schema.json](../../schemas/gate_result.schema.json)):

```json
{
  "schema_version": "1.0",
  "run_id": "2026-06-21T120000+0800-intern-001",
  "gate": "needs_review",
  "evaluator": "agentic-rubric-runner",
  "evaluator_version": "0.1.0",
  "profile": "looppilot-intern",
  "evaluated_at": "2026-06-21T12:30:00+08:00",
  "checks": [
    {
      "check_id": "required_tests",
      "status": "pass",
      "message": "Directed pytest suite passed"
    },
    {
      "check_id": "patch_scope",
      "status": "fail",
      "message": "Patch touches files outside allowed_paths"
    }
  ],
  "blocking_findings": [
    {
      "finding_id": "scope-001",
      "severity": "blocking",
      "message": "Modified config/ outside task scope"
    }
  ],
  "non_blocking_findings": [],
  "recommended_review_action": "reject",
  "artifact_refs": {
    "report": "report.md",
    "review_required": "review_required.md",
    "tool_results": "tool-results.json"
  }
}
```

**Gate values:**

| `gate` | Meaning |
|--------|---------|
| `pass` | Automated checks satisfied; human review optional per policy |
| `needs_review` | Run stopped for human decision; `review_required.md` required |
| `blocked` | Hard failure; no auto-continue; reason in `blocking_findings` |

When [agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner) is used, its output is normalized into `gate_result.json`. Optional companion: `review_suggestion.json` (see §8).

---

## 6. `artifact-manifest.json` and `human_readable`

Each manifest entry extends [17-data-contracts.md §8](17-data-contracts.md) `ArtifactReference` with:

```json
{
  "artifact_id": "2026-06-21T120000+0800-intern-001-report",
  "kind": "report",
  "path": "report.md",
  "media_type": "text/markdown",
  "sha256": "...",
  "size_bytes": 4096,
  "created_by": "intern_loop",
  "human_readable": true,
  "contains_sensitive_data": false
}
```

| `human_readable` | Typical kinds |
|------------------|---------------|
| `true` | `report`, `review`, `draft` (Markdown summaries) |
| `false` | `log`, `evaluation`, `checkpoint`, `trace`, JSON indexes |

Manifest is the directory truth source: filenames alone do not define artifact type. See [schemas/artifact-manifest.json](../../schemas/artifact-manifest.json).

---

## 7. `loop_trace.jsonl` event types

One JSON object per line. Common `event` values:

| Event | When emitted |
|-------|----------------|
| `run_started` | Run accepted; `run_id`, `loop_type`, `config_snapshot_hash` |
| `state_transition` | `RunPhase` change; `phase`, `run_id` |
| `phase_entered` | Sub-step within phase (plan, act, check) |
| `round_complete` | Round finished; embeds `RoundRecord` summary |
| `tool_invoked` | ToolBroker call (optional duplicate of `tool-results.json`) |
| `adapter_call` | Adapter request metadata (optional duplicate of adapter trace) |
| `evaluation_complete` | Internal evaluator finished; may reference `gate_result.json` |
| `interrupted` | Error or external interrupt; `error`, `round` |
| `review_required` | Run entered `WAITING_APPROVAL`; links human + machine review artifacts |
| `terminated` | Final `outcome`, `terminal_reason` |

Consumers MUST tolerate unknown `event` values (forward-compatible).

---

## 8. `review_suggestion.json` (review runs only)

Emitted when a run requires human review (outcome `PARTIAL`, `BLOCKED`, `EXHAUSTED`, or gate `needs_review`):

```json
{
  "schema_version": "1.0",
  "run_id": "2026-06-21T120000+0800-intern-001",
  "recommended": "reject",
  "rationale": "Patch scope exceeds allowed_paths",
  "checklist": [
    "Confirm only src/loop_pilot/ was intended",
    "Re-run with narrowed objective"
  ],
  "gate": "needs_review",
  "human_artifact": "review_required.md"
}
```

`review list` and acceptance scripts SHOULD prefer this file; humans open `review_required.md`.

---

## 9. 0.4-b vs 0.4-c output distinction

| Aspect | **0.4-b** (task entry) | **0.4-c** (personal review) |
|--------|------------------------|-----------------------------|
| Focus | Inbox, queue, today CLI | `review list`, approve/reject/defer/cancel/resume |
| Human review artifact | Optional (`review_required.md` on non-success outcomes) | **Mandatory** for queue-visible review runs |
| `gate_result.json` | Not required (internal eval only) | **Mandatory** when run enters review queue |
| `review_suggestion.json` | Optional | Required when `gate` is `needs_review` or `blocked` |
| SQLite | `inbox_items`, `queue_items`, task events | `reviews` table populated by approve/reject/defer |
| Daily rollup | Not in scope | Feeds 0.4-d `daily-summary.md` review section |

0.4-b may still write `candidate-actions.json` and dual-write inbox rows ([44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md)). 0.4-c acceptance MUST verify `review_required.md` + `gate_result.json` exist for every run listed by `review list`.

---

## 10. Required files matrix

Legend: **R** = required, **C** = conditional, **—** = not required

| File | Every run | Review queue (0.4-c) | Tools used | Adapter used | Daily rollup (0.4-d) |
|------|-----------|----------------------|------------|--------------|----------------------|
| `artifact-manifest.json` | R | R | R | R | — (per-run only) |
| `run_meta.json` | R | R | R | R | — |
| `loop_trace.jsonl` | R | R | R | R | — |
| `report.md` | R | R | R | R | — |
| `review_required.md` | C | R | C | C | — |
| `next_actions.md` | C | C | — | — | — |
| `gate_result.json` | — | R | C | C | — |
| `review_suggestion.json` | — | C | — | — | — |
| `tool-results.json` | C | C | R | C | — |
| `adapter-call-trace.jsonl` | C | C | — | R | — |
| `daily-summary.md` | — | — | — | — | R (under `daily/<date>/`) |

**Conditions:**

- **Review queue:** run appears in `loop-pilot review list` or has `review_status` pending in SQLite.
- **Tools used:** any ToolBroker invocation during the run.
- **Adapter used:** any adapter call attempt (including blocked).

---

## 11. Acceptance and CI

- Automated acceptance MUST assert JSON fields and manifest membership, not Markdown prose equality.
- Human spot-check uses `report.md` and `review_required.md` only.
- External evaluator profile MUST write or update `gate_result.json` in the run directory without modifying human Markdown except via documented templates.

Decision log: [logs/2026-06-21-output-interface-md-json.md](logs/2026-06-21-output-interface-md-json.md).
