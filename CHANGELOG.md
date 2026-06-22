# Changelog

## Unreleased

### Documentation

- **README refresh (2026-06-22)**: 根 `README.md` 重写 — inline SVG 徽章、0.3→0.4→0.5 里程碑条、Loop 状态机 + review gate 流程图；验收门禁表（`verify_0_3` / `0_4b` / `0_4c` / `0_4d` / `0_4` / `0_5_prep`）；反映 PR #8 合入后 **11/11 READY**、**254 pytest**
- **Development log**: [logs/2026-06-22-main-sync-readme-refresh.md](docs/development/logs/2026-06-22-main-sync-readme-refresh.md) — main 同步、Truthful 0.4 合入事实、README 重写摘要
- **Development index**: `docs/development/README.md` 更新当前工程焦点为 `main` + PR #8 merged

### Fixed (Codex PR #8 — truthful patch review acceptance)

- **P0-1 patch review gate**: `patch.diff` runs finalize as `WAITING_APPROVAL` / `PARTIAL` / `needs_review` (not completed) until human approve; `gate_result.json` is `needs_review`; weekly summary excludes them from Completed.
- **P0-2 direct-finalize approve**: `approve` on `patch.diff` runs sets `approved` + `TERMINATED` + `SUCCEEDED` + `gate=pass` without `resume_requested`; `resume()` rejects approved finalized runs.
- **P1-1 manifest self-exclusion**: `artifact-manifest.json` no longer lists itself; `terminal_artifacts` scans run dir and recomputes sha256 from disk (atomic write).
- **P1-2 report_path priority**: prefers `report.md`, `development-report.md`, `paper-development-report.md`, `daily-news-report.md`; manifest fallback only for `kind=="report"`.
- **P1-3 InternLoop manifest**: InternLoop no longer writes `artifact-manifest.json`; canonical finalizer is the sole writer.
- **P2-1 patch phase**: `patch.diff` runs awaiting review stay `WAITING_APPROVAL` (not `TERMINATED`) until human approve; outcome remains `PARTIAL` / `needs_review`.
- **P2-2 review_suggestion manifest**: `review_suggestion.json` is written before `finalize_terminal_artifacts()` so the sealed manifest includes it with a matching checksum.
- **P2-3 patch trace truthfulness**: InternLoop appends the terminal trace event after review gating so `loop_trace.jsonl` reflects `partial` / `needs_review`, not `succeeded`.
- **P2-4 approve DB manifest sync**: `ReviewService.approve()` on patch runs now persists the refreshed `artifact-manifest.json` payload to SQLite `artifact_manifests` via `save_artifact_manifest()` so disk and DB share one truth after `gate=pass`.
- **P2-6 decided review immutability**: `approve` / `reject` / `defer` / `cancel` call `_require_decidable_item()` — only `pending` or `deferred` items accept a decision; already `approved` / `rejected` / `cancelled` items raise `ReviewDecisionError`.
- **P2-7 reject/cancel DB manifest sync**: `reject` and `cancel` on patch runs now persist the refreshed `artifact-manifest.json` (`gate=blocked`) to SQLite `artifact_manifests`, symmetric with approve.
- **P2-5 canonical manifest schema**: `finalize_terminal_artifacts()` emits `schema_version: "1"`; `schemas/artifact-manifest.json` requires `schema_version`, `run_id`, `loop_type`, `terminal_outcome`, `artifacts` with `additionalProperties=false`; `validate_artifact_manifest()` passes on generated and post-approve manifests.
- **P2 deferred sync**: `upsert_pending` keeps `deferred` items until `deferred_until`; approved/rejected/cancelled never revert to pending.
- **0.3 acceptance**: intern fixture/workspace expected outcome updated to `partial` (truthful review semantics).

### Fixed (from merged main / PR #7 — 0.5-prep)

- **P2 review CLI subcommands**: `review approve|reject|defer|cancel|resume` registered under the `review` group; root commands kept as backward-compatible aliases.
- **P2 summary decided-review**: `SummaryCollector` excludes runs whose `review_items` status is `rejected`, `cancelled`, or `approved` from daily/weekly `needs_review`.
- **P2 scheduler install command**: ready-stage `schedule install --yes` embeds `--no-dry-run` so installed daily runs execute for real.
- **P1 adapter execution path**: `SafetyGate.check("adapter.invoke")` before real adapter instantiation when wired from Orchestrator.
- **P2 locks PermissionError**: `_pid_alive` treats `PermissionError` from `os.kill` as live PID (fail-closed stale removal).
- **P2 file locks fail-closed**: unknown/legacy lock payloads are not treated as stale; only unlink when dead PID is confirmed.
- **`verify_0_4_acceptance.py` bootstrap**: insert `src` into `sys.path` before `loop_pilot` imports (source checkout without install).

### Added

- **0.4-c Review Layer**: review CLI (sqlite-only), migration v4 `review_items`, patch-review behavior tests; aggregate `verify_0_4` 11/11 READY
- **0.5-prep fail-closed safety** (from main): `readiness.py`, prep-stage BLOCKED for schedule install/uninstall; `verify_0_5_prep.py`
- **0.5-a SafetyGate v1** (from main): `src/loop_pilot/safety/`; gated `schedule install --yes` (ready stage only); `schedule status`; `safety doctor`

### Stabilization

- **0.4.0b1 Truthful 0.4 baseline.** Codex PR #8 + P2 on `stabilize/0.4-truthful-acceptance`; aggregate `verify_0_4_acceptance.py` target 11/11 READY. Historical note: pre-0.4.0b1 docs described `approve → resume_requested`; current semantics are **direct-finalize** for `patch.diff` runs. See [50-0.4-stabilization-and-truthful-acceptance.md](docs/development/50-0.4-stabilization-and-truthful-acceptance.md).

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
