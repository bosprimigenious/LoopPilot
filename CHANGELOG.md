# Changelog

## [0.3.0a1] - 2026-06-21

### 0.3.0a1 polish (release line)

- **Safety**: `fake_adapter` / unknown `--adapter` → explicit **BLOCKED** (no silent mock fallback)
- **Audit**: blocked adapter runs write `adapter-call-trace.jsonl` with `blocked_reason`, `dry_run`, `allow_real_adapters`; referenced in `artifact-manifest.json`
- **CI**: `python scripts/verify_0_3_acceptance.py` in GitHub Actions
- **CLI**: `adapters doctor --verbose` for blocked reason details
- **Tests**: `test_unknown_adapter_is_blocked`, `test_fake_adapter_is_blocked`, blocked trace + manifest integration tests
- **Docs**: [43-0.3-polish-roadmap-a-to-f.md](docs/development/43-0.3-polish-roadmap-a-to-f.md), live adapter MANUAL template

### Adapter MVP (initial alpha)

- **Adapter 层**: `CursorCLIAdapter`, `OpenAICompatibleAdapter`, `AdapterRequest`, `AdapterHealth`, `AdapterBlockedError`
- **ModelRouter**: role-based selection; real adapters blocked when `allow_real_adapters=false`
- **ToolBroker**: command/file/git policy enforcement (`src/loop_pilot/tools/`)
- **Connectors**: minimal github/arxiv/rss for `live-small` source profile
- **CLI**: `loop-pilot adapters list|doctor`, `--adapter` on run commands, `--source-profile live-small`
- **Artifacts**: adapter-call-trace.jsonl, patch.diff, tool-results.json, proposed-revision.md
- **Config**: `config/adapters.yaml`; updated models/sources
- **Docs**: 36–39 development guides; acceptance checklist
- **Tests**: adapter gating, ToolBroker policy, secret redaction, mock contract integration

### Unchanged from 0.2

- No SQLite recovery, approve/reject CLI, Web UI, PyPI, or auto deploy
- Default remains MockAdapter + dry-run for CI

## [0.2.0a1] - 2026-06-20

### Practical MVP

- Demo workspaces under `examples/`
- Human review Markdown outputs
- `--workspace` and `--source-profile demo`

## [0.1.0] - Mini MVP

- Three Loop fixtures with MockAdapter
- JSON state, CI dry-run acceptance
