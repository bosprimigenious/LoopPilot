# Cursor Prompt — 0.3 Adapter MVP

> **文档体系：** 中文目标见下方 §目标；English execution spec 见 §Task 起。  
> 日常理解：[docs/zh/README.md](../docs/zh/README.md) · 英文规格：[docs/en-core.md](../docs/en-core.md)

Copy everything below §--- into Cursor Agent after opening the LoopPilot repository on branch `adapter-mvp-0.3`.

---

## 目标（中文）

在 **0.2 已验收** 基础上，实现 **0.3 Adapter MVP**：

- Mock→Real Adapter 可控接入（Cursor CLI、OpenAI-compatible）
- 默认 **关闭** 真实 Adapter（`allow_real_adapters=false`）
- ToolBroker 管控 file/git/command
- `adapters list` / `adapters doctor` CLI
- 保持 0.1 fixture 与 0.2 demo profile 全绿

**不要实现：** SQLite recovery、approve/reject/cancel CLI、PyPI、插件、Web UI（均属 0.4+）。

## Task

Implement **0.3 Adapter MVP** only. Branch baseline: tagged `v0.2.0a1` or current `adapter-mvp-0.3`.

### In scope

| Area | Deliverable |
|------|-------------|
| Adapter layer | `BaseAdapter` protocol; hardened `MockAdapter`; `cursor_cli`; `openai_compatible` |
| Registry | `AdapterRegistry` + factory; block real adapters when `allow_real_adapters=false` |
| ModelRouter | Capability routing, budget/deadline, fallback, trace logging |
| ToolBroker | Allowlisted file/git/command/http; audit trail; dry-run mode |
| CLI | `loop-pilot adapters list`, `loop-pilot adapters doctor` |
| Tests | Unit + integration; mock vs real paths separated; 0.1/0.2 regression unchanged |

### Out of scope

- SQLite / `resume` / approval CLI → **0.4**
- PyPI / `init demo` → **0.5**
- Plugins, Web UI, live crawlers, auto push/PR/deploy

## Read before coding

1. `docs/en-core.md`
2. `docs/development/36-adapter-mvp-0.3-acceptance.md`
3. `docs/development/37-adapter-safety-policy.md`
4. `docs/development/38-toolbroker-design.md`
5. `docs/development/19-adapter-specifications.md`
6. `docs/development/29-model-routing-and-runtime-policy.md`
7. `docs/development/02-runtime-mechanism.md`

If documents conflict, follow authority rules in `docs/development/README.md`.

## Constraints

- Python package: `loop_pilot`; CLI: `loop-pilot`
- `runtime.allow_real_adapters` defaults **`false`**
- Real adapter calls require config **and** CLI `--allow-real-adapters`
- Blocked real adapter → `AdapterBlockedError`, outcome **BLOCKED**
- Agents cannot instantiate adapters or choose models directly
- Policy Gate mandatory before every write
- Secret redaction in trace/artifacts (`<redacted>`)
- Do not commit, push, or modify remotes unless explicitly asked
- Do not treat `ideas.md` as specification

## First response before edits

Before modifying files, respond with:

1. Your understanding of 0.3 scope vs 0.4+
2. Files you plan to create or modify
3. Safety gating strategy for real adapters
4. Tests that prove blocked vs allowed paths
5. Any doc conflicts or ambiguities
6. Commands you intend to run

## Acceptance

All must pass:

```bash
pytest -q
loop-pilot doctor
loop-pilot adapters list
loop-pilot adapters doctor
loop-pilot run intern --workspace examples/intern_demo --adapter cursor_cli --dry-run
# expect: BLOCKED (allow_real_adapters=false)
loop-pilot run all --fixture-set mini --dry-run
loop-pilot run all --profile demo --dry-run
```

Checklist: `docs/development/36-adapter-mvp-0.3-acceptance.md`

## Verification log

Record results in `docs/development/logs/` when acceptance is run locally.
