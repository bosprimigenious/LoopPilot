# 2026-06-21 — Codex P2 修复日志

> Branch: `feat/0.5-safe-autonomy`  
> Context: PR #7 Codex review @ 3a63106

## Codex 发现

| 优先级 | 问题 | 影响 |
|--------|------|------|
| P2-1 | `scripts/verify_0_4_acceptance.py` 顶层 `from loop_pilot...` 无 `src` bootstrap | 源码 checkout 未 `pip install -e .` 时 `ModuleNotFoundError` |
| P2-2 | `LoopPilotConfig.snapshot_hash()` 未含 `schedule` / `safety` | 审计哈希无法区分 prep vs ready、`allow_install` true vs false |

## 已修复

1. **`scripts/verify_0_4_acceptance.py`** — 与 `verify_0_5_prep.py` 一致：在 `loop_pilot` 导入前将 `src` 插入 `sys.path`
2. **`src/loop_pilot/config.py`** — `snapshot_hash()` payload 增加 `schedule`、`safety`（`json.dumps(..., sort_keys=True)` 稳定序列化）
3. **测试** — `test_0_5_prep_safety.py` 断言 safety/schedule 变更会改变 hash；`test_verify_0_4_anti_cheat.py` subprocess 验证未安装包时可 `--help`

## 验收

```bash
ruff check .
python -m pytest -q
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
```
