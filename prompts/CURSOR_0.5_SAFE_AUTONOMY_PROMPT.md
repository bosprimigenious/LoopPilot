# Cursor Prompt: 0.5 Safe Autonomy (SafetyGate → Schedule Install → Unattended Daily)

## 目标（中文）

在 **0.4-c Review Layer 验收通过** 后实现 0.5 Safe Autonomy。0.4-c 未完成（当前 0/16 NOT READY）时 **不得开始 Step 1**。

**实施顺序**（不可跳步）：

0. 完成 0.4-c（review list/show、approve/reject/defer/cancel/resume、review_required.md、gate_result.json、review_items、task_events — 禁止 auto approve）
1. **SafetyGate v1**（`src/loop_pilot/safety/`：`levels.py`, `policy.py`, `gate.py`, `audit.py`）
2. `schedule install --yes`（经 SafetyGate、显式 `--yes`、审计；uninstall dry-run/status；dry-run 不变）
3. `run daily --unattended --safe`（锁、db verify、backup、recovery-scan、安全 loop、审阅队列、summary）
4. 崩溃恢复与可观测性验收

**非 daemon 优先**：OS 调度器（cron/systemd/Task Scheduler）直接调用 `loop-pilot run daily --unattended --safe`。`daemon start` 为后续增强，**非 0.5 要求**。

**0.5-prep 可并行**（不等 0.4-c）：SafetyGate 类型、schedule install 骨架、status/audit schema、unattended log schema — 但不做真实 unattended run 或默认真实安装。

## Task (English)

Read [50-personal-daily-loop-0.5-spec.md](../docs/development/50-personal-daily-loop-0.5-spec.md) and implement incrementally **only after 0.4-c is green**.

### Prerequisites (mandatory)

| Milestone | Required before |
|-----------|-----------------|
| 0.4-c Review Layer (`verify_0_4c_acceptance.py` 16/16) | Any 0.5 Step 1+ work |
| 0.4-b, 0.4-d regression green | Every 0.5 PR |

### Constraints (mandatory)

| Rule | Detail |
|------|--------|
| Fail closed | No `--yes` install without explicit flag; no real adapters without config + CLI |
| No auto merge | Never auto approve / commit / push |
| Backward compat | `run daily --dry-run` and `schedule install --dry-run` unchanged |
| SQLite | Unattended paths require `state_backend=sqlite` |
| Default safe mode | Allows SafetyGate Levels 0–3; blocks Level 4 |
| No daemon required | Scheduler calls `run daily --unattended --safe` directly |
| Tests | Every gate level gets at least one unit test; installer mocked on non-Windows CI |

### Implementation order

| Step | Deliverable | Verify |
|------|-------------|--------|
| 0 | 0.4-c Review Layer complete | `verify_0_4c_acceptance.py` |
| 1 | SafetyGate v1 in `src/loop_pilot/safety/` | unit tests + `gate_result.json` |
| 2 | `schedule install --yes` / uninstall / status | `verify_0_5a_acceptance.py` |
| 3 | `run daily --unattended --safe` | `verify_0_5b_acceptance.py` |
| 4 | Crash recovery + observability | `verify_0_5c_acceptance.py` |

### Sub-milestones

- **0.5-a**: SafetyGate + Schedule Install
- **0.5-b**: Unattended Daily Safe Run
- **0.5-c**: Crash Recovery + Observability
- **0.5-d**: 5-day personal unattended trial (manual evidence)

### Starting points in repo

- `src/loop_pilot/scheduler/installer.py` — replace `NotImplementedError` in `install_schedule` (Step 2 only)
- `src/loop_pilot/cli_schedule.py` — wire uninstall/status
- `src/loop_pilot/runtime/daily_run.py` — extend beyond `dry_run=True` only (Step 3)
- `schemas/gate_result.schema.json` — output contract
- New: `src/loop_pilot/safety/` — levels, policy, gate, audit (Step 1)

### Verification

```bash
python scripts/verify_0_4c_acceptance.py   # must pass before Step 1
python scripts/verify_0_4b_acceptance.py
python scripts/verify_0_4d_acceptance.py
python scripts/verify_0_5a_acceptance.py   # add when implementing
python scripts/verify_0_5b_acceptance.py
python scripts/verify_0_5c_acceptance.py
python -m pytest -q
```

### Out of scope

- `daemon start` / long-running daemon (future enhancement)
- Level 4 production hardening (blocked in default safe mode)
- PyPI / `init personal` (separate Personal Beta track)
- Auto approve / commit / push (any level)

### 0.5-prep only (parallel with 0.4-c, separate branch)

Allowed now without 0.4-c:

- SafetyGate type stubs and schema alignment
- Schedule install skeleton (no live `--yes` default)
- `schedule status` / audit log schema
- Unattended run log schema

Not allowed in prep:

- Real `--unattended` execution path
- Default real schedule install

### References

- [52-0.5-revised-plan-rationale.md](../docs/development/52-0.5-revised-plan-rationale.md)
- [53-0.5-acceptance.md](../docs/development/53-0.5-acceptance.md)
- [CURSOR_0.4C_REVIEW_LAYER_PROMPT.md](CURSOR_0.4C_REVIEW_LAYER_PROMPT.md) — Priority 1 blocker
- Chinese: [docs/zh/15-0.5-安全自治.md](../docs/zh/15-0.5-安全自治.md)
