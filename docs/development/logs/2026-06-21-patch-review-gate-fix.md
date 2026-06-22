# 2026-06-21 — Patch Review Gate P1 修复日志

> Branch: `feat/0.5-safe-autonomy`  
> Context: Codex PR #8 — truthful patch review acceptance (ported from `stabilize/0.4-truthful-acceptance`)

## Codex 发现（修复前）

| 优先级 | 问题 | 修复前行为 |
|--------|------|------------|
| P0-1 | `patch.diff` + `SUCCEEDED` 被当作已完成 | 直接进入 Completed；`gate_result.json=pass` |
| P0-2 | `approve` 对 patch run 设置 `resume_requested` | 审批后需 resume 才能终态，易死锁 |
| P1-1 | `artifact-manifest.json` 自引用 checksum | manifest 重写后 self-checksum 过期 |
| P1-2 | `report_path()` 先读 manifest | `diff-summary.md` 可能盖过 `development-report.md` |

## 状态模型（修复后）

### Patch 产出 run — 审批前

| 字段 | 值 | 说明 |
|------|-----|------|
| `phase` | `TERMINATED`（InternLoop 终态）或 `WAITING_APPROVAL`（`maybe_enqueue` 安全层补正） | 均表示「未获人工批准」 |
| `outcome` | `PARTIAL` | 非最终成功 |
| `review_status` | `needs_review` | 待审 |
| `gate_result.json` | `needs_review` | 机器门禁 |

### Patch 产出 run — 审批后

| 字段 | 值 | 说明 |
|------|-----|------|
| `phase` | `TERMINATED` | 已终态 |
| `outcome` | `SUCCEEDED` | 人工批准后视为成功 |
| `review_status` | `approved` | **不是** `resume_requested` |
| `gate_result.json` | `pass` | 机器门禁通过 |

### 禁止行为

- **`approve` 不得** 对 patch run 设置 `resume_requested` 或写 resume checkpoint
- **`resume`** 拒绝 `rejected` / `cancelled` / 已 `approved`+`SUCCEEDED` 终态的 run
- **Weekly summary** 不得将 `needs_review` / `PARTIAL` run 列入 Completed

## 修改文件

| 文件 | 变更 |
|------|------|
| `src/loop_pilot/runtime/terminal_artifacts.py` | patch-aware finalize → `needs_review`；manifest 排除自身 |
| `src/loop_pilot/loops/intern/loop.py` | `_finalize()`：有 `patch.diff` 且未决 → `PARTIAL`/`needs_review` 后再写 artifacts |
| `src/loop_pilot/review/service.py` | `mark_patch_run_waiting_review()`；`maybe_enqueue` 安全层；`approve()` 直接终态 |
| `src/loop_pilot/summary/collector.py` | `report_path()` 规范报告路径优先于 manifest fallback |

## 回归测试（7 项）

1. patch needs_review gate before approval — `test_patch_run_enters_review_gate_before_success`
2. summary shows needs_review not completed — 同上 weekly assert
3. approve direct finalize — `test_approve_patch_run_finalizes_without_resume_deadlock`
4. no resume_requested after approve — 同上
5. rejected cannot resume — `test_rejected_patch_run_cannot_resume`
6. manifest no self checksum — `test_manifest_does_not_include_stale_self_checksum`
7. report_path prefers final report — `test_report_path_prefers_actual_report_over_markdown_logs`

## Before / After

| 场景 | Before | After |
|------|--------|-------|
| Intern 产出 patch | `SUCCEEDED` / Completed | `PARTIAL` / needs_review |
| `approve patch-run` | `resume_requested` | `approved` + `TERMINATED` + `SUCCEEDED` |
| manifest 重写 | 含自身 stale sha256 | 不含 `artifact-manifest.json` |
| summary report 链接 | 可能指向 diff-summary | 优先 development-report |

## 验收

```bash
ruff check .
python -m pytest -q
python scripts/verify_0_4b_acceptance.py
python scripts/verify_0_4c_acceptance.py
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
```
