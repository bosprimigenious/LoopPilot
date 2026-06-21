# Personal Daily Loop 0.4-d Acceptance Checklist

Version: **0.4.0d** (branch `personal-daily-loop-0.4-d`)

> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.4 (0.4-d — daily summary and schedule preview)  
> **Prerequisite:** [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) — review layer green (or readiness gate documented)  
> **Output interface (mandatory):** [47-output-interface-spec.md](47-output-interface-spec.md) — `daily-summary.md` location and human/machine split  
> **Architecture:** [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md)  
> **Chinese guide:** [../zh/14-0.4d-日汇总与调度预览.md](../zh/14-0.4d-日汇总与调度预览.md)

## One-line definition

**0.4-d** validates whether LoopPilot is a **usable daily dashboard** — not a feature demo, but whether you can rely on it for everyday task review, schedule preview, and safe dry-run orchestration.

Core: **Summary + Schedule Preview + Safe Daily Dry-Run + data aggregation consistency** from real SQLite / events / artifacts.

---

## Scope

### In scope (0.4-d)

| Layer | Area | Deliverable |
|-------|------|-------------|
| **1 — Summary** | CLI | `loop-pilot summary today`, `loop-pilot summary week` |
| **1 — Summary** | Artifacts | `var/artifacts/daily/<YYYY-MM-DD>/daily-summary.md`; `var/artifacts/weekly/<week>/week-summary.md` |
| **2 — Data integration** | SQL aggregator | Reads `inbox_items`, `queue_items`, `today_items`, `runs`, `events`, `review_items`, artifact paths |
| **2 — Data integration** | SQLite | `summaries` table metadata on each generation |
| **3 — Schedule preview** | CLI | `loop-pilot schedule print`; `loop-pilot schedule install --dry-run` |
| **3 — Schedule preview** | Safety | No cron/systemd/Task Scheduler/registry writes |
| **4 — Daily run dry-run** | CLI | `loop-pilot run daily --dry-run` — verify + recovery-scan + today preview + summary refresh |
| **4 — Daily run dry-run** | Safety | No real Loop execution; no adapter/API calls |

### Out of scope

| Excluded | Belongs to |
|----------|------------|
| `schedule install --yes` (real OS registration) | **0.5+** |
| Real API / agent execution in `run daily` | **0.5+** unattended levels |
| Auto approve / auto commit / auto push | **Never** |
| Unattended Level 0–4 automation | **0.5+** |
| Team / cloud / Dashboard | **1.3 preview** |

---

## Four acceptance layers

### Layer 1 — Summary (human dashboard)

- `summary today` generates or refreshes `daily-summary.md` with seven sections (see below).
- `summary week` generates `week-summary.md` rollup for the configured timezone week.
- Output paths match [47-output-interface-spec.md §3](47-output-interface-spec.md).

**daily-summary.md seven sections** (aligned with [40-personal-daily-loop-0.4-spec.md §3.4](40-personal-daily-loop-0.4-spec.md)):

