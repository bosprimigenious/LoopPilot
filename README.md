# LoopPilot

LoopPilot is a controlled runtime for three personal AI work loops:

- **InternLoop**: resolve one real development problem with verification.
- **PaperLoop**: advance one evidence-backed research or writing gap.
- **DailyNewsLoop**: select high-value engineering and research signals from offline snapshots.

## Canonical names

- Product/project: `LoopPilot`
- Distribution name: `loop-pilot`
- CLI command: `loop-pilot`
- Python import and source package: `loop_pilot`

The unseparated lowercase form `looppilot` is not used for commands, imports, or source paths.

## Mini status

The Mini implementation provides deterministic offline scenarios with MockAdapter, real `pytest` for Intern fixtures, JSONL trace, Artifact Manifest, and Markdown reports.

## Quick start

```bash
pip install -e ".[dev]"
python scripts/bootstrap_local.py
loop-pilot doctor
```

## Mini commands

```bash
loop-pilot doctor
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
loop-pilot status
loop-pilot inspect <run-id>
```

## Run tests

```bash
pytest -q
```

## Documentation

- [Development plan](DEVELOPMENT_PLAN.md)
- [Complete development documentation](docs/development/README.md)
- [Mini run path](docs/development/25-mini-run-path.md)
- [Cursor Mini implementation prompt](prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md)

## Deferred (V1+)

- `resume`, `approve`, `reject`, `cancel` CLI commands
- SQLite recovery, real model/Git/news connectors
- OS scheduling and PyPI publishing

## Safety

Read [SECURITY.md](SECURITY.md) before adding Adapters, Tools, or credentials.
