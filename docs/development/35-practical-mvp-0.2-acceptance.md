# Practical MVP 0.2 Acceptance Checklist

Version: **0.2.0-practical-mvp** (package `0.2.0a1`)

## Scope

- Controlled demo workspaces under `examples/`
- MockAdapter only (`allow_real_adapters: false`)
- No CursorCLIAdapter, SQLite recovery, or approve/reject CLI

## Config

- [ ] `config/loop-pilot.yaml` defines `workspaces.intern_demo` and `workspaces.paper_demo`
- [ ] `config/sources.yaml` defines `profiles.demo`

## CLI

- [ ] `loop-pilot run intern --workspace examples/intern_demo --dry-run`
- [ ] `loop-pilot run paper --workspace examples/paper_demo --dry-run`
- [ ] `loop-pilot run daily-news --source-profile demo --dry-run`
- [ ] `loop-pilot run all --profile demo --dry-run`
- [ ] 0.1 `--fixture` commands still work

## Artifacts

Each run produces:

- [ ] Primary loop report (development / paper / daily-news)
- [ ] `review-required.md` with recommended human action
- [ ] `next-actions.md` (paper also writes `next_research_tasks.md` when PARTIAL)
- [ ] DailyNews: `intern-candidates.md`, `paper-candidates.md`, `candidate-actions.json`

## Verification

```bash
python -m pip install -e ".[dev]"
pytest -q
loop-pilot doctor
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
```

## Expected outcomes (dry-run)

| Command | Outcome |
|---------|---------|
| intern demo | `succeeded` |
| paper demo | `partial` (SOURCE REQUIRED) |
| daily-news demo | `succeeded` |
| all --profile demo | daily_news/intern succeeded, paper partial |

## Out of scope (defer to 0.3+)

- Real adapters / Cursor CLI
- SQLite recovery and resume CLI
- Interactive approve/reject commands
