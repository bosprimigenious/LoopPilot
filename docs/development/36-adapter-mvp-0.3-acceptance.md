# Adapter MVP 0.3 Acceptance Checklist

Version: **0.3.0a1** (adapter-mvp safety alpha)

> **0.3 ≠ legacy "V1".** This phase proves Mock→Real Adapter with strict safety gates. It does **not** include SQLite recovery, approval CLI, Web UI, plugins, or PyPI.

**Last acceptance run:** [2026-06-21-0.3-executable-acceptance.md](logs/2026-06-21-0.3-executable-acceptance.md)（可执行 L1/L2/L3）；[2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md)（静态分层）

## Prerequisites (gate before starting)

- [x] **0.2 acceptance passed** — see [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md); Layer 2 demo profile green 2026-06-21
- [x] Branch `adapter-mvp-0.3` — **on `adapter-mvp-0.3`** (2026-06-21 executable run)
- [ ] Design docs reviewed: [37-adapter-safety-policy.md](37-adapter-safety-policy.md), [38-toolbroker-design.md](38-toolbroker-design.md) — files not present in repo
- [x] Mini / 0.2 test baseline green on branch start — `pytest -q` → **109 passed** (2026-06-21)

## Executable acceptance (L1 / L2 / L3) — 2026-06-21

Branch: `adapter-mvp-0.3` · Runner: automated · Log: [logs/2026-06-21-0.3-executable-acceptance.md](logs/2026-06-21-0.3-executable-acceptance.md)

### L1 — 0.1 + 0.2 regression — **PASS**

| # | Command | Outcome | Notes |
|---|---------|---------|-------|
| 1.1a | `run intern --fixture simple_python_bug --dry-run` | succeeded | no crash |
| 1.1b | `run paper --fixture unsupported_claim --dry-run` | partial | not succeeded (SOURCE REQUIRED OK) |
| 1.1c | `run daily-news --fixture github_star_snapshots --dry-run` | succeeded | 4 items day2 |
| 1.1d | `run all --fixture-set mini --dry-run` | composite OK | intern/daily_news succeeded, paper partial |
| 1.1e | daily_news candidate artifacts | OK | `intern-candidates.md`, `paper-candidates.md`, `candidate-actions.json` |
| 1.2a | `run intern --workspace examples/intern_demo --dry-run` | succeeded | |
| 1.2b | `run paper --workspace examples/paper_demo --dry-run` | partial | |
| 1.2c | `run daily-news --source-profile demo --dry-run` | succeeded | 2 items |
| 1.2d | `run all --profile demo --dry-run` | composite OK | intern/daily_news succeeded, paper partial |

### L2 — Adapter core — **PASS** (DeepSeek live: MANUAL)

| # | Command | Outcome | Notes |
|---|---------|---------|-------|
| 2.1 | `adapters list` | PASS | mock enabled; real disabled |
| 2.2 | `adapters doctor` | PASS | exit 0; real blocked by default |
| 2.3 | `run intern ... --adapter cursor_cli --dry-run` | blocked | `allow_real_adapters=false`; no adapter-call-trace (expected) |
| 2.4 | `run paper ... --adapter deepseek --dry-run` | blocked | outer gate; **SKIP MANUAL** without key |

### L3 — Safety — **PASS** (fake_adapter: WARN)

| # | Check | Result |
|---|-------|--------|
| 3.1 | Default gate blocks cursor_cli | PASS — blocked, auditable reason |
| 3.2 | Default gate blocks deepseek | PASS — blocked, no Traceback |
| 3.3 | Unknown adapter no crash | PASS — `fake_adapter` → mock fallback (WARN: should BLOCK) |
| 3.4 | `pytest -q` | PASS — 109 passed |
| 3.5 | `ruff check .` | PASS |
| 3.6 | `loop-pilot doctor` | PASS |
| 3.7 | No raw API key in artifacts/state | PASS — N/A (no key set); env names in messages only |

**Automation:** `python scripts/verify_0_3_acceptance.py` → 20/20 PASS (no credentials)

## Scope

### In scope

| Area | Deliverable | Status |
|------|-------------|--------|
| **Adapter layer** | `BaseAdapter` protocol; `MockAdapter` hardened; `CodingCLIAdapter`; `APIModelAdapter` / OpenAI-compatible | Partial — `cursor_cli.py`, `openai_compatible.py`, legacy `coding_cli.py`/`api_model.py` coexist |
| **Registry** | `AdapterRegistry` + factory; reject cli/api when `allow_real_adapters=false` | [x] `registry.py`, `factory.py`, `preflight.py` |
| **ModelRouter** | Capability routing, data class, budget/deadline, fallback, trace logging | [x] core routing; trace artifact partial |
| **ToolBroker** | Allowlisted file/git/command/http; audit trail; dry-run mode | [x] `tools/broker.py` + unit tests; loop integration incomplete |
| **CLI** | `loop-pilot adapters list`, `loop-pilot adapters doctor` | [x] verified 2026-06-21 |
| **Loops** | Intern/Paper/DailyNews each complete ≥1 controlled **real** run with explicit opt-in | [ ] not run (no API key / cursor CLI) |
| **Tests** | Unit + integration; mock vs real paths separated; 0.1/0.2 regression unchanged | [x] 109 tests pass |

