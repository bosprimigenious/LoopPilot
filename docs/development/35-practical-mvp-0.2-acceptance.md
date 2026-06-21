# Practical MVP 0.2 Acceptance Checklist

Version: **0.2.0-practical-mvp** (package `0.2.0a1`)

**Acceptance date**: 2026-06-21  
**Environment**: Windows 10, Python 3.12, repo `C:\AIModel_Zoo\LoopPolit`, branch `main`

## Scope

- Controlled demo workspaces under `examples/`
- MockAdapter only (`allow_real_adapters: false`)
- No CursorCLIAdapter live calls, SQLite recovery, or approve/reject CLI

## Config

- [x] `config/loop-pilot.yaml` defines `workspaces.intern_demo` and `workspaces.paper_demo`
- [x] `config/sources.yaml` defines `profiles.demo`

## CLI

- [x] `loop-pilot run intern --workspace examples/intern_demo --dry-run`
- [x] `loop-pilot run paper --workspace examples/paper_demo --dry-run`
- [x] `loop-pilot run daily-news --source-profile demo --dry-run`
- [x] `loop-pilot run all --profile demo --dry-run`
- [x] 0.1 `--fixture` commands still work

## Artifacts

Each run produces:

- [x] Primary loop report (development / paper / daily-news)
- [x] `review-required.md` with recommended human action
- [x] `next-actions.md` (paper also writes `next_research_tasks.md` when PARTIAL)
- [x] DailyNews: `intern-candidates.md`, `paper-candidates.md`, `candidate-actions.json`

## Full verification (2026-06-21)

```bash
python -m pip install -e ".[dev]"
python scripts/bootstrap_local.py --dry-run
ruff check .
pytest -q
loop-pilot doctor
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
loop-pilot status
```

### Command results summary

| # | Command | Result | Notes |
|---|---------|--------|-------|
| 1 | `pip install -e ".[dev]"` | **PASS** | `loop-pilot==0.2.0a1` installed |
| 2 | `bootstrap_local.py --dry-run` | **PASS** | Would create `var/checkpoints`; state/config skipped |
| 3 | `ruff check .` | **PASS** | All checks passed |
| 4 | `pytest -q` | **PASS** | **91 passed** in ~22s |
| 5 | `loop-pilot doctor` | **PASS** | Config, fixtures, state dirs, MockAdapter default |
| 6 | `run intern --fixture simple_python_bug --dry-run` | **PASS** | `succeeded` |
| 7 | `run paper --fixture unsupported_claim --dry-run` | **PASS** | `partial` (SOURCE REQUIRED) |
| 8 | `run daily-news --fixture github_star_snapshots --dry-run` | **PASS** | `succeeded` (4 items day2) |
| 9 | `run all --fixture-set mini --dry-run` | **PASS** | daily_news/intern succeeded, paper partial |
| 10 | `run intern --workspace examples/intern_demo --dry-run` | **PASS** | `succeeded` |
| 11 | `run paper --workspace examples/paper_demo --dry-run` | **PASS** | `partial` |
| 12 | `run daily-news --source-profile demo --dry-run` | **PASS** | `succeeded` (2 items profile demo) |
| 13 | `run all --profile demo --dry-run` | **PASS** | daily_news/intern succeeded, paper partial |
| 14 | `loop-pilot status` | **PASS** | Lists recent TERMINATED runs |

**Overall**: all 14 commands **PASS**. Tag candidate: `v0.2.0a1`.

## Expected outcomes (dry-run)

| Command | Outcome | Actual (2026-06-21) |
|---------|---------|---------------------|
| intern demo | `succeeded` | ✅ succeeded |
| paper demo | `partial` (SOURCE REQUIRED) | ✅ partial |
| daily-news demo | `succeeded` | ✅ succeeded |
| all --profile demo | daily_news/intern succeeded, paper partial | ✅ matched |

## Out of scope (defer to 0.3+)

- Real adapters / Cursor CLI live calls
- SQLite recovery and resume CLI
- Interactive approve/reject commands

See [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) for next phase.