1. 今日最重要结论 (highlights, ≤3 bullets)
2. Today (scheduled queue/today items)
3. Runs (today's runs with outcome, gate, report path)
4. Needs Review (pending review runs + suggested CLI)
5. Inbox Updates (new items, DailyNews candidates)
6. Blocked (blocked runs + recovery scan notes)
7. Tomorrow (queue/inbox priorities)

### Layer 2 — Data integration (SQLite + artifacts)

- Aggregator MUST query live SQLite tables; MUST NOT use hard-coded mock counts in production path.
- Section counts MUST be reconcilable with SQL (see verification queries below).
- Each run row in summary MUST include `run_id` and resolvable artifact path (`report.md` or loop-specific report).
- Review rows MUST reference `gate_result.json` when present.
- Inbox/queue/today rows MUST map to `inbox_items.id`, `queue_items.id`, or `today_items.id`.

### Layer 3 — Schedule preview (safe only)

- `schedule print` emits platform-appropriate config text (cron / systemd / windows-task-scheduler).
- `schedule install --dry-run` writes preview artifact only (e.g. `var/artifacts/schedule/schedule-preview.md`).
- Neither command creates OS scheduler entries, registry keys, or crontab lines.
- `schedule install --yes` MUST refuse or defer with explicit 0.5 message.

### Layer 4 — Daily run dry-run (orchestration preview)

- `run daily --dry-run` executes, in order: `db verify` (or equivalent), `recovery-scan`, today preview, summary generation.
- Does NOT invoke `run intern|paper|daily-news` without `--dry-run`.
- Does NOT call adapters or external APIs.
- Acquires and releases daily lock; logs steps to stdout.

---

## Section IV — Full acceptance checklist

| # | Item | Layer | Pass criteria |
|---|------|-------|---------------|
| 1 | `summary today` | 1 | Exit 0; writes `var/artifacts/daily/<date>/daily-summary.md`; echoes path |
| 2 | Seven-section structure | 1 | All seven headings present; empty sections show explicit "none" placeholder |
| 3 | `summary week` | 1 | Exit 0; writes `var/artifacts/weekly/<week>/week-summary.md` |
| 4 | SQLite `summaries` row | 2 | Row upserted with `summary_type`, `summary_date`, `path`, counts |
| 5 | Run count consistency | 2 | Summary run table count matches SQL for target date |
| 6 | Review count consistency | 2 | Needs Review section count matches pending review query |
| 7 | Inbox count consistency | 2 | Inbox Updates count matches new inbox rows for date |
| 8 | Traceability — runs | 2 | Each run row includes `run_id`; report path exists or marked missing |
| 9 | Traceability — tasks | 2 | Today/queue rows reference inbox/queue ids |
| 10 | Traceability — events | 2 | Review decisions reflected from `task_events` / `review_items` |
| 11 | Artifact paths | 2 | Paths under `var/artifacts/<loop>/<run-id>/` resolve on disk when run exists |
| 12 | `schedule print` | 3 | Exit 0; prints scheduler snippet; no system mutation |
| 13 | `schedule install --dry-run` | 3 | Exit 0; preview file written; stdout confirms no install |
| 14 | `schedule install --yes` guard | 3 | Refuses real install (exit non-zero or explicit defer message) |
| 15 | `run daily --dry-run` | 4 | Exit 0; verify + recovery + today + summary steps logged |
| 16 | No real loop in daily dry-run | 4 | No new run directories created under intern/paper/daily-news |
| 17 | Pipeline closure | all | Inbox → Queue → Today → Run → Review → Summary chain reflected in summary |
| 18 | sqlite-only guard | all | Commands require `state_backend=sqlite`; json backend clear error |
| 19 | Integration tests | all | `pytest tests/integration/test_daily_summary_cli.py -q` green |
| 20 | 0.4-a regression | all | `db verify`, `recovery-scan` still green |
| 21 | 0.4-b regression | all | inbox/queue/today CLI still green |
| 22 | 0.4-c regression | all | review CLI + artifacts still green when implemented |
| 23 | 0.1–0.3 regression | all | `pytest -q`; `verify_0_3_acceptance.py` green on json backend |

---

## Section V — Pass criteria (8 must-haves)

| # | Must-have | Verification |
|---|-----------|--------------|
| 1 | **Daily dashboard usable** | Maintainer can open `daily-summary.md` and understand today without opening SQLite |
| 2 | **Weekly rollup usable** | `week-summary.md` aggregates 7-day runs, reviews, blocked items |
| 3 | **Data from real stores** | Aggregator reads SQLite + artifact filesystem; no fixture-only counts in CLI path |
| 4 | **Traceability** | Every summary list item links to `run_id`, `event_id`, or `artifact` path verifiable on disk |
| 5 | **Schedule safety** | `schedule print` and `schedule install --dry-run` never write OS scheduler |
| 6 | **Daily dry-run safety** | `run daily --dry-run` never executes real loops or adapter calls |
| 7 | **Pipeline closure** | Summary sections reflect full chain: Inbox → Queue → Today → Run → Review → Summary |
| 8 | **Regression** | 0.1 / 0.2 / 0.3 / 0.4-a / 0.4-b / 0.4-c baselines remain green |

---

## Enable SQLite locally

Reuse the 0.4-a acceptance config:

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
  timezone: Asia/Shanghai
  artifact_dir: var/artifacts
```

```bash
export LP_CONFIG=tests/fixtures/acceptance_0_4a/config
# or: loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config ...
```

---

## Acceptance commands

Run from repo root with sqlite config:

```bash
# Prerequisites
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config db migrate
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config db verify

# Layer 1 — Summary
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config summary today
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config summary week

# Layer 3 — Schedule preview
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config schedule print
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config schedule print --target cron
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config schedule install --dry-run

# Layer 4 — Daily dry-run
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config run daily --dry-run

# Automated runner
python scripts/verify_0_4d_acceptance.py

# Tests and regression
pytest tests/integration/test_daily_summary_cli.py tests/unit/test_summary_collector.py -q
pytest -q
python scripts/verify_0_3_acceptance.py
python scripts/verify_0_4a_acceptance.py 2>/dev/null || true
python scripts/verify_0_4b_acceptance.py 2>/dev/null || true
python scripts/verify_0_4c_acceptance.py 2>/dev/null || true
ruff check .
```

### Expected outputs

| Command | Expected |
|---------|----------|
| `summary today` | `Daily summary: var/artifacts/daily/<YYYY-MM-DD>/daily-summary.md`; exit 0 |
| `summary week` | `Weekly summary: var/artifacts/weekly/<YYYY-Www>/week-summary.md`; exit 0 |
| `schedule print` | Platform scheduler snippet on stdout; exit 0 |
| `schedule install --dry-run` | Preview path echoed; message "No system scheduler entries were created."; exit 0 |
| `run daily --dry-run` | Lines include verify, recovery, today preview, summary path; exit 0 |
| `verify_0_4d_acceptance.py` | All steps PASS (or NOT READY with pending list pre-implementation) |

---

## SQLite verification queries

Run against `runtime.sqlite_path` after `summary today`:

```sql
-- Summary metadata persisted
SELECT summary_type, summary_date, path, run_count, review_count, inbox_count, status
FROM summaries
WHERE summary_type = 'daily'
ORDER BY generated_at DESC
LIMIT 1;

-- Runs on target date (adjust :date)
SELECT run_id, loop_type, outcome, phase, started_at, finished_at
FROM runs
WHERE substr(started_at, 1, 10) = :date OR substr(finished_at, 1, 10) = :date;

-- Pending review (0.4-c)
SELECT run_id, decision, created_at
FROM review_items
WHERE decision IS NULL OR decision = 'pending';

-- Today focus
SELECT t.id, q.id AS queue_id, q.title, q.status
FROM today_items t
JOIN queue_items q ON t.queue_id = q.id
WHERE t.date = :date;

-- New inbox on date
SELECT id, title, source, status, created_at
FROM inbox_items
WHERE substr(created_at, 1, 10) = :date;

-- Task events audit trail
SELECT event_type, entity_id, payload, created_at
FROM task_events
WHERE substr(created_at, 1, 10) = :date
ORDER BY created_at;
```

**Consistency rules:**

- `summaries.run_count` SHOULD equal count of runs query for that date (± runs without timestamps).
- Needs Review section count SHOULD match pending review query (± runs in WAITING_APPROVAL without review row).
- Inbox Updates count SHOULD match new inbox query for date.

---

## Traceability requirements

Every human-facing summary list item MUST be traceable:

| Summary section | Required link |
|-----------------|---------------|
| Runs | `run_id` → `var/artifacts/<loop>/<run-id>/report.md` |
| Needs Review | `run_id` → `review_required.md`, `gate_result.json` |
| Today / Tomorrow | `queue_id` or `inbox_id` → SQLite row |
| Inbox Updates | `inbox_id` → `inbox_items.id`; DailyNews → source artifact path |
| Blocked | `run_id` → terminal outcome BLOCKED + optional recovery event |
| Metadata footer | `run_ids[]`, generation timestamp, config timezone |

Acceptance scripts SHOULD assert JSON/SQL fields and path existence; MUST NOT diff Markdown prose.

---

## Pipeline closure

End-to-end personal daily loop:

```text
Inbox → Queue → Today → Run → Review → Summary
  │       │       │      │       │         │
  │       │       │      │       │         └── daily-summary.md (Layer 1)
  │       │       │      │       └── review list / approve / reject (0.4-c)
  │       │       │      └── run intern|paper|daily-news (dry-run or live)
  │       │       └── today CLI / today_items
  │       └── queue promote
  └── inbox add / import-daily-news
```

**0.4-d closure test:** After seeding inbox → promote → today, running a dry-run loop, and leaving a review pending, `summary today` MUST show entries in Today, Runs (if run completed), and Needs Review sections respectively.

**Schedule + daily dry-run closure:** `run daily --dry-run` MUST produce an updated `daily-summary.md` without executing new loops.

---

## Output paths (47 cross-reference)

Per [47-output-interface-spec.md §3](47-output-interface-spec.md):

| Artifact | Path |
|----------|------|
| Daily summary | `var/artifacts/daily/<YYYY-MM-DD>/daily-summary.md` |
| Weekly summary | `var/artifacts/weekly/<YYYY-Www>/week-summary.md` |
| Schedule preview | `var/artifacts/schedule/schedule-preview.md` |

Per-run artifacts remain under `var/artifacts/<loop>/<run-id>/`; daily summary references them by path only.

---

## Regression matrix

| Baseline | Command | Must remain green |
|----------|---------|-------------------|
| 0.1 Mini | `loop-pilot run all --fixture-set mini --dry-run` | exit 0 on json backend |
| 0.2 Practical | `pytest tests/ -k practical -q` (if present) | no new failures |
| 0.3 Adapter | `python scripts/verify_0_3_acceptance.py` | all PASS |
| 0.4-a | `db verify`, `recovery-scan` | exit 0 on sqlite config |
| 0.4-b | inbox/queue/today CLI | exit 0 |
| 0.4-c | review CLI + artifacts | exit 0 when implemented |

Default `state_backend=json` MUST NOT register 0.4-d commands without clear sqlite-only message.

---

## CI note

- Default CI uses `state_backend: json`; 0.4-d integration tests use temp sqlite paths.
- Full CLI acceptance opt-in via `tests/fixtures/acceptance_0_4a/config` or `verify_0_4d_acceptance.py`.

---

## Related

- [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md) — engine architecture
- [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) — review prerequisite
- [44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md) — task entry prerequisite
- [47-output-interface-spec.md](47-output-interface-spec.md) — artifact layout
- [logs/2026-06-21-0.4d-spec-and-prompt.md](logs/2026-06-21-0.4d-spec-and-prompt.md) — decision log