### Explicitly out of scope

| Excluded | Belongs to |
|----------|------------|
| SQLite recovery / `resume` | **0.4** |
| `approve` / `reject` / `cancel` CLI | **0.4** |
| OS scheduler / daily automation | **0.4** |
| Web UI | Not on roadmap |
| PyPI / `init demo` | **0.5 可选** / **0.8 Optional Public** — 见 [34-version-roadmap-0x.md](34-version-roadmap-0x.md) |
| Plugin marketplace | **0.7** Personal Extensions（本地 only） |
| Team / Dashboard | **1.1+** |
| Vector DB / RAG | Not 0.3 |
| auto push / PR / deploy | Never |

## Config & defaults

- [x] `runtime.allow_real_adapters` defaults **`false`** in `config/loop-pilot.yaml` — evidence: line 22
- [x] Real adapter entries in `config/models.yaml` / `config/adapters.yaml` present but marked disabled until opt-in — `adapters list` shows `disabled (allow_real_adapters=false)`
- [x] CLI flag `--allow-real-adapters` required **in addition** to config for real calls — verified Layer 6
- [x] `doctor` reports real adapters as disabled/warn when keys missing — `adapters doctor` exit 1 with blocked real adapters

## Adapter layer checklist

### BaseAdapter protocol

- [x] `capabilities() -> AdapterCapabilities` — `adapters/base.py`
- [x] `healthcheck() -> HealthStatus` (no side effects) — cursor_cli / openai_compatible
- [x] `execute(request, timeout, cancellation) -> AdapterResult` — implemented
- [x] `estimate_cost(request) -> CostEstimate` — implemented
- [x] `normalize_error(error) -> LoopPilotError` — implemented
- [x] Full `AdapterResult` per [19-adapter-specifications.md](19-adapter-specifications.md) — core fields present

### MockAdapter

- [x] Deterministic fixture responses (success, timeout, invalid schema, rate limit) — `mock_adapter.py` scenarios
- [x] Usage / transcript / tool_calls fields populated where applicable
- [x] No network; no real workspace writes

### CodingCLIAdapter

- [x] Configurable command template + argv array (no shell string concatenation) — `cursor_cli.py`
- [x] `cwd` restricted to approved worktree
- [x] Env allowlist; hard timeout + cancellation
- [x] stdout/stderr/transcript artifacts; exit code captured
- [ ] Pre/post git/file snapshot hooks — not implemented
- [x] dry-run: read/plan only, no writes

### APIModelAdapter

- [x] OpenAI-compatible + optional Anthropic-compatible config — `openai_compatible.py`
- [x] Structured output + JSON Schema; one repair attempt on parse failure — parse + error path
- [x] 429/5xx backoff; auth/4xx no retry — HTTP error mapping
- [x] Token/cost/request-id in usage; secrets redacted in artifacts — `_redact` helpers + tests

### AdapterRegistry + factory

- [x] Registers mock, coding_cli, api_model types — `factory.py`
- [x] When `allow_real_adapters=false`, factory raises or returns BLOCKED for cli/api — Layer 5 + `test_adapter_gating.py`
- [x] `adapters list` shows id, type, enabled/disabled, capabilities summary — Layer 4

## ModelRouter checklist

- [x] Routes by `model_role` from `config/models.yaml` (`model_roles` schema)
- [x] Filters by required capabilities (`supports_tools`, `supports_file_write`, etc.)
- [x] Enforces data class: `SECRET` → BLOCKED; `SENSITIVE` → authorized adapters only — `test_model_router.py`
- [ ] Budget and deadline hard filters — partial (BudgetManager separate)
- [x] Same-role fallback with exclusion reasons logged — `RouterDecision.excluded`
- [x] No silent downgrade to mock when real was requested and failed policy — override path blocks
- [ ] Selection rationale written to trace / routing artifact — partial

## ToolBroker checklist

See [38-toolbroker-design.md](38-toolbroker-design.md).

- [x] Single entry point for file read/write, git/worktree, subprocess, HTTP fetch — `tools/broker.py` (HTTP fetch via connectors, not broker yet)
- [x] PolicyEngine invoked before every operation — policy checks in broker methods
- [ ] dry-run suppresses writes; reads allowed where configured — not fully wired
- [ ] Every call → trace event + optional artifact — not loop-wide
- [ ] Loops and Agents cannot bypass ToolBroker for shell/file/network — **not enforced in loops yet**; unit tests pass

## Loop integration checklist

### InternLoop

- [ ] Real repo + approved worktree + CodingCLIAdapter (opt-in) — MANUAL (no cursor CLI)
- [x] Test chain capture; diff review; out-of-bound diff → BLOCKED — fixture paths
- [ ] Task priority: user task > yesterday next action > real failure > DailyNews candidate — not 0.3 scope
- [x] Default dry-run; `--allow-write` explicit for writes — policy engine

### PaperLoop

