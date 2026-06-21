# Cursor Prompt: 0.5 Safe Autonomy (Schedule Install + Daemon + SafetyGate)

## 目标（中文）

在 **0.4-d 已绿** 基础上实现 0.5 Safe Autonomy **Step 2+**（Step 1 仅为规格与本 prompt）：

1. `SafetyGate` levels 0–4 + `gate_result.json` 写入
2. `run daily --safe --level N`（Level 0 与现有 `--dry-run` 行为一致）
3. `schedule install --yes` / `uninstall` / `status`（Windows Task Scheduler 优先）
4. `daemon run --once` 供调度器调用
5. `scripts/verify_0_5_acceptance.py` + pytest

## Task (English)

Read [50-personal-daily-loop-0.5-spec.md](../docs/development/50-personal-daily-loop-0.5-spec.md) and implement incrementally.

### Constraints (mandatory)

| Rule | Detail |
|------|--------|
| Fail closed | No `--yes` install without explicit flag; no real adapters without config + CLI |
| No auto merge | Never auto approve / commit / push |
| Backward compat | `run daily --dry-run` and `schedule install --dry-run` unchanged |
| SQLite | Unattended paths require `state_backend=sqlite` |
| Tests | Every gate level gets at least one unit test; installer mocked on non-Windows CI |

### Starting points in repo

- `src/loop_pilot/scheduler/installer.py` — replace `NotImplementedError` in `install_schedule`
- `src/loop_pilot/cli_schedule.py` — wire uninstall/status
- `src/loop_pilot/runtime/daily_run.py` — extend beyond `dry_run=True` only
- `schemas/gate_result.schema.json` — output contract

### Verification

```bash
python scripts/verify_0_4b_acceptance.py
python scripts/verify_0_4d_acceptance.py
python scripts/verify_0_5_acceptance.py   # add when implementing
python -m pytest -q
```

### Out of scope for first implementation PR

- Level 4 production hardening
- Full 0.4-c review agent
- PyPI / `init personal` (separate Personal Beta track)
