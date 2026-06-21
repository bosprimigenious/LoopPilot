# 50 Personal Daily Loop — 0.5 Safe Autonomy Specification

> **Version tag**: `0.5.0-safe-autonomy` (parallel to [34-version-roadmap-0x.md](34-version-roadmap-0x.md) §7 Personal Beta; this spec focuses on **unattended safe operation**)  
> **Parent roadmap**: [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)  
> **Safety baseline**: [37-adapter-safety-policy.md](37-adapter-safety-policy.md), `schemas/gate_result.schema.json`  
> **Review layer design**: [46-review-layer-design.md](46-review-layer-design.md), [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md)

---

## 1. Goal

0.5 **Safe Autonomy** upgrades the personal daily loop from manual + dry-run preview to **OS-scheduled unattended runs with graded safety**, defaulting to **fail-closed**:

1. **SafetyGate v1** — unified gate evaluation (Levels 0–4), writes `gate_result.json`
2. **Real schedule install** — `schedule install --yes` registers with Windows Task Scheduler / cron / systemd (with audit + uninstall)
3. **Unattended daily safe run** — `loop-pilot run daily --unattended --safe` (lock, db verify, backup, recovery-scan, safe loops, review queue, summary)
4. **Crash recovery + observability** — auditable failure paths, recovery acceptance, unattended run logs

**Never (at any level)**: auto approve, auto commit, auto push, bypass ToolBroker/PolicyEngine.

**Not a 0.5 requirement**: long-running daemon. OS scheduler calls `loop-pilot run daily --unattended --safe` directly. `daemon start` is a **future enhancement** only.

---

## 2. Prerequisites (hard blockers)

| Milestone | Status | Notes |
|-----------|--------|-------|
| 0.4-b Task Entry | ✅ complete | inbox/queue/today green |
| 0.4-d Summary + Schedule Preview | ✅ complete | summary + `schedule install --dry-run` |
| **0.4-c Review Layer** | ❌ **blocker** | 0/16 NOT READY — must pass before formal 0.5 |
| 0.5 Spec | ✅ drafted | this document |
| 0.5 Implementation | ⏸ blocked by 0.4-c | no Step 1 until 0.4-c complete |

**Rule**: Do **not** start 0.5 Step 1 (SafetyGate v1) until 0.4-c Review Layer is complete and acceptance is green.

### 0.4-c exit criteria (Step 0)

Complete the Review Layer per [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md):

- `review list` / `review show`
- `approve` / `reject` / `defer` / `cancel` / `resume` with resume policy
- `review_required.md`, `gate_result.json`, `review_items`, `task_events` on every review-queue run
- **No auto approve** — human decision required for every review item

---

## 3. Increment over 0.4-d

| Capability | 0.4-d | 0.5 |
|------------|-------|-----|
| `schedule print` / `install --dry-run` | ✅ | ✅ unchanged |
| `schedule install --yes` | ❌ `NotImplementedError` | ✅ via SafetyGate + explicit `--yes` + audit |
| `run daily --dry-run` | ✅ | ✅ unchanged; maps to Level 0 |
| `run daily --unattended --safe` | ❌ | ✅ primary unattended path |
| Daemon (`daemon start`) | ❌ | ❌ **not 0.5** — future enhancement |
| OS scheduler target command | `run daily --dry-run` | `run daily --unattended --safe` (after install --yes) |

**Existing code (0.4-d)**:

- `src/loop_pilot/scheduler/installer.py` — `preview_install()` only; `install_schedule(yes=True)` raises `NotImplementedError`
- `src/loop_pilot/cli_schedule.py` — `--yes` without `--dry-run` fails; default writes `var/artifacts/schedule/schedule-preview.md`
- `src/loop_pilot/scheduler/profiles.py` — `DEFAULT_PROFILE.command = "loop-pilot run daily --dry-run"`

---

## 4. SafetyGate levels (0–4)

`SafetyGate` evaluates before every unattended run. Result written to `gate_result.json` in the run artifact directory.

