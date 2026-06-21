# Adapter MVP 0.3 Acceptance Checklist

Version: **0.3.0-adapter-mvp** (target package `0.3.0a1`)

> **0.3 ≠ legacy "V1".** This phase proves Mock→Real Adapter with strict safety gates. It does **not** include SQLite recovery, approval CLI, Web UI, plugins, or PyPI.

## Prerequisites (gate before starting)

- [ ] **0.2 acceptance passed** — see [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md)
- [ ] Branch `adapter-mvp-0.3` created from tagged `v0.2.0a1`
- [ ] Design docs reviewed: [37-adapter-safety-policy.md](37-adapter-safety-policy.md), [38-toolbroker-design.md](38-toolbroker-design.md)
- [ ] Mini / 0.2 test baseline green on branch start

## Scope

### In scope

| Area | Deliverable |
|------|-------------|
| **Adapter layer** | `BaseAdapter` protocol; `MockAdapter` hardened; `CodingCLIAdapter`; `APIModelAdapter` / OpenAI-compatible |
| **Registry** | `AdapterRegistry` + factory; reject cli/api when `allow_real_adapters=false` |
| **ModelRouter** | Capability routing, data class, budget/deadline, fallback, trace logging |
| **ToolBroker** | Allowlisted file/git/command/http; audit trail; dry-run mode |
| **CLI** | `loop-pilot adapters list`, `loop-pilot adapters doctor` |
| **Loops** | Intern/Paper/DailyNews each complete ≥1 controlled **real** run with explicit opt-in |
| **Tests** | Unit + integration; mock vs real paths separated; 0.1/0.2 regression unchanged |

### Explicitly out of scope

| Excluded | Belongs to |
|----------|------------|
| SQLite recovery / `resume` | **0.4** |
| `approve` / `reject` / `cancel` CLI | **0.4** |
| OS scheduler / daily automation | **0.4** |
| Web UI | Not on roadmap |
| PyPI / `init demo` | **0.5** |
| Plugin marketplace | **0.6+** |
| Vector DB / RAG | Not 0.3 |
| auto push / PR / deploy | Never |

## Config & defaults

- [ ] `runtime.allow_real_adapters` defaults **`false`** in `config/loop-pilot.yaml`
- [ ] Real adapter entries in `config/models.yaml` present but marked disabled until opt-in
- [ ] CLI flag `--allow-real-adapters` (or equivalent) required **in addition** to config for real calls
- [ ] `doctor` reports real adapters as disabled/warn when keys missing

## Adapter layer checklist

### BaseAdapter protocol

- [ ] `capabilities() -> AdapterCapabilities`
- [ ] `healthcheck() -> HealthStatus` (no side effects)
- [ ] `execute(request, timeout, cancellation) -> AdapterResult`
- [ ] `estimate_cost(request) -> CostEstimate`
- [ ] `normalize_error(error) -> LoopPilotError`
- [ ] Full `AdapterResult` per [19-adapter-specifications.md](19-adapter-specifications.md)

### MockAdapter

- [ ] Deterministic fixture responses (success, timeout, invalid schema, rate limit)
- [ ] Usage / transcript / tool_calls fields populated where applicable
- [ ] No network; no real workspace writes

### CodingCLIAdapter

- [ ] Configurable command template + argv array (no shell string concatenation)
- [ ] `cwd` restricted to approved worktree
- [ ] Env allowlist; hard timeout + cancellation
- [ ] stdout/stderr/transcript artifacts; exit code captured
- [ ] Pre/post git/file snapshot hooks
- [ ] dry-run: read/plan only, no writes

### APIModelAdapter

- [ ] OpenAI-compatible + optional Anthropic-compatible config
- [ ] Structured output + JSON Schema; one repair attempt on parse failure
- [ ] 429/5xx backoff; auth/4xx no retry
- [ ] Token/cost/request-id in usage; secrets redacted in artifacts

### AdapterRegistry + factory

- [ ] Registers mock, coding_cli, api_model types
- [ ] When `allow_real_adapters=false`, factory raises or returns BLOCKED for cli/api
- [ ] `adapters list` shows id, type, enabled/disabled, capabilities summary

