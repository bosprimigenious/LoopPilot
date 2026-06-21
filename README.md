# LoopPilot

LoopPilot is a controlled runtime for three personal AI work loops:

- **InternLoop**: resolve one real development problem with verification.
- **PaperLoop**: advance one evidence-backed research or writing gap.
- **DailyNewsLoop**: select high-value engineering and research signals from offline snapshots.

## Canonical names

- Product/project: `LoopPilot`
- GitHub repository: [bosprimigenious/LoopPilot](https://github.com/bosprimigenious/LoopPilot)
- Distribution name: `loop-pilot`
- CLI command: `loop-pilot`
- Python import and source package: `loop_pilot`

The unseparated lowercase form `looppilot` is not used for commands, imports, or source paths.

## Version roadmap (0.x)

LoopPilot uses a **0.x release track** (not simple "V1" naming):

| Version | Name | Focus |
|---------|------|-------|
| **0.1** | mini | Three dry-run Loops, MockAdapter, CI |
| **0.2** | practical-mvp | Controlled demo workspaces, dry-run/report (current) |
| 0.3 | adapter-mvp | Mock→Real Adapter, ToolBroker |
| 0.4 | recovery-and-automation | SQLite, recovery, approval, scheduling |
| 0.5 | public-beta | PyPI, init demo, open-source onboarding |
| 0.6 | plugin-ecosystem | Local plugins; custom Loop/Skill/Connector |
| 0.7 | evaluation-benchmark | Benchmarks, model comparison, Eval reports |
| 0.8 | team-cloud-preview | Project workspaces, roles, Dashboard preview |
| 0.9 | release-candidate | API/config/DB freeze, security audit, doc freeze — **no new features** |
| 1.0 | stable | Formal semver stability promise after 0.9 RC |

See [docs/development/34-version-roadmap-0x.md](docs/development/34-version-roadmap-0x.md) for full milestones.

## Practical MVP (0.2)

0.2 moves from pure fixtures to **controlled demo workspaces** under `examples/`, still defaulting to **MockAdapter + dry-run**. Human review is Markdown-only (`review-required.md`, `next-actions.md`) — no approve/reject CLI yet.

Demo commands:

```bash
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
```

Acceptance checklist: [docs/development/35-practical-mvp-0.2-acceptance.md](docs/development/35-practical-mvp-0.2-acceptance.md)

0.1 `--fixture` commands remain supported for regression.

## Mini-MVP status (0.1)

Mini-MVP is an **architecture scaffold** with deterministic offline scenarios. It proves orchestration, state transitions, Policy Gate, Artifact Manifest, JSONL trace, and Markdown reports without connecting to real external systems.

0.1 defaults:

- `runtime.allow_real_adapters: false` — only `MockAdapter` is permitted unless explicitly enabled
- `runtime.state_backend: json` — local JSON snapshot store (no SQLite recovery in 0.1)
- No real Cursor CLI, Codex, DeepSeek API, private workspaces, or live crawlers
- No `resume`, `approve`, `reject`, or `cancel` CLI commands (deferred to **0.4**)

Later stages: 0.2 adds real workspaces; 0.3 adds real adapters; 0.4 adds SQLite recovery and scheduling.

## Acceptance commands

Run these from the repository root after install:

```bash
python -m pip install -e ".[dev]"
loop-pilot doctor
pytest -q
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

Optional bootstrap for first-time setup:

```bash
python scripts/bootstrap_local.py
```

## Quick start

```bash
pip install -e ".[dev]"
python scripts/bootstrap_local.py
loop-pilot doctor
```

## V1/MVP commands (SQLite backend)

When `runtime.state_backend: sqlite` is configured:

```bash
loop-pilot resume <run-id>
loop-pilot approve <run-id>
loop-pilot reject <run-id> --reason "..."
loop-pilot cancel <run-id>
loop-pilot report <run-id>
python scripts/migrate_state.py --dry-run
python scripts/backup_state.py --dry-run
python scripts/install_scheduler.py --dry-run
python scripts/run_regression.py --dry-run
```

Mini JSON backend rejects V1 recovery commands by design.

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
ruff check .
```

## Documentation

- [Development plan](DEVELOPMENT_PLAN.md)
- [Complete development documentation](docs/development/README.md)
- [0.x version roadmap (0.1→1.0)](docs/development/34-version-roadmap-0x.md)
- [Next steps: finish 0.1, then 0.2](docs/development/33-next-steps-0.2.md)
- [Mini run path](docs/development/25-mini-run-path.md)
- [Practical MVP 0.2 acceptance](docs/development/35-practical-mvp-0.2-acceptance.md)
- [Mini-MVP delivery log](docs/development/logs/2026-06-20-mini-mvp-delivery.md)
- [Cursor Mini implementation prompt](prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md)

## Deferred (0.3+)

- **0.3**: real model/CLI adapters (`allow_real_adapters` gated)
- **0.4**: `resume`, `approve`, `reject`, `cancel`, SQLite recovery, OS scheduling
- **0.5**: PyPI publishing, init demo, open-source docs
- **0.6–0.8**: plugins, eval benchmarks, team preview (documented only)
- **0.9**: stability freeze / RC — testing and docs, not features
- **1.0**: stable release after 0.9 RC

## Safety

Read [SECURITY.md](SECURITY.md) before adding Adapters, Tools, or credentials.
