# 32 Mini-MVP 验收文档

## Phase 目标

| 项 | 值 |
|---|---|
| 里程碑 | **Mini-MVP Phase A** → tag `0.1.0-mini` |
| 验收日期 | 2026-06-21 |
| 范围 | 架构脚手架：MockAdapter、三条离线 Loop、fixtures、trace/report/artifacts、CI |

> **不属于本里程碑（V1 / Practical MVP）**：SQLite `resume`/`approve`/`reject`/`cancel` CLI、真实 Cursor CLI/API、真实工作区与在线源。仓库中相关代码（`sqlite.py`、`approvals.py`、`recovery.py`）保留供后续 V1，但 Mini CLI 不暴露这些命令。

## Phase A 清单

| # | 项 | 状态 |
|---|---|---|
| 1 | `pip install -e ".[dev]"` 本地安装 | ✅ |
| 2 | `loop-pilot doctor` 成功 | ✅ |
| 3 | `pytest -q` + `ruff check .` | ✅ (85 passed) |
| 4 | 三条 Loop 各自 dry-run 成功 | ✅ |
| 5 | `loop-pilot run all --fixture-set mini --dry-run` | ✅ |
| 6 | `status` / `inspect` 可用 | ✅ |
| 7 | PaperLoop `unsupported_claim` → `partial`（SOURCE REQUIRED） | ✅ |
| 8 | DailyNews 输出 `paper-candidates.md` + `candidate-actions.json` | ✅ |
| 9 | `runtime.allow_real_adapters=false` 守卫 | ✅ |
| 10 | `.github/workflows/ci.yml` | ✅ |
| 11 | 命名统一 LoopPilot / loop-pilot（无 LoopPolit 残留） | ✅ |

## 自验收命令与结果（2026-06-21）

### 1. 安装

```text
pip install -e ".[dev]"  →  PASS
```

### 2. Doctor

```text
Doctor: OK
  Config loaded
  Fixtures present
  State directories ready
  MockAdapter default (allow_real_adapters=false)
→ PASS
```

### 3. Pytest + Ruff

```text
ruff check .  →  All checks passed
85 passed in ~21s
→ PASS
```

### 4–7. 单 Loop 与 run all

| 命令 | 结果 | 预期 |
|---|---|---|
| `run intern --fixture simple_python_bug --dry-run` | `succeeded` | ✅ |
| `run paper --fixture unsupported_claim --dry-run` | `partial`（Claim requires additional source） | ✅ |
| `run daily-news --fixture github_star_snapshots --dry-run` | `succeeded` | ✅ |
| `run all --fixture-set mini --dry-run` | daily_news/intern `succeeded`, paper `partial` | ✅ |

### 8. Status

```text
status  →  列出最近 run（loop_type / phase / outcome）
→ PASS
```

## 关键行为验证

### PaperLoop SOURCE_REQUIRED

- `_run_checks` 将 `[SOURCE REQUIRED]` 视为未完全通过
- `unsupported_claim` fixture outcome 为 `partial`，非 `succeeded`
- `paper-development-report.md` 含 `## Source Required` / `yes`

### DailyNews 候选路由

产物（除 `intern-candidates.md` 外）：

- `paper-candidates.md`
- `candidate-actions.json`（`target_loop`, `priority`, `source_item_id`, `reason`, `recommended_action`）

### allow_real_adapters

- 默认 `false`（`config/loop-pilot.yaml`）
- `ModelRouter` 与 `adapters/registry.py` 阻止 cli/api 类真实 Adapter

## 完成度估计

| 阶段 | 完成度 | 说明 |
|---|---|---|
| **Mini-MVP (0.1.0-mini)** | **100%** | Phase A 清单全部通过；待打 tag `0.1.0-mini` |
| Practical MVP (0.2.0) | ~15% | 工作区 allowlist、CursorCLIAdapter、真实源未开始 |
| V1 stable | ~25% | SQLite/恢复/审批代码在库中，CLI 未暴露，非本阶段目标 |

## 与 Practical MVP 的差距

- 真实 git worktree 与用户工作区 allowlist
- `CodingCLIAdapter` 最小接入（需 `allow_real_adapters=true`）
- 真实 DailyNews 源与 Markdown 人工审阅流（非 approve/reject CLI）
- patch/diff 限制与无 push/commit/deploy 策略落地

## 与 V1 的明确边界

以下**不是** Mini-MVP Phase A 交付物：

- CLI：`resume`, `approve`, `reject`, `cancel`, `report`（代码保留，Mini help 不暴露）
- SQLite recovery 生产化与跨进程锁
- `APIModelAdapter` / 真实 API 配置
- OS 调度安装、PyPI 发布

## 相关文档

- [25-mini-run-path.md](25-mini-run-path.md)
- [README.md](../../README.md)
