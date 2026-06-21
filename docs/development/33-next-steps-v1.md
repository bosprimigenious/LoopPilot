# 33 V1 后续开发规划（Legacy → 0.x 映射）

> **权威版本路线**见 [33-version-roadmap.md](33-version-roadmap.md) 与 [34-version-roadmap-0x.md](34-version-roadmap-0x.md)。  
> 本文保留「V1」称呼，便于对照历史任务；**新工作必须使用 0.2 / 0.3 / 0.4 / 0.5 编号**。

## 0.1 Mini-MVP 状态（2026-06-21）

**已完成并可验收。** 详见 [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) 与 [logs/2026-06-20-mini-mvp-delivery.md](logs/2026-06-20-mini-mvp-delivery.md)。

Mini 不交付：真实 API/CLI、SQLite 真续跑、`resume`/`approve`/`reject`/`cancel` 对外 CLI。

## V1 能力 → 0.x 阶段

| 原「V1」能力 | 目标版本 | 分支/worktree 建议 |
|---|---|---|
| 真实 Intern/Paper workspace、路径 allowlist | **0.2** Practical MVP | `feat/0.2-practical-mvp` |
| `CodingCLIAdapter` / `APIModelAdapter` / ModelRouter 生产化 | **0.3** Real Adapter MVP | `feat/0.3-adapter-mvp` |
| SQLite、`resume`/`approve`/`reject`/`cancel`/`report` CLI | **0.4** Daily Runner | `wip/0.4-recovery`（已有 worktree） |
| OS 调度、`run all` 真实每日链 | **0.4** | 同上 |
| PyPI、开源 README、release CI | **0.5** Public Beta | 文档已规划 |
| 插件生态、多租户 | **0.6+** | 见 34 §0.6 |

## 推荐实施顺序

```
0.1 Mini-MVP ✅
    ↓
0.2 Practical MVP — workspace 配置、dry-run 报告、Inbox 结构
    ↓
0.3 Real Adapter MVP — CLI/API Adapter + ToolBroker（需 allow_real_adapters=true）
    ↓
0.4 Daily Automation — SQLite recovery、审批 CLI、scheduler
    ↓
0.5 Public Beta — PyPI 与社区文档
```

**原则**：上一阶段验收通过前，不将下一阶段能力合并进默认运行链。

## 0.2 首要任务（V1 第一站）

1. `config/loop-pilot.yaml`：`intern.workspace`、`paper.workspace`、`allowed_paths` / `forbidden_paths`
2. Intern/Paper workspace 模块与边界测试（仍 MockAdapter）
3. DailyNews Inbox 双通道结构与候选过期策略（fixture 驱动）
4. Markdown 人工审阅流（文件级，非 approve/reject CLI）

详细 checklist 见 [33-next-steps-0.2.md](33-next-steps-0.2.md)。

## 0.3 首要任务（原 V1 Adapter 部分）

1. `CodingCLIAdapter` 最小路径（批准 worktree + 测试链）
2. `APIModelAdapter` 与 `models.yaml` 真实 endpoint 配置
3. `adapters/factory.py` + `registry.py` 与 PolicyEngine 联动
4. DailyNews `--real-sources` 与有限在线源

见 [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)。

## 0.4 首要任务（原 V1 每日自动化）

1. `state_backend: sqlite` 默认路径与迁移脚本
2. 暴露 `resume` / `approve` / `reject` / `cancel` / `report` CLI（已在 `wip/0.4-recovery` 原型）
3. `test_v1_recovery.py` 全绿（中断后续跑、审批门控）
4. `install_scheduler.py` 与 `run_regression.py` 生产化

WIP 模块：`src/loop_pilot/storage/sqlite.py`、`runtime/recovery.py`、`runtime/approvals.py`、`runtime/checkpoints.py`。

## 0.5 及以后

- PyPI `loop-pilot` 发布、`CONTRIBUTING.md`、`SECURITY.md`
- Golden 回归与 fault-injection 矩阵扩展
- 1.0 长期个人生产稳定性

## 与 Mini 的代码分岔

| 位置 | Mini (`feat/mini-mvp-0.1`) | V1 恢复 (`wip/0.4-recovery`) |
|---|---|---|
| CLI | `doctor`/`run`/`status`/`inspect` | 含 `resume`/`approve`/`reject`/`cancel`/`report` |
| 默认 `state_backend` | `json` | 可切 `sqlite` 开发 |
| `test_v1_recovery` | skip | 应全绿 |

## 相关文档

- [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md)（Legacy 任务分解）
- [33-next-steps-0.2.md](33-next-steps-0.2.md)（0.2 行动项）
- [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md)（0.1 验收）
