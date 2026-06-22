# Personal Daily Loop 0.4 Full Acceptance Checklist

Version: **0.4.0** (full chain a → b → c → d)

> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)  
> **Sub-checklists:** [43](43-personal-daily-loop-0.4a-acceptance.md) · [44](44-personal-daily-loop-0.4b-acceptance.md) · [45](45-personal-daily-loop-0.4c-acceptance.md) · [48](48-personal-daily-loop-0.4d-acceptance.md)  
> **Latest run:** [logs/2026-06-21-0.4-full-acceptance-run.md](logs/2026-06-21-0.4-full-acceptance-run.md)

## One-line definition

Verify complete **personal daily loop OS manual closure**:

```text
SQLite reliable → Inbox → Queue → Today → Run → Review → Summary → Schedule preview
```

## Prerequisites

```bash
cd LoopPolit
python -m pip install -e ".[dev]"
```

SQLite config (acceptance fixture or `config.local`):

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

Use: `loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config …`

## Out of scope

- Unattended mode
- `schedule install --yes` (real OS registration)
- Real API / live adapters
- Auto approve / auto commit

---

## Layer 0 — Quality + 0.3 regression

| # | Check | Command |
|---|-------|---------|
| 0.1 | Lint | `ruff check .` |
| 0.2 | Tests | `pytest -q` |
| 0.3 | 0.3 acceptance | `python scripts/verify_0_3_acceptance.py` |

---

## Layer 1 — 0.4-a (SQLite / recovery)

| # | Check | Command |
|---|-------|---------|
| 1.1 | Doctor | `loop-pilot doctor` |
| 1.2 | DB status | `loop-pilot db status` |
| 1.3 | Migrate dry-run | `loop-pilot db migrate --dry-run` |
| 1.4 | Migrate | `loop-pilot db migrate` |
| 1.5 | Verify | `loop-pilot db verify` |
| 1.6 | Backup dry-run | `loop-pilot db backup --dry-run` |
| 1.7 | Recovery scan | `loop-pilot recovery-scan` |

Script (if present): `python scripts/verify_0_4a_acceptance.py`

---

## Layer 2 — 0.4-b (Inbox / Queue / Today)

| # | Check | Command |
|---|-------|---------|
| 2.1 | Inbox add | `inbox add "fix login test" --source manual --loop intern --priority 2` |
| 2.2 | Inbox list | `inbox list` |
| 2.3 | Queue promote | `queue promote <inbox-id> --loop intern --priority 2` |
| 2.4 | Queue list | `queue list` |
| 2.5 | Today schedule | `today add-queue <queue-id>` |
| 2.6 | Today view | `today` |
| 2.7 | DailyNews run | `run daily-news --source-profile demo --dry-run` |
| 2.8 | Import dry-run | `inbox import-daily-news --from <candidate-actions.json> --dry-run` |
| 2.9 | Import | `inbox import-daily-news --from <path>` |
| 2.10 | Dedup | repeat import → skipped duplicates |

Script: `python scripts/verify_0_4b_acceptance.py`

If inbox/queue/today CLI missing → **FAIL layer 2, note blocked**.

---

## Layer 3 — 0.4-c (Review — CRITICAL)

| # | Check | Command |
|---|-------|---------|
| 3.1 | Intern run | `run intern --workspace examples/intern_demo --dry-run [--json]` |
| 3.2 | Review list | `review list` |
| 3.3 | Review show | `review show <run-id>` |
| 3.4 | Approve | `review approve <run-id> --note "checked locally"` (alias: `loop-pilot approve`) |
| 3.5 | Reject (with reason) | `review reject <run-id> --reason "needs more tests"` (alias: `loop-pilot reject`) |
| 3.6 | Reject (no reason) | must **FAIL** |
| 3.7 | Defer | `review defer <run-id> --until 2026-06-25` (alias: `loop-pilot defer`) |
| 3.8 | Cancel | `review cancel <run-id> --reason "not needed"` (alias: `loop-pilot cancel`) |
| 3.9 | Recovery after cancel | `recovery-scan` |
| 3.10 | Report | `report <run-id>` |

**Artifacts:** `gate_result.json`, `review_required.md`, `report.md`  
**SQLite:** `review_items`, `task_events` audit rows

Script: `python scripts/verify_0_4c_acceptance.py`

If 0.4-c NOT implemented → document **"0.4 full acceptance blocked by incomplete 0.4-c"**.

---

## Layer 4 — 0.4-d (Summary / Schedule)

| # | Check | Command |
|---|-------|---------|
| 4.1 | Daily summary | `summary today` |
| 4.2 | Weekly summary | `summary week` |
| 4.3 | Schedule print | `schedule print` |
| 4.4 | Cron preview | `schedule print --target cron` |
| 4.5 | Systemd preview | `schedule print --target systemd` |
| 4.6 | Windows preview | `schedule print --target windows-task-scheduler` |
| 4.7 | Install dry-run | `schedule install --dry-run` |
| 4.8 | Daily orchestration | `run daily --dry-run` |

**Artifacts:** `daily-summary.md` (7 sections), `week-summary.md`, `schedule-preview.md`

Script: `python scripts/verify_0_4d_acceptance.py`

---

## Layer 5 — Negative tests

| # | Check | Expected |
|---|-------|----------|
| 5.1 | `schedule install --yes` | fail / block (0.5 message) |
| 5.2 | `run daily --unattended --safe` | fail / block |
| 5.3 | `run intern … --adapter cursor_cli --dry-run` | blocked outcome |

---

## Layer 6 — SQLite audit

```sql
.tables
SELECT COUNT(*) FROM inbox_items, queue_items, review_items;
SELECT event_type, COUNT(*) FROM task_events GROUP BY event_type;
```

---

## Pass criteria

**Full PASS** requires:

- Layers 0–6 all PASS
- `verify_0_4b` and `verify_0_4d` green
- `verify_0_4c` green (not readiness gate FAIL)
- Review CLI exercisable end-to-end

**Tag `v0.4.0`** only when full PASS + user criteria met.

---

## Current status (2026-06-21)

| Layer | Status |
|-------|--------|
| 0 | PASS |
| 1 | PASS |
| 2 | PASS |
| 3 | **FAIL — blocked** |
| 4 | PASS |
| 5 | PASS |
| 6 | PASS* |

**Verdict:** BLOCKED by 0.4-c.
