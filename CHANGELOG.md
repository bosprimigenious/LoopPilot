# Changelog

## Unreleased

### Fixed (Codex PR #8 — patch review gate on feat/0.5-safe-autonomy)

- **P0-1 patch review gate**: `patch.diff` + `SUCCEEDED` runs enter `PARTIAL` / `needs_review` via `mark_patch_run_waiting_review()` and InternLoop `_finalize()`; `gate_result.json` is `needs_review`; weekly summary excludes them from Completed.
- **P0-2 direct-finalize approve**: `approve` on `patch.diff` runs sets `approved` + `TERMINATED` + `SUCCEEDED` + `gate=pass` without `resume_requested`; `resume()` rejects approved finalized runs.
- **P1-1 manifest self-exclusion**: `artifact-manifest.json` no longer lists itself (avoids stale self-checksum).
- **P1-2 report_path priority**: prefers canonical report paths before manifest fallback; `kind=="report"` filter on manifest entries.

See [logs/2026-06-21-patch-review-gate-fix.md](docs/development/logs/2026-06-21-patch-review-gate-fix.md).

### Added

- **0.5-prep fail-closed safety** (Codex review): `readiness.py`, prep-stage BLOCKED for schedule install/uninstall and unattended daily; `InstallStatus` PREVIEWED/BLOCKED/INSTALLED; deferred review preserved on sync; `verify_0_5_prep.py`
- **0.4-c Review Layer**: review CLI (sqlite-only), migration v4 `review_items`, verify 22/22
- **0.5-a SafetyGate v1**: `src/loop_pilot/safety/`; gated `schedule install --yes` (ready stage only); `schedule status`; `safety doctor`

### Stabilization

- **0.4.0b1 stabilization in progress.** 0.4-c review layer delivered; Truthful 0.4 Milestone A aggregate gate may still have open items. See [50-0.4-stabilization-and-truthful-acceptance.md](docs/development/50-0.4-stabilization-and-truthful-acceptance.md).

### Documentation

- **0.5 Safe Autonomy (0.5-prep only)**: fail-closed prep scaffolding on `feat/0.5-safe-autonomy` — not full 0.5 implementation
  - [logs/2026-06-21-0.5-prep-codex-fixes.md](docs/development/logs/2026-06-21-0.5-prep-codex-fixes.md) — Codex review fixes
  - [verify_0_5_prep.py](scripts/verify_0_5_prep.py) — `0.5-prep: PASS` / `0.5-ready: NOT READY`
- **0.5 Safe Autonomy (revised plan)**: SafetyGate first, no daemon — spec drafted; 0.5-prep allowed in parallel
  - [50-personal-daily-loop-0.5-spec.md](docs/development/50-personal-daily-loop-0.5-spec.md) — full spec (Steps 0–4, 0.5-a/b/c/d)
  - [52-0.5-revised-plan-rationale.md](docs/development/52-0.5-revised-plan-rationale.md) — why SafetyGate first, why 0.4-c blocker, why no daemon
  - [53-0.5-acceptance.md](docs/development/53-0.5-acceptance.md) — acceptance for 0.5-a/b/c/d
  - [15-0.5-安全自治.md](docs/zh/15-0.5-安全自治.md) — Chinese guide
  - [CURSOR_0.5_SAFE_AUTONOMY_PROMPT.md](prompts/CURSOR_0.5_SAFE_AUTONOMY_PROMPT.md) — implementation prompt (blocked on Truthful 0.4 Milestone A)
  - [2026-06-21-0.5-plan-revision.md](docs/development/logs/2026-06-21-0.5-plan-revision.md) — decision log
  - [CURSOR_0.4C_REVIEW_LAYER_PROMPT.md](prompts/CURSOR_0.4C_REVIEW_LAYER_PROMPT.md) — Priority 1 blocker note

- **0.4-d spec (planned)**: Daily Summary + Schedule Preview + Daily Dry-Run — usable daily dashboard, not feature demo
  - [48-personal-daily-loop-0.4d-acceptance.md](docs/development/48-personal-daily-loop-0.4d-acceptance.md) — four-layer acceptance + 8 must-haves + SQL queries
  - [49-daily-summary-engine-design.md](docs/development/49-daily-summary-engine-design.md) — summary engine architecture
  - [14-0.4d-日汇总与调度预览.md](docs/zh/14-0.4d-日汇总与调度预览.md) — Chinese guide
  - [CURSOR_0.4D_DAILY_SUMMARY_PROMPT.md](prompts/CURSOR_0.4D_DAILY_SUMMARY_PROMPT.md) — implementation prompt
  - [verify_0_4d_acceptance.py](scripts/verify_0_4d_acceptance.py) — readiness gate skeleton
  - [2026-06-21-0.4d-spec-and-prompt.md](docs/development/logs/2026-06-21-0.4d-spec-and-prompt.md) — decision log
- **0.4-c spec (planned)**: Review Layer — AI suggests only; human decides; no auto-approve
  - [45-personal-daily-loop-0.4c-acceptance.md](docs/development/45-personal-daily-loop-0.4c-acceptance.md) — acceptance (8 must-haves, schema v3, CLI)
  - [46-review-layer-design.md](docs/development/46-review-layer-design.md) — architecture
  - [12-0.4c-审阅与决策层.md](docs/zh/12-0.4c-审阅与决策层.md) — Chinese guide
  - [CURSOR_0.4C_REVIEW_LAYER_PROMPT.md](prompts/CURSOR_0.4C_REVIEW_LAYER_PROMPT.md) — implementation prompt
  - [verify_0_4c_acceptance.py](scripts/verify_0_4c_acceptance.py) — readiness gate skeleton
  - [2026-06-21-0.4c-spec-and-prompt.md](docs/development/logs/2026-06-21-0.4c-spec-and-prompt.md) — decision log
  - **Not shipped**: review CLI, ReviewAgent, migration v3
- **Output interface spec**: [47-output-interface-spec.md](docs/development/47-output-interface-spec.md) — human Markdown vs machine JSON/JSONL; canonical per-run artifact layout; `gate_result.json`; `artifact-manifest.json` `human_readable` flag; 0.4-b vs 0.4-c matrix
- **Chinese guide**: [13-输出接口-人看MD机器看JSON.md](docs/zh/13-输出接口-人看MD机器看JSON.md)
- **Review layer** (see 0.4-c spec above for full set)
- **Schema**: [schemas/gate_result.schema.json](schemas/gate_result.schema.json)
- **Decision log**: [logs/2026-06-21-output-interface-md-json.md](docs/development/logs/2026-06-21-output-interface-md-json.md)
- **Pointers** in [17-data-contracts.md](docs/development/17-data-contracts.md), [07-data-and-reports.md](docs/development/07-data-and-reports.md)

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