| Level | Name | Allowed | Blocked |
|-------|------|---------|---------|
| **0** | Observe | `db verify`, recovery-scan, today preview, summary refresh; **zero** adapter/loop execution | Any real/mock adapter call |
| **1** | Collect | Level 0 + read-only adapters (fetch/RSS/read-only CLI per policy) | Workspace writes, mutating subprocess |
| **2** | Mock execute | Level 1 + **mock** loop steps (existing dry-run adapter path) | `allow_real_adapters`, network mutating |
| **3** | Real guarded | Level 2 + real adapters when config **and** CLI confirm; every run produces `needs_review` artifacts | Auto approve, git push |
| **4** | Real bounded | Level 3 + pre-configured loop whitelist and in-budget auto-continue (still per-step trace); review queue never auto-cleared | Auto merge, deploy, secret exfil paths |

**Default safe mode**: allows Levels **0–3**, **blocks Level 4**.

**Module layout** (`src/loop_pilot/safety/`):

| File | Responsibility |
|------|----------------|
| `levels.py` | Level enum, capability matrix |
| `policy.py` | Config + CLI flag resolution, max level cap |
| `gate.py` | Pre-run evaluation, pass/block decision |
| `audit.py` | Gate decision audit trail |

**Config example** (`loop-pilot.yaml`):

```yaml
runtime:
  state_backend: sqlite
  unattended:
    default_level: 0
    max_level: 3              # hard cap; Level 4 blocked in default safe mode
    require_cli_flag: true    # run daily must pass --unattended --safe
```

**CLI**:

```bash
loop-pilot run daily --unattended --safe              # default safe mode (levels 0–3)
loop-pilot run daily --unattended --safe --level 0  # equivalent to --dry-run behavior
loop-pilot run daily --unattended --safe --level 2
```

Gate failure: `gate=blocked`, run marked failed, **no** infinite retry.

---

## 5. CLI command inventory (0.5)

### 5.1 Schedule

| Command | Notes |
|---------|-------|
| `loop-pilot schedule print [--target]` | unchanged |
| `loop-pilot schedule install [--dry-run]` | unchanged (default dry-run) |
| `loop-pilot schedule install --yes [--target]` | **0.5**: writes OS scheduler entry; must pass SafetyGate; prints task id / cron line; audit logged |
| `loop-pilot schedule uninstall [--yes]` | remove installed entry; dry-run when no `--yes` |
| `loop-pilot schedule status` | installed?, next run time (read-only OS query) |

### 5.2 Run daily (primary unattended path)

| Command | Notes |
|---------|-------|
| `loop-pilot run daily --dry-run` | preserved; maps to Level 0 |
| `loop-pilot run daily --unattended --safe [--level N]` | **0.5 primary path** — lock, db verify, backup, recovery-scan, safe loops, review queue, summary |
| `loop-pilot run daily` (no flags) | **reject** or equivalent `--unattended --safe --level 0` (prefer reject) |

**Unattended run sequence** (no daemon required):

1. Acquire run lock
2. `db verify`
3. `db backup` (or configured backup step)
4. `recovery-scan`
5. Execute loops within SafetyGate level
6. Surface review queue (from 0.4-c; no auto approve)
7. Refresh summary

OS scheduler (cron / systemd / Task Scheduler) invokes:

```bash
loop-pilot run daily --unattended --safe
```

### 5.3 Daemon (out of scope for 0.5)

| Command | Status |
|---------|--------|
| `loop-pilot daemon start` | **future enhancement** — not 0.5 |
| `loop-pilot daemon run --once` | optional convenience wrapper; not required if scheduler calls `run daily` directly |

---

## 6. Implementation order (mandatory)

| Step | Content | Acceptance |
|------|---------|------------|
| **0** | Complete **0.4-c Review Layer** | `verify_0_4c_acceptance.py` 16/16 green |
| **1** | **SafetyGate v1** (`levels.py`, `policy.py`, `gate.py`, `audit.py`) | unit tests per level; `gate_result.json` on gate paths |
| **2** | `schedule install --yes` (through SafetyGate, explicit `--yes`, audit; uninstall dry-run/status; dry-run unchanged) | integration tests; mock OS on CI |
| **3** | `run daily --unattended --safe` (lock, db verify, backup, recovery-scan, safe loops, review queue, summary) | `verify_0_5b`; no daemon required |
| **4** | Crash / recovery / observability acceptance | `verify_0_5c`; unattended log schema |

