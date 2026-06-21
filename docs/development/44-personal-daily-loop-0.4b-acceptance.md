# Personal Daily Loop 0.4-b Acceptance Checklist

Version: **0.4.0b** (branch `personal-daily-loop-0.4-b` or continuation of `0.4-a`)

> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.2 (0.4-b — personal task entry)  
> **Prerequisite:** [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) — db + recovery-scan green  
> **Chinese guide:** (pending) `docs/zh/12-0.4b-任务入口.md`

## Scope

### In scope (0.4-b)

| Area | Module | Deliverable |
|------|--------|-------------|
| Schema migration v2 | `src/loop_pilot/storage/migrations.py` | `inbox_items`, `queue_items`, `today_items` (or documented view-only today) |
| Task store | `src/loop_pilot/tasks/` (new) | Inbox/queue CRUD against SQLite |
| Inbox CLI | `src/loop_pilot/cli_tasks.py` or `cli.py` | `inbox add`, `inbox list`, optional `inbox archive` |
| Queue CLI | same | `queue list`, `queue promote`, optional `queue demote` |
| Today CLI | same | `today`, optional `today add` |
| DailyNews dual-write | `src/loop_pilot/loops/daily_news/` | `candidate-actions.json` also writes SQLite `inbox_items` |
| Tests | `tests/unit/test_inbox_queue.py` | add → promote → today traceable; DailyNews route |

### Out of scope

| Excluded | Belongs to |
|----------|------------|
| `review list`, `approve` / `reject` / `defer` / `cancel` / `resume` | **0.4-c** |
| `summary today/week`, `schedule print/install` | **0.4-d** |
| Team / cloud / Dashboard | **1.3 preview** |
| PyPI / public onboarding | **0.5 / 0.8** |

## Enable SQLite locally

Reuse the 0.4-a acceptance config (or copy to `var/acceptance-0.4b-config`):

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

Recommended config dir for acceptance runs:

```bash
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config inbox add "fix login test" --source manual
```

## Acceptance checklist

| # | Item | Pass criteria |
|---|------|---------------|
| 1 | Migration v2 | `db migrate` creates `inbox_items`, `queue_items` (and `today_items` if entity table) |
| 2 | `inbox add` | Writes row to SQLite; prints item id; exit 0 |
| 3 | `inbox list` | Default `--status open` shows added item; `--status all` includes archived |
| 4 | `queue promote <inbox-id>` | Inbox status updated; queue row created with priority |
| 5 | `queue list` | Shows promoted item; inbox no longer in open list |
| 6 | `today` | Renders queue head + active runs + pending review count (review count may be 0 pre-0.4-c) |
| 7 | DailyNews → inbox | After `run daily-news --fixture …`, SQLite has inbox rows from high-confidence candidates |
| 8 | Artifact dual-write | `candidate-actions.json` still written (0.3 compat) |
| 9 | Unit tests | `pytest tests/unit/test_inbox_queue.py -q` green |
| 10 | JSON regression | Default `config/loop-pilot.yaml` (`state_backend: json`) — inbox/queue/today **not registered** or clear "sqlite only" message |
| 11 | 0.4-a regression | `db verify`, `recovery-scan`, `doctor` still green on sqlite config |

## Acceptance commands

Run from repo root with sqlite config:

```bash
# Prerequisites (0.4-a)
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config db migrate
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config db verify

# 0.4-b task flow
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config inbox add "fix login test" --source manual
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config inbox list
# capture inbox id from list output:
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config queue promote <inbox-id>
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config queue list
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config today

# DailyNews dual-write (optional integration check)
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config run daily-news --fixture github_star_snapshots --dry-run
# then verify inbox_items rows with source daily-news

# Automated runner
python scripts/verify_0_4b_acceptance.py

# Tests and lint
pytest tests/unit/test_inbox_queue.py -q
ruff check .
loop-pilot doctor
```

### Expected outputs (fill after first green run)

| Command | Expected |
|---------|----------|
| `inbox add` | Prints id (e.g. `inbox-…`); exit 0 |
| `inbox list` | Table or lines with title, id, source, status=open |
| `queue promote` | Confirms promotion; inbox status no longer open |
| `queue list` | Shows queue id, inbox_id, priority, status |
| `today` | Sections: queue focus, active runs, pending reviews |
| `pytest test_inbox_queue.py` | All passed |
| `verify_0_4b_acceptance.py` | All steps PASS |

## Data semantics (from spec)

- **Inbox**: uncommitted inputs (manual, DailyNews route, Loop next-actions)
- **Queue**: committed, not yet assigned to a Run
- **Today**: daily focus subset of Queue (entity table or view — document choice in code)

## CI note

- Default CI uses `state_backend: json`; 0.4-b unit tests should use temp sqlite paths (like 0.4-a).
- Full CLI acceptance remains opt-in via sqlite config dir.

## Readiness gate (2026-06-21 verification)

| Expected | Status |
|----------|--------|
| `src/loop_pilot/tasks/` (store, inbox/queue/today services) | **WIP present** |
| `src/loop_pilot/cli_tasks.py` | **WIP present** |
| Migration v2 (`inbox_items`, `queue_items`, `task_events`) | **WIP present** (`CURRENT_SCHEMA_VERSION = 2`) |
| `loop-pilot inbox` / `queue` / `today` CLI | **Missing** — `cli_tasks` not wired in `cli.py` |
| `tests/unit/test_inbox_queue.py` | **Missing** |
| `test_db_ops.py` schema v2 alignment | **Failing** (tests still assert v1) |
| DailyNews → SQLite inbox dual-write in loop | **Missing** (artifact-only; use `inbox import-daily-news` CLI when wired) |

Run `python scripts/verify_0_4b_acceptance.py` to re-check before full acceptance.

## Related docs

- [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) — full 0.4 four sub-phases
- [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) — Phase 2 implementation order
- [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) — prerequisite
