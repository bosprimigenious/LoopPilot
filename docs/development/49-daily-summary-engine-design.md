# 49 Daily Summary Engine Design

> **Status:** Design spec for 0.4-d daily summary, schedule preview, and daily dry-run orchestration.  
> **Acceptance:** [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md)  
> **Output contract:** [47-output-interface-spec.md](47-output-interface-spec.md) — `daily-summary.md` path and human/machine split  
> **Parent spec:** [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.4

---

## 1. Purpose

The summary engine turns scattered SQLite state and run artifacts into a **single daily dashboard** the maintainer can open every morning. It is not a report generator demo — it must reflect real inbox, queue, run, and review data.

```text
SQLite (runs, tasks, reviews, events)
        +
Artifact filesystem (report.md, gate_result.json, …)
        │
        ▼
SummaryCollector  →  DailySummaryData / WeeklySummaryData
        │
        ▼
Renderer (Markdown)  →  daily-summary.md / week-summary.md
        │
        ▼
SummaryStore  →  summaries table (metadata + counts)
```

Schedule preview and daily dry-run are sibling modules that **never mutate OS schedulers** and **never execute real loops** in 0.4-d.

---

## 2. Module layout

| Module | Path | Responsibility |
|--------|------|----------------|
| Summary package | `src/loop_pilot/summary/` | Collector, renderer, models, store, service |
| `collector.py` | SQL + artifact aggregation | Query runs, inbox, queue, today, reviews; read gate/report paths |
| `renderer.py` | Markdown templates | Seven-section daily; weekly rollup sections |
| `models.py` | Dataclasses | `DailySummaryData`, `WeeklySummaryData`, row types |
| `store.py` | SQLite persistence | Upsert `summaries` table |
| `service.py` | Orchestration | `generate_daily()`, `generate_weekly()` |
| `weekly.py` | Week boundaries | ISO week label, date range in config timezone |
| CLI summary | `src/loop_pilot/cli_summary.py` | `summary today`, `summary week` |
| Scheduler package | `src/loop_pilot/scheduler/` | Print/install preview only |
| `printer.py` | Platform snippets | cron / systemd / windows-task-scheduler text |
| `installer.py` | Dry-run guard | Preview file; refuse `--yes` until 0.5 |
| `profiles.py` | Schedule profiles | Daily command template (`run daily --dry-run`, etc.) |
| CLI schedule | `src/loop_pilot/cli_schedule.py` | `schedule print`, `schedule install --dry-run` |
| Daily run | `src/loop_pilot/runtime/daily_run.py` | `run daily --dry-run` orchestration |
| CLI wiring | `src/loop_pilot/cli.py` | Register `summary`, `schedule`, `run daily` |

Legacy path `src/loop_pilot/reporting/daily_summary.py` (if present) SHOULD delegate to `summary/` or be removed to avoid duplicate writers.

---

## 3. Data sources

### SQLite tables

| Table | Used for |
|-------|----------|
| `runs` | Today's runs; outcome, phase, timestamps |
| `events` | State transitions; audit for summary metadata |
| `review_items` | Needs Review section; pending decisions |
| `inbox_items` | Inbox Updates; new tasks by date |
| `queue_items` | Tomorrow priorities; queue head |
| `today_items` | Today section; daily focus |
| `task_events` | Promote/defer/approve audit trail |
| `summaries` | Persisted summary metadata (migration v3+) |
| `artifact_manifests` | Optional join for path resolution |

### Artifact filesystem

| File | Used for |
|------|----------|
| `report.md` / loop-specific report | Run row link in summary |
| `gate_result.json` | Gate column; Needs Review reason |
| `review_required.md` | Human review link (path only in machine checks) |
| `candidate-actions.json` | DailyNews inbox routing evidence |
| `artifact-manifest.json` | Fallback path index when DB path stale |

Collector MUST read gate from JSON, not parse Markdown.

---

## 4. SummaryCollector design

```python
class SummaryCollector:
    def collect_daily(self, date_str: str | None) -> DailySummaryData: ...
    def collect_weekly(self, week: str | None) -> WeeklySummaryData: ...
```

**Daily collection steps:**

1. Resolve target date in `runtime.timezone`.
2. Query `runs` where `started_at` or `finished_at` date matches.
3. Join artifact dir: `var/artifacts/<loop>/<run-id>/` for report and gate.
4. Query pending reviews via `review_items` + `WAITING_APPROVAL` runs.
5. Query `today_items` + `queue_items` for Today section.
6. Query `inbox_items` created on date; tag DailyNews source separately.
7. Run `scan_recovery()` (read-only) for blocked/stale notes.
8. Derive Tomorrow from queue priority excluding deferred.
9. Build highlights (≤3) from runs completed, reviews cleared, inbox imported.

**Weekly collection:** Roll up last 7 days or ISO week range; aggregate loop stats, completed titles, open reviews.

---

## 5. Renderer design

`render_daily_summary(data: DailySummaryData) -> str` emits fixed headings (acceptance checks heading presence, not prose):

1. `## 1. 今日最重要结论`
2. `## 2. Today`
3. `## 3. Runs`
4. `## 4. Needs Review`
5. `## 5. Inbox Updates`
6. `## 6. Blocked`
7. `## 7. Tomorrow`

YAML front matter optional; if added, use [17-data-contracts.md §12](17-data-contracts.md) fields: `schema_version`, `summary_date`, `generated_at`, `timezone`.

Weekly renderer sections: Highlights, Completed, Needs Review, Blocked, Loop stats, Suggestions.

---

## 6. SummaryStore and migration

Migration v3 (or next) adds:

```sql
CREATE TABLE IF NOT EXISTS summaries (
    id TEXT PRIMARY KEY,
    summary_type TEXT NOT NULL,       -- 'daily' | 'weekly'
    summary_date TEXT NOT NULL,       -- YYYY-MM-DD or YYYY-Www
    path TEXT NOT NULL,
    status TEXT NOT NULL,
    run_count INTEGER DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    blocked_count INTEGER DEFAULT 0,
    inbox_count INTEGER DEFAULT 0,
    generated_at TEXT NOT NULL,
    UNIQUE(summary_type, summary_date)
);
```

Upsert on each `generate_*` call; idempotent regeneration for same date.

---

## 7. CLI extensions

### `cli_summary.py`

```text
loop-pilot summary today [--date YYYY-MM-DD]
loop-pilot summary week [--week YYYY-Www]
```

- Requires `state_backend=sqlite` via shared `_require_sqlite()` from `cli_tasks.py`.
- Prints output path on success.

### `cli_schedule.py`

```text
loop-pilot schedule print [--target cron|systemd|windows-task-scheduler]
loop-pilot schedule install [--dry-run] [--target ...] [--yes]
```

- `--dry-run` (default for install): write `var/artifacts/schedule/schedule-preview.md`; stdout confirms no OS write.
- `--yes`: MUST exit non-zero with message pointing to 0.5; no crontab/systemctl/schtasks execution.

### `cli.py` — `run daily`

```text
loop-pilot run daily [--dry-run]   # --dry-run required in 0.4-d
```

Orchestration via `DailyRunService.run_daily(dry_run=True)`:

1. Acquire lock `loop:daily`.
2. `verify_database()` — fail fast on schema errors.
3. `scan_recovery()` — count findings; do not auto-fix.
4. `TodayService.render()` — planned items for stdout.
5. `SummaryService.generate_daily()` — refresh dashboard.
6. Release lock; return `DailyRunResult`.

Non-dry-run MUST raise or exit with "0.4-d only supports --dry-run".

---

## 8. Scheduler profiles

`profiles.py` defines the command block printed by `schedule print`:

| Profile | Suggested schedule | Command |
|---------|-------------------|---------|
| `daily-morning` | 07:30 local | `loop-pilot run daily --dry-run` |
| `daily-news` | 08:00 local | `loop-pilot run daily-news --dry-run` (preview only in 0.4-d) |

Print output is documentation for the maintainer; install remains dry-run only.

---

## 9. Testing strategy

| Test file | Coverage |
|-----------|----------|
| `tests/unit/test_summary_collector.py` | Date filtering, gate read, highlight logic |
| `tests/unit/test_scheduler_printer.py` | Platform snippet generation |
| `tests/integration/test_daily_summary_cli.py` | summary today/week, schedule, run daily dry-run |

Tests use temp sqlite + temp artifact dirs (same pattern as 0.4-a/b integration tests).

Acceptance script: `scripts/verify_0_4d_acceptance.py` — readiness gate + CLI smoke.

---

## 10. Non-goals (0.4-d)

- Real cron/systemd/Task Scheduler registration
- Live loop execution inside `run daily`
- Auto-approve before summary generation
- LLM-generated narrative in summary (deterministic aggregation only)
- Multi-user or shared dashboard (1.3 preview)

---

## 11. Related

- [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md)
- [47-output-interface-spec.md](47-output-interface-spec.md)
- [46-review-layer-design.md](46-review-layer-design.md) — review data feeds Needs Review section
- [07-data-and-reports.md](07-data-and-reports.md) — storage policy
- [13-source-and-crawler-plan.md](13-source-and-crawler-plan.md) — DailyNews source context
