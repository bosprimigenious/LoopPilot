# Personal Daily Loop 0.4-a Acceptance Checklist

Version: **0.4.0a1** (branch `personal-daily-loop-0.4-a`)

> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.1 (0.4-a — state reliability)  
> **Delivery log:** [logs/2026-06-21-0.4a-delivery.md](logs/2026-06-21-0.4a-delivery.md)  
> **Chinese guide:** [../zh/11-0.4a-SQLite与恢复扫描.md](../zh/11-0.4a-SQLite与恢复扫描.md)

## Scope

### In scope (0.4-a)

| Area | Module | Deliverable |
|------|--------|-------------|
| Schema migrations | `src/loop_pilot/storage/migrations.py` | Idempotent `schema_migrations`; v1 tables |
| DB operations | `src/loop_pilot/storage/db_ops.py` | `status`, `migrate`, `verify`, `backup` helpers |
| DB CLI | `src/loop_pilot/cli_db.py` | `loop-pilot db status/migrate/backup/verify` |
| Recovery scan | `src/loop_pilot/runtime/recovery_scan.py` | `loop-pilot recovery-scan` |
| Doctor (sqlite) | `src/loop_pilot/cli.py` | SQLite writable, `lock_dir`, recovery hints |
| Tests | `tests/unit/test_db_ops.py`, `tests/unit/test_recovery_scan.py` | Migration idempotency, ACTING → `manual_review_required` |

Schema v1 tables: `runs`, `checkpoints`, `reviews`, `artifact_manifests`, `events`, `run_locks`, `schema_migrations`.

### Out of scope

| Excluded | Belongs to |
|----------|------------|
| `inbox` / `queue` / `today` CLI | **0.4-b** |
| `review list`, `approve` / `reject` / `defer` / `cancel` | **0.4-c** |
| `summary today/week`, `schedule print/install` | **0.4-d** |
| Auto-resume on ACTING interrupt | Never in 0.4-a (scan only) |

## Enable SQLite locally

Default repo config stays **`state_backend: json`** (0.1 CI baseline).

**Committed acceptance fixture:**

```bash
--config-dir tests/fixtures/acceptance_0_4a/config
```

**Local override** (e.g. `config.local/`):

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

## Acceptance checklist

| # | Item | Pass criteria |
|---|------|---------------|
| 1 | `db status` | Reports `backend: sqlite`, schema version, run counts, lock dir |
| 2 | `db migrate --dry-run` | No error; pending list or "No pending migrations" |
| 3 | `db migrate` | Idempotent; second run reports up to date |
| 4 | `db verify` | `Verify: OK` on migrated DB |
| 5 | `db backup --dry-run` | Lists planned copy targets; no writes |
| 6 | `recovery-scan` | Exit 0; `OK (no issues)` or actionable findings |
| 7 | `doctor` | `Doctor: OK` with sqlite checks |
| 8 | Unit tests | `pytest tests/unit/test_db_ops.py tests/unit/test_recovery_scan.py -q` green |
| 9 | JSON regression | Default config `doctor` OK with sqlite hint warning |
| 10 | ACTING interrupt | `recovery-scan` → `manual_review_required`, not auto-resume |

## Acceptance commands

```bash
CFG=tests/fixtures/acceptance_0_4a/config

loop-pilot --config-dir $CFG db status
loop-pilot --config-dir $CFG db migrate --dry-run
loop-pilot --config-dir $CFG db migrate
loop-pilot --config-dir $CFG db verify
loop-pilot --config-dir $CFG db backup --dry-run
loop-pilot --config-dir $CFG recovery-scan
loop-pilot --config-dir $CFG doctor

# 0.1 regression (json default)
loop-pilot doctor
pytest tests/unit/test_db_ops.py tests/unit/test_recovery_scan.py -q
pytest -q
```

### Expected outputs (2026-06-21)

| Command | Expected |
|---------|----------|
| `db status` | `backend: sqlite`, `schema_version: 1`, `pending_migrations: none` |
| `db migrate --dry-run` | `No pending migrations` |
| `db migrate` | `Database schema up to date` |
| `db verify` | `Verify: OK` |
| `db backup --dry-run` | `Would back up:` lines for db, state dir, config |
| `recovery-scan` | `Recovery scan: OK (no issues)` |
| `doctor` (sqlite cfg) | `Doctor: OK` |
| `doctor` (json default) | `Doctor: OK` + Warning about sqlite |
| `pytest …` (0.4-a only) | `11 passed` |
| `pytest -q` (full) | `141 passed` |

## Key behavior: recovery-scan

- **`ACTING`** → category `acting_interrupted`, action **`manual_review_required`** (no auto-resume)
- **`WAITING_APPROVAL`** → `needs_human`
- **`TERMINATED` + FAILED** → `review_or_resume`
- Stale locks under `lock_dir` → `stale_lock` / `blocked`

## CI note

- GitHub Actions and default `config/loop-pilot.yaml` use **`state_backend: json`**
- 0.4-a sqlite commands are **opt-in** via fixture or local config
- Unit tests for db/recovery run in CI via pytest (temp sqlite paths)

## Related docs

- [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) — full 0.4 four sub-phases
- [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) — implementation order
- [08-security-and-recovery.md](08-security-and-recovery.md) — recovery rules

## Next step

0.4-b: inbox / queue / today CLI and `inbox_items` table. See [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.2.