---

## 7. Sub-milestones

| Sub-milestone | Scope | Verify script |
|---------------|-------|---------------|
| **0.5-a** | SafetyGate v1 + Schedule Install (`--yes`) | `verify_0_5a_acceptance.py` |
| **0.5-b** | Unattended Daily Safe Run | `verify_0_5b_acceptance.py` |
| **0.5-c** | Crash Recovery + Observability | `verify_0_5c_acceptance.py` |
| **0.5-d** | 5-day personal unattended trial | manual evidence log |

---

## 8. 0.5-prep (parallel work, allowed now)

The following may proceed **in parallel with 0.4-c** on a separate branch, but must **not** ship real unattended runs or default real schedule install:

| Prep item | Allowed | Not allowed yet |
|-----------|---------|-----------------|
| SafetyGate type stubs / schema alignment | ✅ | wiring into live run path |
| Schedule install dry implementation skeleton | ✅ | `--yes` default or live OS write |
| `schedule status` / audit log schema | ✅ | — |
| Unattended run log schema | ✅ | real `--unattended` execution |

---

## 9. Priority stack

1. **Finish 0.4-c** (blocker)
2. **SafetyGate v1**
3. **`schedule install --yes`**
4. **`run daily --unattended --safe`**

---

## 10. Testing and acceptance

```bash
python scripts/verify_0_4c_acceptance.py   # must pass before 0.5 Step 1
python scripts/verify_0_4b_acceptance.py
python scripts/verify_0_4d_acceptance.py
python scripts/verify_0_5a_acceptance.py   # add when implementing
python scripts/verify_0_5b_acceptance.py
python scripts/verify_0_5c_acceptance.py
python -m pytest -q
```

Manual: on Windows, compare `schedule install --dry-run` vs `--yes`; confirm installed task invokes `run daily --unattended --safe`.

---

## 11. Non-goals (0.5)

- Long-running daemon (`daemon start`)
- Team / cloud / Dashboard (1.3+)
- Auto approve / PR / deploy
- PyPI release (Personal Beta optional, see 34 §7)
- Level 4 production hardening (blocked in default safe mode)

---

## 12. References

- [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md)
- [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md)
- [50-0.4-stabilization-and-truthful-acceptance.md](50-0.4-stabilization-and-truthful-acceptance.md)
- `src/loop_pilot/scheduler/installer.py`, `cli_schedule.py`, `runtime/daily_run.py`

---

## 中文摘要

**0.5 Safe Autonomy** 目标：在 0.4 个人日用闭环上，实现 OS 调度 + 分级无人值守，默认 fail-closed。

**硬前置**：0.4-c Review Layer 未完成（0/16 NOT READY）前，不得启动 0.5 Step 1。

**实施顺序**：

0. 完成 0.4-c（review list/show、approve/reject/defer/cancel/resume、review_required.md、gate_result.json、review_items、task_events，禁止 auto approve）  
1. SafetyGate v1（`src/loop_pilot/safety/`，Levels 0–4，默认 safe 允许 0–3、阻断 4）  
2. `schedule install --yes`（经 SafetyGate、显式 `--yes`、审计）  
3. `run daily --unattended --safe`（锁、db verify、backup、recovery-scan、安全 loop、审阅队列、summary）  
4. 崩溃恢复与可观测性验收  

**非 daemon 优先**：cron/systemd/Task Scheduler 直接调用 `loop-pilot run daily --unattended --safe`；`daemon start` 为后续增强，非 0.5 要求。

**子里程碑**：0.5-a SafetyGate+安装 → 0.5-b 无人值守 daily → 0.5-c 恢复可观测 → 0.5-d 5 天个人试用。

**可并行 prep**（不等 0.4-c）：SafetyGate 类型、schedule install 骨架、status/audit schema、unattended log schema；但不做真实 unattended run 或默认真实安装。
