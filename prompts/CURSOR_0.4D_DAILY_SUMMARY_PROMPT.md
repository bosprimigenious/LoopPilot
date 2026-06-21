# Cursor Prompt: 0.4-d Daily Summary + Schedule Preview + Daily Dry-Run

## 目标（中文）

实现 **0.4-d 个人日用闭环的最后一层**：summary engine（today/week）、schedule 预览（print + install --dry-run）、`run daily --dry-run` 安全编排。验收标准不是「能跑 demo」，而是「能当每日仪表盘用」——数据来自真实 SQLite 与 artifacts，不是 mock。

## Task (English)

Implement the 0.4-d daily dashboard layer:

1. **Summary CLI** — `loop-pilot summary today|week` generating Markdown per [47-output-interface-spec.md](../docs/development/47-output-interface-spec.md)
2. **SQL aggregator** — collect from `inbox_items`, `queue_items`, `today_items`, `runs`, `review_items`, `task_events`, and artifact paths
3. **Markdown renderer** — seven-section `daily-summary.md`; weekly `week-summary.md`
4. **Schedule preview** — `schedule print`; `schedule install --dry-run` (no OS writes)
5. **Daily dry-run** — `run daily --dry-run` orchestrates verify + recovery-scan + today + summary refresh without executing real loops
6. **Tests + verify script** — integration tests and `scripts/verify_0_4d_acceptance.py`
7. **Docs** — update acceptance expected outputs on green run

---

## Prerequisites

- **0.4-a** green: sqlite backend, `db migrate/verify`, `recovery-scan`
- **0.4-b** green: inbox / queue / today CLI
- **0.4-c** green (or documented partial): review list + artifacts for Needs Review section

Run before starting:

```bash
python scripts/verify_0_4a_acceptance.py
python scripts/verify_0_4b_acceptance.py
python scripts/verify_0_4c_acceptance.py
```

---

## Constraints (mandatory)

| Rule | Detail |
|------|--------|
| NO schedule install | `schedule install --yes` MUST refuse or defer to 0.5; never write crontab/systemd/schtasks |
| NO real API in run daily | `run daily` without `--dry-run` MUST fail; no adapter calls in daily path |
| NO auto approve | Summary reads review state; does not approve/reject |
| Data from SQLite | Collector MUST query real tables; no hard-coded demo counts in CLI path |
| sqlite-only | Summary/schedule/daily commands require `state_backend=sqlite` |
| Human MD / machine JSON | Follow [47-output-interface-spec.md](../docs/development/47-output-interface-spec.md); acceptance asserts paths and SQL, not Markdown prose |

---

## Implementation checklist

- [ ] `summary today` CLI — writes `var/artifacts/daily/<date>/daily-summary.md`
- [ ] `summary week` CLI — writes `var/artifacts/weekly/<week>/week-summary.md`
- [ ] `SummaryCollector` — SQL + artifact aggregation ([49 design](../docs/development/49-daily-summary-engine-design.md))
- [ ] `renderer.py` — seven daily sections + weekly sections
- [ ] `SummaryStore` — upsert `summaries` table (migration v3+)
- [ ] `schedule print` — platform snippets (cron/systemd/windows-task-scheduler)
- [ ] `schedule install --dry-run` — preview file only; stdout confirms no install
- [ ] `run daily --dry-run` — verify + recovery + today + summary; no new run dirs
- [ ] Wire `cli_summary.py`, `cli_schedule.py`, `run daily` in `cli.py`
- [ ] Integration tests: `tests/integration/test_daily_summary_cli.py`
- [ ] Unit tests: `tests/unit/test_summary_collector.py`, `tests/unit/test_scheduler_printer.py`
- [ ] `scripts/verify_0_4d_acceptance.py` — readiness gate + smoke
- [ ] Update [48 acceptance](../docs/development/48-personal-daily-loop-0.4d-acceptance.md) expected output table after green run
- [ ] Write delivery log `docs/development/logs/2026-06-21-0.4d-delivery.md`

---

## File layout

```text
src/loop_pilot/summary/
├── __init__.py
├── collector.py      # SQL + artifact aggregation
├── models.py         # DailySummaryData, WeeklySummaryData
├── renderer.py       # Markdown templates
├── service.py        # generate_daily / generate_weekly
├── store.py          # summaries table
└── weekly.py         # ISO week helpers

src/loop_pilot/scheduler/
├── __init__.py
├── printer.py        # schedule print
├── installer.py      # dry-run preview; refuse --yes
└── profiles.py       # daily-morning profile

src/loop_pilot/runtime/daily_run.py   # DailyRunService
src/loop_pilot/cli_summary.py
src/loop_pilot/cli_schedule.py
src/loop_pilot/cli.py                 # register summary, schedule, run daily

tests/integration/test_daily_summary_cli.py
tests/unit/test_summary_collector.py
tests/unit/test_scheduler_printer.py
scripts/verify_0_4d_acceptance.py
```

Remove or delegate legacy `src/loop_pilot/reporting/daily_summary.py` if it duplicates `summary/`.

---

## Acceptance (copy from 48)

### Section V — 8 must-haves

1. **Daily dashboard usable** — open `daily-summary.md` without SQLite
2. **Weekly rollup usable** — `week-summary.md` aggregates 7-day activity
3. **Data from real stores** — SQLite + filesystem, not fixture-only counts
4. **Traceability** — every list item links to `run_id`, `event_id`, or artifact path
5. **Schedule safety** — print and install --dry-run never write OS scheduler
6. **Daily dry-run safety** — no real loops or adapter calls
7. **Pipeline closure** — Inbox → Queue → Today → Run → Review → Summary reflected
8. **Regression** — 0.1 / 0.2 / 0.3 / 0.4-a / 0.4-b / 0.4-c green

### Commands

```bash
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config summary today
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config summary week
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config schedule print
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config schedule install --dry-run
loop-pilot --config-dir tests/fixtures/acceptance_0_4a/config run daily --dry-run
python scripts/verify_0_4d_acceptance.py
pytest tests/integration/test_daily_summary_cli.py -q
```

### Expected outputs

| Command | Expected |
|---------|----------|
| `summary today` | `Daily summary: var/artifacts/daily/<date>/daily-summary.md` |
| `summary week` | `Weekly summary: var/artifacts/weekly/<week>/week-summary.md` |
| `schedule print` | Scheduler snippet on stdout |
| `schedule install --dry-run` | Preview path; "No system scheduler entries were created." |
| `run daily --dry-run` | Verify + recovery + summary steps; no new run artifacts |

---

## References

| Doc | Purpose |
|-----|---------|
| [48-personal-daily-loop-0.4d-acceptance.md](../docs/development/48-personal-daily-loop-0.4d-acceptance.md) | Full checklist + SQL queries |
| [49-daily-summary-engine-design.md](../docs/development/49-daily-summary-engine-design.md) | Architecture |
| [47-output-interface-spec.md](../docs/development/47-output-interface-spec.md) | daily-summary.md path |
| [13-输出接口-人看MD机器看JSON.md](../docs/zh/13-输出接口-人看MD机器看JSON.md) | Chinese output guide |
| [40-personal-daily-loop-0.4-spec.md](../docs/development/40-personal-daily-loop-0.4-spec.md) | Parent 0.4 spec |
| [14-0.4d-日汇总与调度预览.md](../docs/zh/14-0.4d-日汇总与调度预览.md) | Chinese cognitive layer |
