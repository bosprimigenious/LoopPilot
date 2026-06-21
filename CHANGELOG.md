# Changelog

## [0.4.0a1] - 2026-06-21

### 0.4-a State reliability

- **CLI**: `loop-pilot db status|migrate|backup|verify` (requires `state_backend=sqlite`)
- **CLI**: `loop-pilot recovery-scan` — stale/interrupted/WAITING_APPROVAL/ACTING/FAILED/stale lock
- **CLI**: `loop-pilot doctor` — sqlite writability and schema checks; json mode hints sqlite requirement
- **Storage**: versioned migrations v1 (`runs`, `checkpoints`, `reviews`, `artifact_manifests`, `events`, `run_locks`)
- **Recovery**: ACTING interrupted → `manual_review_required` (no auto-resume)
- **Tests**: `test_db_ops`, `test_recovery_scan`; full suite 141 passed
- **Config**: default remains `state_backend=json`; acceptance fixture at `tests/fixtures/acceptance_0_4a/config`
- **Docs**: [43-personal-daily-loop-0.4a-acceptance.md](docs/development/43-personal-daily-loop-0.4a-acceptance.md), [11-0.4a-SQLite与恢复扫描.md](docs/zh/11-0.4a-SQLite与恢复扫描.md), [2026-06-21-0.4a-delivery.md](docs/development/logs/2026-06-21-0.4a-delivery.md)

### Unchanged / deferred to 0.4-b+

- inbox/queue/today (0.4-b), review/approve/defer (0.4-c), summary/schedule (0.4-d)

## [0.3.0b1] - 2026-06-21

### ToolBroker full Loop integration (0.3.0b1)

- **InternLoop**: `_run_pytest` / `_apply_fix` route through ToolBroker (no direct subprocess/workspace writes)
- **PaperLoop**: working-copy read/write via ToolBroker; `tool-results.json` audit trail
- **DailyNewsLoop**: connector `fetch_source` via ToolBroker `http_get` audit
- **Audit**: `tool-results.json` includes broker `audit` array (`event`, `tool`, `status`, `duration_ms`, `policy`)
- **Tests**: `test_toolbroker_loop_enforcement`, `test_tool_results_audit`, `test_controlled_live_run_evidence`
- **Docs**: b1 delivery log; MANUAL template with config.local instructions; [2026-06-21-0.3-b1-delivery.md](docs/development/logs/2026-06-21-0.3-b1-delivery.md)

### Unchanged / deferred

- Live DeepSeek/Cursor runs remain MANUAL (template + mock evidence)
- SQLite, resume, approve/reject, inbox/queue → **0.4-a+**

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
