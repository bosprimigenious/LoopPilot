# Personal Daily Loop 0.4-c Acceptance Checklist

Version: **0.4.0c** (branch `personal-daily-loop-0.4-c`)

> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.3 (0.4-c — personal review)  
> **Prerequisite:** [44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md) — inbox/queue/today green  
> **Output interface (mandatory):** [47-output-interface-spec.md](47-output-interface-spec.md)  
> **Chinese guide:** [../zh/12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md)

## Scope

### In scope (0.4-c)

| Area | Deliverable |
|------|-------------|
| Review CLI | `review list`, `approve`, `reject`, `defer`, `cancel`, `resume`, `report` |
| SQLite | `reviews` table writes on each decision |
| Human artifacts | `review_required.md` for every review-queue run |
| Machine artifacts | `gate_result.json` for every review-queue run |
| Optional | `review_suggestion.json` when gate is `needs_review` or `blocked` |
| Tests | integration tests for review flow + artifact presence |

### Out of scope

| Excluded | Belongs to |
|----------|------------|
| `summary today/week`, `schedule` | **0.4-d** |
| Team / cloud | **1.3 preview** |

## Output interface requirements (0.4-c)

Per [47-output-interface-spec.md](47-output-interface-spec.md):

| Artifact | Requirement |
|----------|-------------|
| `review_required.md` | **Mandatory** for every run returned by `review list` |
| `gate_result.json` | **Mandatory** for every run returned by `review list` |
| `artifact-manifest.json` | Must list both with correct `human_readable` flags |
| `review_suggestion.json` | Required when `gate_result.json.gate` is `needs_review` or `blocked` |

Acceptance scripts MUST assert JSON structure and manifest membership; MUST NOT diff Markdown prose.

## Acceptance checklist

| # | Item | Pass criteria |
|---|------|---------------|
| 1 | `review list` | Shows WAITING_APPROVAL / pending review runs with artifact paths |
| 2 | `review_required.md` | Present and listed in manifest for each listed run |
| 3 | `gate_result.json` | Present with valid `gate` for each listed run |
| 4 | `approve` | Writes review row; updates run review_status |
| 5 | `reject --reason` | Requires reason; terminal BLOCKED semantics |
| 6 | `defer` | Sets deferred_until; hidden from default `today` |
| 7 | `cancel` | Releases lock; auditable |
| 8 | `resume` | Only from legal checkpoint (0.4-a dependency) |
| 9 | 0.4-b regression | inbox/queue/today still green |
| 10 | Manifest | `human_readable: true` on MD, `false` on JSON gate/trace |

## Related

- [46-review-layer-design.md](46-review-layer-design.md)
- [23-human-review-protocol.md](23-human-review-protocol.md)
