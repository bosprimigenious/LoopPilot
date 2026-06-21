# 规划日志：个人优先路线图 Pivot

**日期**：2026-06-21  
**决策类型**：战略调整 — 从工具型开源/团队转向个人 AI 工作循环系统  
**状态**：已采纳（文档 only）

---

## 背景

LoopPilot 早期路线图（2026-06-20）将 0.5 定义为 **Public Beta / 急 PyPI**，0.8 为 **team-cloud-preview**，0.x 隐含「对外可安装 + 团队协作 preview」双轨压力。

实际使用场景明确为：**单人**每天三条 Loop + 任务管理，团队/云/公开 onboarding 会分散 0.4 日用链交付。

## 决策

### 1. 核心口径

**LoopPilot = 个人开发助手 + 论文推进器 + 信息筛选器 + 每日任务 OS**

- 0.x 主线：**一个人每天真的能用**
- Team / Cloud / Public onboarding **后移至 1.1+**
- 0.5 不再急 public beta

### 2. 新版本链

| 版本 | 新名称 | 要点 |
|------|--------|------|
| 0.4 | Personal Recovery & Daily Loop | inbox/queue/today/review/summary；四子阶段 a–d |
| 0.5 | Personal Beta | init personal；PyPI **可选** |
| 0.6 | Personal Memory & Evaluation | 原 0.7 eval 个人化 |
| 0.7 | Personal Extensions | 原 0.6 plugin 缩小为本地 |
| 0.8 | Optional Public Beta | 原 0.5 public 降级为可选 |
| 1.0 | Personal Stable | 单人 semver 承诺 |
| **1.1+** | Team / Cloud Preview | 原 0.8 team **移出 0.x** |

### 3. 0.4 四子阶段（锁定）

- **0.4-a** 状态可靠：db status/migrate/backup/verify, recovery scan
- **0.4-b** 个人任务入口：inbox, queue, today
- **0.4-c** 个人审阅：review list, approve/reject/defer/cancel
- **0.4-d** 每日总结：summary today/week, schedule print/dry-run

### 4. 0.4 不做

团队、Web Dashboard、云同步、插件市场、PyPI onboarding。

### 5. 0.3 状态保留

- 包版本 `0.3.0a1`；分支 `adapter-mvp-0.3`
- 2026-06-21 自动化验收 PASS（109 tests）；手动层文档化
- **不**因 pivot 回退 0.3 已完成项

### 6. Supersede 说明

| 旧文档 | 处理 |
|--------|------|
| [2026-06-20-0.5-public-beta-spec.md](2026-06-20-0.5-public-beta-spec.md) | 保留；顶部 cross-ref：0.5 现为 Personal Beta |
| [33-version-roadmap.md §0.8](../33-version-roadmap.md) | 团队规格标记为 **1.1+ 候选** |
| [34-version-roadmap-0x.md §6 旧 Public Beta](../34-version-roadmap-0x.md) | 已重写为 Personal Beta + 0.8 Optional Public |

## 产出文档

| 文件 | 动作 |
|------|------|
| `34-version-roadmap-0x.md` | 大幅重写 |
| `40-personal-daily-loop-0.4-spec.md` | 新建 |
| `41-next-steps-after-0.3.md` | 新建 |
| `31-v1-v2-v3-implementation-roadmap.md` | Legacy 映射更新 |
| `docs/development/README.md` | 索引更新 |
| `README.md` | 路线图表 |
| `docs/zh/03-版本路线图.md` | 中文同步 |
| `39-next-steps-0.3.md` | cross-ref |
| `36-adapter-mvp-0.3-acceptance.md` | cross-ref |
| 本文 | 新建 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 0.4 范围膨胀 | `40-personal-daily-loop-0.4-spec.md` 锁定不做项 |
| 双路线图冲突（33 vs 34） | 34 为个人优先权威；33 保留历史详细规格 + 顶注 |
| 过早 PyPI | 降为 0.5 可选 / 0.8 |

## 下一步

1. 收尾 0.3 手动验收记录
2. 启动 **0.4-a** SQLite + db CLI
3. 个人日用日志（连续 5 天）作为 0.4 完成证据
