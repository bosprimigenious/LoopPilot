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

## Verification status

**Last run:** 2026-06-21 — see stabilization branch CI / `verify_0_4c_acceptance.py` (patch review gate behavior checks included).

### Review gate semantics (Codex PR #8 + P2)

| Run state | Before approve | After approve (`patch.diff`) |
|-----------|----------------|------------------------------|
| phase | `WAITING_APPROVAL` (not `TERMINATED`) | `TERMINATED` |
| outcome | `PARTIAL` | `SUCCEEDED` |
| gate | `needs_review` | `pass` |
| manifest | includes `review_suggestion.json` with matching sha256 | refreshed on disk **and** in SQLite `artifact_manifests` (`schema_version: 1`) |
| loop_trace | `waiting_review` / `partial` / `needs_review` — no `terminated/succeeded` | updated on approve |
| resume | blocked — use approve/reject/cancel | **blocked** — already finalized |

**Artifact write order (P2-2):** `write_review_suggestion()` → `finalize_terminal_artifacts()` — suggestion must exist on disk before manifest scan.

### Deferred sync invariant (P2)

When `ReviewService.sync_from_runs()` re-enqueues runs that still need review:

- Items with `status=deferred` and `deferred_until` in the future stay `deferred` (only `artifact_path` may update).
- Items with `status` in `approved`, `rejected`, `cancelled` are never touched.
- Expired deferred items (`deferred_until <= today`) may return to `pending`.

## Acceptance checklist

| # | Item | Pass criteria | Verified |
|---|------|---------------|----------|
| 1 | `review list` | Shows WAITING_APPROVAL / pending review runs with artifact paths | PASS |
| 2 | `review_required.md` | Present and listed in manifest for each listed run | PASS |
| 3 | `gate_result.json` | Present with valid `gate` for each listed run | PASS |
| 4 | `approve` | Direct-finalize patch runs (`TERMINATED`/`SUCCEEDED`/`pass`); no `resume_requested` | PASS |
| 5 | `reject --reason` | Requires reason; terminal BLOCKED semantics | PASS |
| 6 | `defer` | Sets `deferred_until`; hidden from default `today`; **sync must not revert to pending before due date** | PASS |
| 7 | `cancel` | Releases lock; auditable | PASS |
| 8 | `resume` | Blocked after approve/reject/cancel; safe checkpoint only | PASS |
| 9 | 0.4-b regression | inbox/queue/today still green | PASS |
| 10 | Manifest | No self-entry; `human_readable` flags correct | PASS |

## Executable acceptance flow

Prerequisites (from repo root):

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python scripts/verify_0_3_acceptance.py
```

Use sqlite acceptance config (`tests/fixtures/acceptance_0_4a/config`) or equivalent `loop-pilot.yaml`:

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

### Step 0 — Readiness gate

```bash
python scripts/verify_0_4c_acceptance.py
```

Must report **READY** before Steps 1–4.

### Step 1 — Generate review run

```bash
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config \
  run intern --workspace examples/intern_demo --dry-run
```

Assert artifacts under `var/artifacts/intern/<run-id>/`:

- `artifact-manifest.json`
- `run_meta.json`
- `report.md`
- `gate_result.json`
- `review_required.md`

### Step 2 — Review CLI

```bash
loop-pilot review list
loop-pilot review show <run-id>
loop-pilot approve <run-id> --note "checked locally"
# new run → reject
loop-pilot reject <run-id> --reason "patch is too risky"
loop-pilot reject <run-id>                    # MUST fail (no --reason)
loop-pilot defer <run-id> --until 2026-06-25
loop-pilot cancel <run-id> --reason "not needed anymore"
loop-pilot recovery-scan                      # after cancel — not stale
loop-pilot resume <run-id>                    # safe vs unsafe; ACTING must block
loop-pilot report <run-id>
```

### Step 3 — SQLite audit

```sql
SELECT id, run_id, status, decision, reason, decided_at FROM review_items;
SELECT entity_type, entity_id, event_type, created_at
  FROM task_events ORDER BY created_at DESC LIMIT 20;
```

### Step 4 — Integration tests

```bash
pytest tests/integration/test_review_cli.py -q
pytest tests/integration/test_review_decisions.py -q
pytest tests/integration/test_resume_policy.py -q
pytest tests/integration/test_review_events.py -q
pytest tests/integration/test_review_artifacts.py -q
pytest -q
python scripts/verify_0_4c_acceptance.py
```

### Pass criteria (all must hold)

- Run enters review queue after completion
- `review list` / `review show` work
- `approve` / `reject` / `defer` / `cancel` persist to SQLite + emit events
- `reject` without `--reason` fails
- `resume` policy blocks ACTING state
- `report <run-id>` works
- Every listed run has `review_required.md` + `gate_result.json`
- **No auto-approve**
- 0.1 / 0.2 / 0.3 / 0.4-b regression intact

## Related

- [46-review-layer-design.md](46-review-layer-design.md)
- [23-human-review-protocol.md](23-human-review-protocol.md)