- [ ] Real paper workspace; APIModelAdapter for research/writing/evaluation roles — MANUAL (no API key)
- [x] Citation key, BibTeX, DOI/arXiv checks; claim-evidence mapping — demo partial outcome
- [x] Insufficient evidence → SOURCE REQUIRED / BLOCKED (no fabrication) — paper partial on demo

### DailyNewsLoop

- [ ] `--real-sources`: RSS/Atom, GitHub snapshot API, paper metadata (limited connectors) — not implemented
- [x] Dedup, confidence, Inbox routing; single-source failure does not kill loop — demo profile
- [x] GitHub star baseline on first run; delta ranking on subsequent runs — fixture day1/day2

## CLI checklist

- [x] `loop-pilot adapters list` — mock + configured real adapters; disabled state visible
- [x] `loop-pilot adapters doctor` — mock OK; missing-key real adapters WARN/BLOCKED with clear message
- [ ] `loop-pilot run intern --workspace ... --allow-write --allow-real-adapters` (controlled real run) — MANUAL
- [ ] `loop-pilot run paper --workspace ... --allow-write --allow-real-adapters` — MANUAL
- [ ] `loop-pilot run daily-news --real-sources --allow-real-adapters` — not implemented
- [ ] `loop-pilot run all --real-sources --allow-write-intern --dry-run-paper` (composite flags documented) — not implemented

## Test checklist

- [x] `tests/unit/test_allow_real_adapters.py` extended for registry + CLI flags
- [x] `tests/unit/test_model_router.py` — capability, data class, fallback
- [x] `tests/unit/test_v1_adapters.py` — mock + adapter contract (real tests gated by env)
- [x] New ToolBroker unit tests — `test_tool_broker_policy.py`
- [x] Integration: real adapter tests skipped unless credentials — `test_adapter_blocked_by_default.py`
- [x] Full suite: `pytest -q` — 0.1 + 0.2 tests still pass (109)

## Verification commands (target at 0.3 ship)

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
loop-pilot doctor
loop-pilot adapters list
loop-pilot adapters doctor

# Regression (must stay green, no real adapters)
loop-pilot run all --fixture-set mini --dry-run
loop-pilot run all --profile demo --dry-run

# Real adapter (requires allow_real_adapters=true + env keys + explicit flags)
loop-pilot run intern --workspace examples/intern_demo --allow-write --allow-real-adapters
loop-pilot run paper --workspace examples/paper_demo --allow-write --allow-real-adapters
loop-pilot run daily-news --real-sources --allow-real-adapters
```

**2026-06-21 executable run:** L1/L2/L3 PASS (see log); real-adapter live commands MANUAL/SKIP; `verify_0_3_acceptance.py` 20/20.

## Acceptance criteria (definition of done)

1. [x] **`allow_real_adapters=false`**: any cli/api adapter invocation blocked at Registry/Router with auditable reason — Layer 5 PASS
2. [ ] **`allow_real_adapters=true` + CLI flag + credentials**: each of Intern, Paper, DailyNews completes one documented controlled run — MANUAL
3. [x] **`adapters list` / `adapters doctor`**: operational; mock always OK — Layer 4 PASS
4. [ ] **ToolBroker**: all file/git/command/http from loops go through broker; bypass attempts fail tests — broker exists; loop bypass not closed
5. [x] **Regression**: all 0.2 acceptance commands still pass with defaults unchanged — **L1 PASS** (2026-06-21 executable)
6. [ ] **Documentation**: [39-next-steps-0.3.md](39-next-steps-0.3.md) phases marked complete — file not present

## Verdict (2026-06-21 executable)

| Layer | Result |
|-------|--------|
| L1 | **PASS** |
| L2 | **PASS** (DeepSeek live: MANUAL) |
| L3 | **PASS** (unknown adapter silent mock: WARN) |

**§六 must-pass (safety alpha):** L1 + L2 gate + L3 **met**. Full DoD item 2 (controlled real runs) and ToolBroker loop enforcement **not met**.

**One line:** Real adapters are **safely gated off by default**; system **stable and regressions green**; **0.3 safety alpha合格，完整 DoD 未达**.

## Expected outcomes (real runs, when enabled)

| Loop | Typical outcome | Failure modes that must be handled |
|------|-----------------|-------------------------------------|
| Intern | `succeeded` or `blocked` (policy) | timeout, schema error, diff out of bounds |
| Paper | `partial` or `succeeded` | SOURCE REQUIRED, citation mismatch |
| DailyNews | `succeeded` | single connector failure → degraded, not crash |

## Related documents

- [34-version-roadmap-0x.md §4](34-version-roadmap-0x.md#4-03-real-adapter-mvp030-adapter-mvp)
- [19-adapter-specifications.md](19-adapter-specifications.md)
- [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)
- [38-toolbroker-design.md](38-toolbroker-design.md)
- Run log: [logs/2026-06-21-0.3-executable-acceptance.md](logs/2026-06-21-0.3-executable-acceptance.md)
- Prior run: [logs/2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md)
- Automation: [scripts/verify_0_3_acceptance.py](../../scripts/verify_0_3_acceptance.py)
