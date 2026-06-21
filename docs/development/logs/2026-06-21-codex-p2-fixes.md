# 2026-06-21 — Codex P2 修复日志

> Branch: `feat/0.5-safe-autonomy`  
> Context: PR #7 Codex review @ 3a63106  
> Related: [2026-06-21-patch-review-gate-fix.md](2026-06-21-patch-review-gate-fix.md) (PR #8 P0/P1, prerequisite for truthful 0.4)

## Codex 发现

| 优先级 | 问题 | 影响 |
|--------|------|------|
| P2-1 | `scripts/verify_0_4_acceptance.py` 顶层 `from loop_pilot...` 无 `src` bootstrap | 源码 checkout 未 `pip install -e .` 时 `ModuleNotFoundError` |
| P2-2 | `LoopPilotConfig.snapshot_hash()` 未含 `schedule` / `safety` | 审计哈希无法区分 prep vs ready、`allow_install` true vs false |

## 已修复（文件）

| 文件 | 变更 |
|------|------|
| `scripts/verify_0_4_acceptance.py` | `src` bootstrap 于 `loop_pilot` 导入前 |
| `scripts/verify_0_3_acceptance.py` | 同上（自检补充，被 0.4-d 链式调用） |
| `scripts/verify_0_4d_acceptance.py` | 同上 |
| `src/loop_pilot/config.py` | `snapshot_hash()` 含 `schedule`、`safety`；`load_config` 加载两节 |
| `tests/unit/test_0_5_prep_safety.py` | `test_snapshot_hash_includes_safety_stage` / `test_snapshot_hash_includes_schedule_allow_install` |
| `tests/unit/test_verify_0_4_anti_cheat.py` | `test_verify_0_4_imports_without_package_install`（无 PYTHONPATH subprocess `--help`） |

## 自检审计（绕过风险）

| 风险 | 结论 | 处理 |
|------|------|------|
| `schedule.allow_install=true` + prep 阶段真装 | **已阻断** | `installer.py` + `SafetyGate` 双检 `is_prep_stage`；`test_windows_schedule_install_blocked_in_prep` 断言 `subprocess.run` 未调用 |
| `safety.stage=ready` 无验收即放行 | **已知缺口（未修）** | 当前 `ready` 为配置开关，无自动 readiness 探针；`0.5-ready` 仍 NOT READY，需后续 readiness 自动化 |
| 验收脚本 skip/xfail/弱化断言 | **未发现** | 全量 pytest 无 skip/xfail；patch gate 7 项行为测试在 `verify_0_4c` 内强制执行 |
| 仅检查文件存在的行为测试 | **部分存在（可接受）** | 0.4-b/c/d readiness 含静态 `exists` 步，但链末有 CLI/pytest 行为步；聚合门跑完整 pytest |
| 文档谎称「0.5 READY」 | **未发现** | 统一口径「0.5-prep only」；`verify_0_5_prep.py` 打印 `0.5-ready: NOT READY` |
| `verify_*` 缺 bootstrap | **已修** | `verify_0_4_acceptance`、`verify_0_3`、`verify_0_4d`、`verify_0_5_prep` |
| prep 可达 `schtasks` | **已阻断** | prep 阶段 `install_schedule` 抛 `BLOCKED`；Windows schtasks 仅在 `stage=ready` 路径 |
| Patch review gate 回归 | **无回归** | `test_review_service_patch_gate.py` 7 passed；`verify_0_4c` 含 6 项行为子步 |

## 验收结果（2026-06-22，源码树无 pip install）

```text
ruff check .                              → All checks passed
python -m pytest -q                       → 235 passed
python scripts/verify_0_4b_acceptance.py  → 27/27 READY
python scripts/verify_0_4c_acceptance.py  → 32/32 READY
python scripts/verify_0_4d_acceptance.py  → 32/32 READY
python scripts/verify_0_4_acceptance.py   → 11/11 READY (PYTHONPATH 清空)
python scripts/verify_0_5_prep.py         → 3/3 PASS, 0.5-ready: NOT READY
```

## 已知剩余限制（诚实）

1. **`safety.stage=ready` 无程序化 readiness gate** — 操作者手动改 YAML 即可绕过「验收后才 ready」的意图；0.5-ready 里程碑需实现自动探针（0.4 aggregate + 0.4c + doctor 等）。
2. **0.5-b/c/d 未实现** — `verify_0_5a/b/c_acceptance.py` 不存在；无人值守 daily、崩溃恢复、5 天 dogfood 均未交付。
3. **cron/systemd 仅 marker** — `install_status=previewed`，非真装；Windows schtasks 仅在 `stage=ready` 时执行。
4. **Truthful 0.4 聚合在本分支已绿**，但 PR #7 仍待 Codex re-review 后合并；`stabilize/0.4-truthful-acceptance` 分支可能领先/分叉，合并前需对齐。

## Commits

- `aab00ac` — fix: bootstrap verify_0_4_acceptance; safety/schedule in config snapshot_hash + tests
- *(this step)* — fix: bootstrap verify_0_3/0_4d; docs completion
