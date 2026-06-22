# 2026-06-21 — Codex P1/P2 merge 修复日志

> Branch: `feat/0.5-safe-autonomy`  
> Context: Codex re-review on PR #7 — **P1 merge blocker** + two P2 quality fixes  
> Prior agent [Fix P1 SafetyGate locks defer](35a81e6c-e627-434e-bf39-113a1ed00a5f): **未完成**；本步全量交付

## Codex 发现

| 优先级 | 问题 | 影响 |
|--------|------|------|
| **P1** | `SafetyGate._check_adapter_invoke` 在 `safety.stage=ready` 时未校验 `policy.max_level` | `max_level=2` 时 `adapter.invoke level=4` 可能被 allow — **SafetyGate 绕过** |
| P2 | `FileLockStore._lock_is_stale` 对未知 payload 返回 `True` | 非 `pid:holder` 格式 lock 被误删，并发互斥失效 |
| P2 | `SummaryCollector._needs_review` 未读 `ReviewStore.deferred_until` | 已 defer 的 run 仍出现在日/周汇总 `needs_review` |

## 已修复（行为前后）

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `src/loop_pilot/safety/gate.py` | ready 阶段 level≥3 即 allow | 统一门禁：`LEVEL_4_BLOCKED`、`LEVEL_EXCEEDS_MAX`；prep 仍 block level≥3 |
| `src/loop_pilot/runtime/locks.py` | 未知 payload → stale → unlink | fail-closed：未知/legacy payload → **not stale** |
| `src/loop_pilot/summary/collector.py` | 仅看 run phase/outcome/gate | 绑定 `ReviewStore`；未来 `deferred_until` 从 `needs_review` 排除 |
| `src/loop_pilot/summary/service.py` | 无 ReviewStore | 注入 `ReviewStore(cfg.sqlite_path)` |

## 新增测试

- `test_safety_gate.py`: `test_adapter_invoke_denied_when_level_exceeds_max_level`, `test_adapter_invoke_level_4_denied_even_when_stage_ready`, `test_adapter_invoke_cannot_bypass_policy_allows_level`
- `test_file_locks.py`: `test_unknown_legacy_lock_payload_is_not_treated_as_stale`, `test_dead_pid_lock_is_stale`, `test_live_pid_lock_is_not_stale`
- `test_summary_collector.py`: `test_deferred_review_item_hidden_from_summary_until_due`, `test_deferred_review_item_reappears_after_due`, `test_summary_needs_review_matches_review_list_for_deferred`

## 自检审计（剩余 bypass 风险）

| 风险 | 结论 |
|------|------|
| `adapter.invoke` 绕过 `max_level` | **已清除（P1）** |
| `safety.stage=ready` 手改 YAML 无 readiness 探针 | **已知缺口** |
| ToolBroker 不经 SafetyGate 直调 adapter | **0.5-b 待审计** |
| 未知 lock 被误删 | **已清除（P2 locks）** |
| defer 后 summary 仍催审 | **已清除（P2 summary）** |

## 验收结果（2026-06-22）

```text
ruff check .                              → All checks passed
python -m pytest -q                       → 241 passed
python scripts/verify_0_4c_acceptance.py  → 32/32 READY
python scripts/verify_0_4_acceptance.py   → 11/11 READY
python scripts/verify_0_5_prep.py         → 3/3 PASS, 0.5-ready: NOT READY
```

## merge 后下一步

1. PR #7 Codex re-review → merge
2. readiness 自动化（禁止手改 `safety.stage=ready`）
3. 0.5-b/c/d

## Commits

- `5ba9781` — fix(safety): enforce max_level on adapter.invoke (Codex P1)
- `9d8812e` — fix(locks): fail-closed unknown lock payloads
- `b3a1840` — fix(summary): honor deferred_until in needs_review
- *(docs)* — docs: codex P1/P2 merge fix log
