# LoopPilot 开发文档索引

本目录是 LoopPilot 的**英文接口规格层**（Layer 2）。日常中文理解请从 [docs/zh/README.md](../zh/README.md) 开始；英文最小规格见 [docs/en-core.md](../en-core.md)。

`ideas.md` 仅保存原始思路。根目录 [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) 为计划入口。

## 三层文档架构

| 层 | 语言 | 目录 | 用途 |
|----|------|------|------|
| **Layer 1 认知层** | 中文 | [docs/zh/](../zh/)、[README.md](../../README.md) | 人读：理解系统、跑命令、看进度 |
| **Layer 2 执行层** | 英文 | 本目录、`src/`、`config/` | AI/CI：契约、状态机、验收 |
| **Layer 3 提示词层** | 中+英 | [prompts/](../../prompts/) | 中文目标 + English constraints |

详见 [docs/zh/05-文档体系说明.md](../zh/05-文档体系说明.md)。

## 命名与版本基线

- 项目名：`LoopPilot`；GitHub：[bosprimigenious/LoopPilot](https://github.com/bosprimigenious/LoopPilot)
- PyPI / CLI：`loop-pilot`；Python 包：`loop_pilot` / `src/loop_pilot/`
- **阶段版本**：0.x 个人优先（0.1 → … → 0.9）→ **1.x**（1.0 稳定 → 1.1 智能 → 1.2 协作 → 1.3 团队 preview），路线图权威见 [34-version-roadmap-0x.md](34-version-roadmap-0x.md) + [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md)；semver 索引见 [33-version-roadmap.md](33-version-roadmap.md)
- **当前工程焦点**：
  - **0.1** 已完成
  - **0.2** 已验收 `v0.2.0a1`（2026-06-21）
  - **0.3** safety alpha `v0.3.0a1`（分支 `adapter-mvp-0.3`）— L1/L2 通过；Full DoD 待 MANUAL 层
  - **0.4-a** 已交付（2026-06-21，分支 `personal-daily-loop-0.4-a`）— SQLite + db/recovery CLI；tag `v0.4.0a1`
  - **0.4-b** 已验收（2026-06-21）— inbox/queue/today；verify 27/27
  - **0.4-c** **未实现** — Review Layer；全链 BLOCKED
  - **0.4-d** 已验收（2026-06-21）— summary/schedule/daily dry-run；verify 29/29
  - **0.4 全链** BLOCKED — [50-personal-daily-loop-0.4-full-acceptance.md](50-personal-daily-loop-0.4-full-acceptance.md)；[logs/2026-06-21-0.4-full-acceptance-run.md](logs/2026-06-21-0.4-full-acceptance-run.md)
  - **0.5+** 文档规划；Team/Cloud **仅在 1.3 preview**（1.2 为文件包协作）
- 1.x：**1.0** Personal Stable → **1.1** Intelligence → **1.2** Controlled Collaboration → **1.3** Team/Cloud Preview（见 [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md)）
- 0.1–0.3 CLI：`doctor`、`run`、`run all`、`status`、`inspect`；0.3 增 `adapters list/doctor`
- `resume`/`approve`/`reject`/`cancel` 从 **0.4** 开始

## 阅读顺序（英文规格）

### 快速理解（中文）

1. [docs/zh/00-快速开始.md](../zh/00-快速开始.md)
2. [docs/zh/01-系统是什么.md](../zh/01-系统是什么.md)
3. [docs/zh/02-三条循环.md](../zh/02-三条循环.md)

### 完整规格（本目录）

1. [00-system-definition.md](00-system-definition.md) — 目标、边界、成功定义
2. [01-architecture.md](01-architecture.md) — 总体架构、组件依赖
3. [02-runtime-mechanism.md](02-runtime-mechanism.md) — 状态机、预算、重试、锁
4. [03-intern-loop.md](03-intern-loop.md) — 实习开发闭环
5. [04-paper-loop.md](04-paper-loop.md) — 论文研究闭环
6. [05-daily-news-loop.md](05-daily-news-loop.md) — 高价值日报
7. [06-agents-skills-tools.md](06-agents-skills-tools.md) — Agent、Skill、Tool、Connector
8. [07-data-and-reports.md](07-data-and-reports.md) — 状态、产物、报告契约
9. [08-security-and-recovery.md](08-security-and-recovery.md) — 权限、审批、故障恢复
10. [09-versions.md](09-versions.md) — Mini/V1/V2/V3 范围（Legacy）
11. [10-testing-and-acceptance.md](10-testing-and-acceptance.md) — 测试与验收矩阵
12. [11-daily-operation.md](11-daily-operation.md) — 每日真实运行方式
13. [12-development-work-breakdown.md](12-development-work-breakdown.md) — 开发顺序与任务
14. [13-source-and-crawler-plan.md](13-source-and-crawler-plan.md) — 数据源与爬取策略
15. [14-implementation-manifest.md](14-implementation-manifest.md) — 模块/脚本/配置清单
16. [15-ideas-traceability.md](15-ideas-traceability.md) — Ideas 迁移追踪
17. [16-design-audit.md](16-design-audit.md) — 设计自检
18. [17-data-contracts.md](17-data-contracts.md) — 核心对象与 Schema
19. [18-state-transition-spec.md](18-state-transition-spec.md) — 状态转换规格
20. [19-adapter-specifications.md](19-adapter-specifications.md) — Adapter 协议
21. [20-skill-specifications.md](20-skill-specifications.md) — Skill 规格
22. [21-test-fixtures-and-golden-cases.md](21-test-fixtures-and-golden-cases.md) — Fixture 与 Golden
23. [22-error-and-budget-policy.md](22-error-and-budget-policy.md) — 错误与预算策略
24. [23-human-review-protocol.md](23-human-review-protocol.md) — 人工 Review 协议
25. [24-configuration-spec.md](24-configuration-spec.md) — 配置 Schema
26. [25-mini-run-path.md](25-mini-run-path.md) — Mini 运行路径
27. [28-agent-development-guide.md](28-agent-development-guide.md) — Agent 开发规范
28. [29-model-routing-and-runtime-policy.md](29-model-routing-and-runtime-policy.md) — 模型路由策略
29. [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md) — Adapter/Router 路线
30. [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) — Legacy 实施路线
31. [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) — **0.1 验收**
32. [33-version-roadmap.md](33-version-roadmap.md) — **semver 权威索引**
33. [33-next-steps-v1.md](33-next-steps-v1.md) — Legacy V1 规划
34. [33-next-steps-0.2.md](33-next-steps-0.2.md) — 0.2 行动项
35. [34-version-roadmap-0x.md](34-version-roadmap-0x.md) — **0.1→1.0 详细路线**
36. [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md) — **0.2 验收**
37. [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) — **0.3 验收**
38. [37-adapter-safety-policy.md](37-adapter-safety-policy.md) — Adapter 安全策略
39. [38-toolbroker-design.md](38-toolbroker-design.md) — ToolBroker 设计
40. [39-next-steps-0.3.md](39-next-steps-0.3.md) — 0.3 后续步骤
41. [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) — **0.4 个人日用链规格**
42. [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) — **0.3→0.4 行动顺序**
43. [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) — **0.4-a 验收**
44. [44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md) — **0.4-b 验收**
45. [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) — **0.4-c 验收（planned）**
46. [46-review-layer-design.md](46-review-layer-design.md) — **0.4-c Review Layer 架构**
47. [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) — **1.x 个人→协作权威规格**
45. [44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md) — **0.4-b 验收**
46. [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) — **0.4-c 验收**
47. [46-review-layer-design.md](46-review-layer-design.md) — **0.4-c 审阅层设计**
48. [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md) — **0.4-d 验收（planned）**
49. [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md) — **0.4-d Summary Engine 架构**
50. [47-output-interface-spec.md](47-output-interface-spec.md) — **输出接口：人 MD / 机器 JSON**

## 中文认知层对应关系

日常理解用中文（`docs/zh/`）；勾选验收与接口细节以本目录英文 spec 为准。维护规则：[docs/zh/10-中英文文档管理.md](../zh/10-中英文文档管理.md)。

| 中文 (`docs/zh/`) | 英文 (`docs/development/`) | 用途 |
|-------------------|----------------------------|------|
| [README.md](../zh/README.md) | [README.md](README.md) + [en-core.md](../en-core.md) | 文档入口 |
| [03-版本路线图.md](../zh/03-版本路线图.md) | [34-version-roadmap-0x.md](34-version-roadmap-0x.md) | 0.x 阶段边界 |
| [03-版本路线图.md](../zh/03-版本路线图.md) | [33-version-roadmap.md](33-version-roadmap.md) | semver 索引与历史详细规格 |
| [07-0.3-Adapter验收说明.md](../zh/07-0.3-Adapter验收说明.md) | [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) | 0.3 验收 |
| [07-0.3-Adapter验收说明.md](../zh/07-0.3-Adapter验收说明.md) | [logs/2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md) | 0.3 验收跑记录 |
| [08-0.4-个人日用闭环.md](../zh/08-0.4-个人日用闭环.md) | [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) | 0.4 规格 |
| [11-0.4a-SQLite与恢复扫描.md](../zh/11-0.4a-SQLite与恢复扫描.md) | [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) | 0.4-a 验收 |
| [11-0.4a-SQLite与恢复扫描.md](../zh/11-0.4a-SQLite与恢复扫描.md) | [logs/2026-06-21-0.4a-delivery.md](logs/2026-06-21-0.4a-delivery.md) | 0.4-a 交付记录 |
| [12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md) | [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) | 0.4-c 验收（planned） |
| [12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md) | [46-review-layer-design.md](46-review-layer-design.md) | 0.4-c 架构 |
| [12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md) | [logs/2026-06-21-0.4c-spec-and-prompt.md](logs/2026-06-21-0.4c-spec-and-prompt.md) | 0.4-c 规格决策 |
| [08-0.4-个人日用闭环.md](../zh/08-0.4-个人日用闭环.md) | [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) | 0.3→0.4 行动 |
| [09-1.x-个人到协作.md](../zh/09-1.x-个人到协作.md) | [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) | 1.x 路线 |
| [04-如何跑验收.md](../zh/04-如何跑验收.md) | [32](32-mini-mvp-acceptance.md) / [35](35-practical-mvp-0.2-acceptance.md) / [36](36-adapter-mvp-0.3-acceptance.md) | 验收命令 |
| [10-中英文文档管理.md](../zh/10-中英文文档管理.md) | [logs/2026-06-21-zh-en-doc-management.md](logs/2026-06-21-zh-en-doc-management.md) | 文档策略 |
| [05-文档体系说明.md](../zh/05-文档体系说明.md) | [logs/2026-06-21-doc-system-bilingual-upgrade.md](logs/2026-06-21-doc-system-bilingual-upgrade.md) | 三层架构决策 |
| [12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md) | [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) | 0.4-c 验收 |
| [12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md) | [46-review-layer-design.md](46-review-layer-design.md) | 审阅层设计 |
| [13-输出接口-人看MD机器看JSON.md](../zh/13-输出接口-人看MD机器看JSON.md) | [47-output-interface-spec.md](47-output-interface-spec.md) | 输出接口规格 |
| [14-0.4d-日汇总与调度预览.md](../zh/14-0.4d-日汇总与调度预览.md) | [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md) | 0.4-d 验收（planned） |
| [14-0.4d-日汇总与调度预览.md](../zh/14-0.4d-日汇总与调度预览.md) | [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md) | 0.4-d 架构 |
| [14-0.4d-日汇总与调度预览.md](../zh/14-0.4d-日汇总与调度预览.md) | [logs/2026-06-21-0.4d-spec-and-prompt.md](logs/2026-06-21-0.4d-spec-and-prompt.md) | 0.4-d 规格决策 |

### 决策日志（中文）

- [logs/2026-06-21-zh-en-doc-management.md](logs/2026-06-21-zh-en-doc-management.md) — 中英文文档管理策略
- [logs/2026-06-21-doc-system-bilingual-upgrade.md](logs/2026-06-21-doc-system-bilingual-upgrade.md) — 文档三层体系升级
- [logs/2026-06-21-personal-first-roadmap-pivot.md](logs/2026-06-21-personal-first-roadmap-pivot.md) — 0.x 个人优先 pivot
- [logs/2026-06-21-1x-roadmap-personal-stable.md](logs/2026-06-21-1x-roadmap-personal-stable.md) — 1.x 四段式决策
- [logs/2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md) — 0.3 验收跑记录
- [logs/2026-06-21-0.4a-delivery.md](logs/2026-06-21-0.4a-delivery.md) — 0.4-a 交付
- [logs/2026-06-21-0.4c-spec-and-prompt.md](logs/2026-06-21-0.4c-spec-and-prompt.md) — 0.4-c 规格与 Cursor 提示词
- [logs/2026-06-21-0.4d-spec-and-prompt.md](logs/2026-06-21-0.4d-spec-and-prompt.md) — 0.4-d 规格与 Cursor 提示词
- [logs/2026-06-21-output-interface-md-json.md](logs/2026-06-21-output-interface-md-json.md) — 输出接口 MD/JSON 决策
- [logs/2026-06-20-mini-mvp-delivery.md](logs/2026-06-20-mini-mvp-delivery.md) — 0.1 交付
- [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md) — 0.5 规划
- [logs/2026-06-20-0.9-release-candidate-spec.md](logs/2026-06-20-0.9-release-candidate-spec.md) — 0.9 RC 规划

## 文档权威性

- 架构冲突 → `01-architecture.md`
- 运行流程冲突 → `02-runtime-mechanism.md`
- 单 Loop 行为 → 对应 Loop 分册
- **阶段版本（个人优先）** → `34-version-roadmap-0x.md`；**1.x** → `42-1x-roadmap-personal-to-collaboration.md`；0.4 规格 → `40-personal-daily-loop-0.4-spec.md`；0.4-a/b/c/d 验收 → `43` / `44` / `45` / `48`；0.4-c/d 架构 → `46` / `49`
- semver 索引（含历史 0.6–0.8 详细规格）→ `33-version-roadmap.md`
- 是否完成 → `10-testing-and-acceptance.md` + 对应版本验收 doc（32/35/36）
- 当前行动项 → `41-next-steps-after-0.3.md`
- 新设计 **先改文档，再改代码**

## 核心结论

LoopPilot 由一个共享受控 Runtime、两个主 Loop 和一个小型信息 Loop 组成：

```text
DailyNewsLoop ──候选任务──┬──> InternLoop
                          └──> PaperLoop

InternLoop  = 昨日问题 → 最小修复 → 测试 → 诊断 → 再修复 → 开发报告
PaperLoop   = 当前缺口 → 查证 → 修订 → 引用/证据检查 → 再修订 → 论文报告
```

默认每个 Loop 约 30 分钟。价值在于有限时间内真正关闭一个问题，或准确指出下一步研究方向。
