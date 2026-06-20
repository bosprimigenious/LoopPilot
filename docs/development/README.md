# LoopPilot 开发文档索引

本目录是 LoopPilot 的正式开发说明。`ideas.md` 仅保存原始思路，根目录 `DEVELOPMENT_PLAN.md` 只作为入口。

## 命名与版本基线

- 项目名：`LoopPilot`。
- GitHub 仓库：[bosprimigenious/loop-pilot](https://github.com/bosprimigenious/loop-pilot)。
- PyPI distribution 与 CLI：`loop-pilot`。
- Python import 与源码目录：`loop_pilot` / `src/loop_pilot/`。
- **阶段版本**：采用 **0.x 体系**（0.1 → … → **0.5 public-beta** → **0.6 plugin-ecosystem** → **0.7 evaluation-benchmark** → **0.8 team-cloud-preview** → **0.9 release-candidate** → **1.0 stable**），semver 权威见 [33-version-roadmap.md](33-version-roadmap.md)；**0.5 完整实现清单**见 [34-version-roadmap-0x.md §6](34-version-roadmap-0x.md#6-05-public-beta--pypi050-public-beta)；**0.9 RC 规格**见 [34-version-roadmap-0x.md §10](34-version-roadmap-0x.md#10-09-release-candidate--stability-freeze090-release-candidate)。
- **当前工程焦点**：**仅 0.1 Mini-MVP**（Phase A checklist）；**0.2–1.0 均为文档规划，不得提前实现**。
- 0.1 状态：本地 JSON 快照 + JSONL 事件，通过 `StateStore` 接口访问。
- 0.4 状态：SQLite、事务检查点、恢复、审批、调度、daily-summary（**旧称「V1」每日自动化 = 0.4，不是 0.3**）。
- 0.5 状态：PyPI、开源 README、`init demo`、examples、release CI、CONTRIBUTING/SECURITY（**旧 V1 PyPI/开源 = 0.5，不是 0.4**）。
- 0.6 状态：本地插件生态（Loop/Skill/Connector/Adapter 扩展框架）。
- 0.7 状态：Evaluation Harness、benchmark 套件、模型对比与 eval report。
- 0.8 状态：本地优先团队协作（多项目 RBAC、共享审批、用量核算、Dashboard preview；**非** cloud SaaS）。
- 0.9 状态：RC 稳定化（API/配置/DB 冻结、conformance、安全审计、7 天长跑）。
- 1.0 状态：**生产就绪稳定承诺**（非功能堆叠；见 [33-version-roadmap.md §1.0](33-version-roadmap.md#100-stable--stableproduction-ready)）。
- 0.1 CLI：`doctor`、`run`、`run all`、`status`、`inspect`。
- `resume`、`approve`、`reject`、`cancel` 从 **0.4** 开始；0.1 不暴露占位或假成功命令。

## 阅读顺序

1. [00-system-definition.md](00-system-definition.md)：目标、边界和成功定义。
2. [01-architecture.md](01-architecture.md)：总体架构、组件依赖和三条 Loop 的关系。
3. [02-runtime-mechanism.md](02-runtime-mechanism.md)：状态机、预算、重试、锁和恢复。
4. [03-intern-loop.md](03-intern-loop.md)：实习开发闭环。
5. [04-paper-loop.md](04-paper-loop.md)：论文研究、引用、修订和评价闭环。
6. [05-daily-news-loop.md](05-daily-news-loop.md)：GitHub、研究、政治和财经高价值日报。
7. [06-agents-skills-tools.md](06-agents-skills-tools.md)：Agent、Skill、Tool、Connector 和模型职责。
8. [07-data-and-reports.md](07-data-and-reports.md)：状态、产物、Markdown 报告和数据契约。
9. [08-security-and-recovery.md](08-security-and-recovery.md)：权限、审批、故障和恢复。
10. [09-versions.md](09-versions.md)：Mini、V1、V2、V3 的实现范围。
11. [10-testing-and-acceptance.md](10-testing-and-acceptance.md)：测试体系和验收矩阵。
12. [11-daily-operation.md](11-daily-operation.md)：每天三次约 30 分钟的真实运行方式。
13. [12-development-work-breakdown.md](12-development-work-breakdown.md)：严格开发顺序和任务清单。
14. [13-source-and-crawler-plan.md](13-source-and-crawler-plan.md)：数据源、爬取器、API、去重和降级策略。
15. [14-implementation-manifest.md](14-implementation-manifest.md)：必须与可选的模块、脚本、配置和测试文件。
16. [15-ideas-traceability.md](15-ideas-traceability.md)：Ideas 内容的迁移、改名、替代和归档依据。
17. [16-design-audit.md](16-design-audit.md)：三个 Loop、文档闭环和 Ideas 删除条件的正式审计。
18. [17-data-contracts.md](17-data-contracts.md)：核心对象、Trace、Evidence、News 和 Markdown Schema。
19. [18-state-transition-spec.md](18-state-transition-spec.md)：逐状态进入条件、动作、转移和恢复。
20. [19-adapter-specifications.md](19-adapter-specifications.md)：模型、CLI、Web 与 Connector Adapter 协议。
21. [20-skill-specifications.md](20-skill-specifications.md)：共享与三 Loop Skill 的可执行规格。
22. [21-test-fixtures-and-golden-cases.md](21-test-fixtures-and-golden-cases.md)：真实 Fixture 目录和 Golden 断言。
23. [22-error-and-budget-policy.md](22-error-and-budget-policy.md)：错误决策、重试、预算和降级。
24. [23-human-review-protocol.md](23-human-review-protocol.md)：人工接受、拒绝、继续和状态回写。
25. [24-configuration-spec.md](24-configuration-spec.md)：全局与三 Loop 配置 Schema。
26. [25-mini-run-path.md](25-mini-run-path.md)：从 Mock 到真实 Adapter 的最小可运行路径。
27. [28-agent-development-guide.md](28-agent-development-guide.md)：Agent 语言、层级、调用图、权限、契约与逐 Loop 角色。
28. [29-model-routing-and-runtime-policy.md](29-model-routing-and-runtime-policy.md)：模型角色、Adapter 选择、Fallback、隐私、成本和替换策略。
29. [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)：Adapter 契约、ModelRouter 能力与 V1 接入顺序。
30. [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md)：Mini 后 V1/MVP、V2、V3 的实施路线和阶段边界（Legacy 任务分解）。
31. [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md)：0.1 Mini-MVP 验收范围与验证命令。
32. [33-version-roadmap.md](33-version-roadmap.md)：**权威** semver 路线图（**完整链 0.1–1.0**；含 **§1.0 production-ready 规格**）。
33. [33-next-steps-v1.md](33-next-steps-v1.md)：V1 后续规划（Legacy → 0.2/0.3/0.4/0.5 映射）。
34. [33-next-steps-0.2.md](33-next-steps-0.2.md)：当前行动项（0.1 后 0.2）；§7 含 **0.5 远期 checklist**。
35. [34-version-roadmap-0x.md](34-version-roadmap-0x.md)：**0.1→1.0 详细路线图**；§6 = 0.5 Public Beta；**§10 = 0.9 RC 完整规格**；§11 = 1.0 概要。
36. [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md)：0.5 规划决策日志。
37. [logs/2026-06-20-0.9-release-candidate-spec.md](logs/2026-06-20-0.9-release-candidate-spec.md)：0.9 RC / Stability Freeze 规划决策日志。
38. [logs/2026-06-20-mini-mvp-delivery.md](logs/2026-06-20-mini-mvp-delivery.md)：0.1 Mini-MVP 交付与验证日志。

## 文档权威性

- 架构冲突时，以 `01-architecture.md` 为准。
- 运行流程冲突时，以 `02-runtime-mechanism.md` 为准。
- 单个 Loop 行为以对应 Loop 分册为准。
- **阶段版本与推进顺序以 `33-version-roadmap.md` 为准**（完整链 **0.1 → … → 1.0**）；**0.5 发布规格以 `34-version-roadmap-0x.md` §6 为准**；**0.9 RC 以 §10 为准**；**1.0 稳定承诺以 33 §1.0 为准**。
- 版本能力描述见 `09-versions.md`（Legacy）；与 33 冲突时以 33 为准。
- 是否完成以 `10-testing-and-acceptance.md` 与 `32-mini-mvp-acceptance.md`（0.1）为准。
- 0.1 Mini-MVP 边界以 `33-version-roadmap.md` §0.1、`32-mini-mvp-acceptance.md` 与 `25-mini-run-path.md` 为准。
- 仓库内 sqlite/recovery/approvals 等 WIP 代码归属 **0.4**，见 `33-version-roadmap.md` §0.4「既有 WIP」。
- 当前行动项以 `33-next-steps-v1.md` 与 `33-next-steps-0.2.md` 为准。
- Legacy 任务细节以 `31-v1-v2-v3-implementation-roadmap.md` 为准（旧 V1 每日自动化 → 0.4；旧 V1 PyPI/开源 → **0.5**）。
- 新设计必须先修改文档，再修改代码。

## 核心结论

LoopPilot 由一个共享受控 Runtime、两个主 Loop 和一个小型信息 Loop 组成：

```text
DailyNewsLoop ──候选任务──┬──> InternLoop
                          └──> PaperLoop

InternLoop  = 昨日问题 → 最小修复 → 测试 → 诊断 → 再修复 → 开发报告
PaperLoop   = 当前缺口 → 查证 → 修订 → 引用/证据检查 → 再修订 → 论文报告
```

默认每个 Loop 运行约 30 分钟。系统的价值不是“每天生成很多内容”，而是在有限时间内真正关闭一个问题，或准确指出下一步最应该推进的研究方向。