## ModelRouter checklist

- [ ] Routes by `model_role` from `config/models.yaml` (`model_roles` schema)
- [ ] Filters by required capabilities (`supports_tools`, `supports_file_write`, etc.)
- [ ] Enforces data class: `SECRET` → BLOCKED; `SENSITIVE` → authorized adapters only
- [ ] Budget and deadline hard filters
- [ ] Same-role fallback with exclusion reasons logged
- [ ] No silent downgrade to mock when real was requested and failed policy
- [ ] Selection rationale written to trace / routing artifact

## ToolBroker checklist

See [38-toolbroker-design.md](38-toolbroker-design.md).

- [ ] Single entry point for file read/write, git/worktree, subprocess, HTTP fetch
- [ ] PolicyEngine invoked before every operation
- [ ] dry-run suppresses writes; reads allowed where configured
- [ ] Every call → trace event + optional artifact
- [ ] Loops and Agents cannot bypass ToolBroker for shell/file/network

## Loop integration checklist

### InternLoop

- [ ] Real repo + approved worktree + CodingCLIAdapter (opt-in)
- [ ] Test chain capture; diff review; out-of-bound diff → BLOCKED
- [ ] Task priority: user task > yesterday next action > real failure > DailyNews candidate
- [ ] Default dry-run; `--allow-write` explicit for writes

### PaperLoop

- [ ] Real paper workspace; APIModelAdapter for research/writing/evaluation roles
- [ ] Citation key, BibTeX, DOI/arXiv checks; claim-evidence mapping
- [ ] Insufficient evidence → SOURCE REQUIRED / BLOCKED (no fabrication)

### DailyNewsLoop

- [ ] `--real-sources`: RSS/Atom, GitHub snapshot API, paper metadata (limited connectors)
- [ ] Dedup, confidence, Inbox routing; single-source failure does not kill loop
- [ ] GitHub star baseline on first run; delta ranking on subsequent runs

## CLI checklist

- [ ] `loop-pilot adapters list` — mock + configured real adapters; disabled state visible
- [ ] `loop-pilot adapters doctor` — mock OK; missing-key real adapters WARN/BLOCKED with clear message
- [ ] `loop-pilot run intern --workspace ... --allow-write --allow-real-adapters` (controlled real run)
- [ ] `loop-pilot run paper --workspace ... --allow-write --allow-real-adapters`
- [ ] `loop-pilot run daily-news --real-sources --allow-real-adapters`
- [ ] `loop-pilot run all --real-sources --allow-write-intern --dry-run-paper` (composite flags documented)

## Test checklist

- [ ] `tests/unit/test_allow_real_adapters.py` extended for registry + CLI flags
- [ ] `tests/unit/test_model_router.py` — capability, data class, fallback
- [ ] `tests/unit/test_v1_adapters.py` — mock + adapter contract (real tests gated by env)
- [ ] New ToolBroker unit tests
- [ ] Integration: real adapter tests skipped unless `LOOP_PILOT_ALLOW_REAL_ADAPTERS=1` + credentials
- [ ] Full suite: `pytest -q` — 0.1 + 0.2 tests still pass

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

## Acceptance criteria (definition of done)

1. **`allow_real_adapters=false`**: any cli/api adapter invocation blocked at Registry/Router with auditable reason.
2. **`allow_real_adapters=true` + CLI flag + credentials**: each of Intern, Paper, DailyNews completes one documented controlled run.
3. **`adapters list` / `adapters doctor`**: operational; mock always OK.
4. **ToolBroker**: all file/git/command/http from loops go through broker; bypass attempts fail tests.
5. **Regression**: all 0.2 acceptance commands still pass with defaults unchanged.
6. **Documentation**: [39-next-steps-0.3.md](39-next-steps-0.3.md) phases marked complete; safety policy unchanged or versioned.

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
- [37-adapter-safety-policy.md](37-adapter-safety-policy.md)
- [38-toolbroker-design.md](38-toolbroker-design.md)
