# LoopPilot 开发文档索引

本目录是 LoopPilot 的正式开发说明。`ideas.md` 仅保存原始思路，根目录 `DEVELOPMENT_PLAN.md` 只作为入口。

## 命名与 Mini 决策基线

- 项目名：`LoopPilot`。
- PyPI distribution 与 CLI：`loop-pilot`。
- Python import 与源码目录：`loop_pilot` / `src/loop_pilot/`。
- Mini 状态：本地 JSON 快照 + JSONL 事件，通过 `StateStore` 接口访问。
- V1 状态：SQLite、事务检查点和完整恢复。
- Mini CLI：`doctor`、`run`、`run all`、`status`、`inspect`。
- `resume`、`approve`、`reject`、`cancel` 从 V1 开始；Mini 不暴露占位或假成功命令。

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

## 文档权威性

- 架构冲突时，以 `01-architecture.md` 为准。
- 运行流程冲突时，以 `02-runtime-mechanism.md` 为准。
- 单个 Loop 行为以对应 Loop 分册为准。
- 版本范围以 `09-versions.md` 为准。
- 是否完成以 `10-testing-and-acceptance.md` 为准。
- Mini 边界以 `09-versions.md` 与 `25-mini-run-path.md` 为准。
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
