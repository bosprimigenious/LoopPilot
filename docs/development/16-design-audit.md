# 16 设计自检报告

## 1. 审计范围

本次检查覆盖：三个 Loop、共享 Runtime、权限与恢复、Markdown 产物、开发版本、实现文件、脚本清单、Ideas 迁移和文档交叉引用。

## 2. 三个 Loop 闭环检查

| 检查项 | InternLoop | PaperLoop | DailyNewsLoop |
|---|---|---|---|
| 明确输入 | 通过 | 通过 | 通过 |
| 单任务/有限结果 | 通过 | 通过 | 通过 |
| 观察真实状态 | 通过 | 通过 | 通过 |
| 任务选择规则 | 通过 | 通过 | 通过 |
| 执行前计划 | 通过 | 通过 | 通过 |
| Policy Gate | 通过 | 通过 | 通过 |
| 实际动作 | 代码修改 | 论文修订/引用核验 | 抓取/核验/路由 |
| 客观验证 | 测试、lint、build、diff | 引用、实验、数字、一致性 | 来源、日期、去重、快照 |
| 失败诊断 | 通过 | 通过 | 通过共享 Runtime |
| 有限重试 | 通过 | 通过 | 通过共享 Runtime |
| 停止条件 | 通过 | 通过 | 通过 |
| 检查点与恢复 | 通过共享 Runtime | 通过共享 Runtime | 通过共享 Runtime |
| Markdown 报告 | 通过 | 通过 | 通过 |
| 下一步任务 | 通过 | 通过 | 通过 Inbox/日报 |

设计层面三条 Loop 均已闭环。

## 3. 跨日闭环

```text
昨日开发 next-actions ──> 今日 InternLoop ──> 今日开发报告 ──> 明日任务
昨日论文 next-actions ──> 今日 PaperLoop  ──> 今日论文报告 ──> 明日方向
今日 DailyNews ─────────> 两个 Inbox ──────> 主 Loop 选择/拒绝 ─> 候选状态更新
```

关键规则已经明确：用户任务和昨日未关闭问题高于新闻候选；新闻不能驱动未验证的自动修改。

## 4. 设计成熟度判断

### 已经充分明确

- 六层逻辑架构与依赖方向；
- 确定性 Orchestrator 与模型能力分离；
- 状态、预算、锁、审批、检查点和恢复；
- 两个主 Loop 和一个信息 Loop 的权限边界；
- 25 分钟执行、5 分钟收尾；
- Intern 的真实修复与测试链；
- Paper 的引用查询、证据链和评价管线；
- DailyNews 的少量高价值过滤和 GitHub 增量逻辑；
- 所有用户可见 Markdown 报告；
- Mini/V1/V2/V3 与验收；
- 必需和可选文件、模块、脚本。

### 只能在实现后验证

- 具体模型在真实任务上的成功率和成本；
- 每个目标仓库的 test/lint/build 命令；
- 论文全文访问权限与解析质量；
- 每个新闻/论文来源的 API、限速、条款和页面稳定性；
- GitHub 热度异常检测是否足够可靠；
- 30 分钟是否适合不同规模任务；
- Reviewer Simulation 与人工判断的一致性。

因此目前可以说“开发设计已经闭环”，不能说“所有组件已经经过运行证明”。运行证明必须来自 `10-testing-and-acceptance.md` 的测试证据。

## 5. Ideas 覆盖检查

- 架构、Loop、Agent、Skill、信息源、模型、报告、三轮限制和 Paper Evaluator 均已建立迁移关系。
- 重复对话、宣传性措辞、冲突层级和时效性模型判断未逐字复制。
- TextGuard 类论文关键词被正确下沉为 `paper.yaml` 项目配置，而不是写死在框架。
- 具体 Agent/Skill 名称的改名与替代已记录在 `15-ideas-traceability.md`。

结论：有效内容已迁移，原始文本仍有历史追溯价值。

## 6. 是否删除 ideas.md

当前不删除。目录尚无 Git 历史，直接删除会失去原始来源。当前处理已经足够规范：文件顶部明确标为历史原稿，并链接正式入口和迁移表。

项目进入版本控制后，建议将其移动为：

```text
docs/archive/ideas-original.md
```

归档后根目录只保留 `DEVELOPMENT_PLAN.md`。

## 7. 文档细分检查

当前文档已经按以下边界拆分：定义、架构、Runtime、三个 Loop、能力体系、数据报告、安全恢复、版本、测试验收、每日运行、任务分解、数据源、实现清单、迁移追踪和设计审计。

不建议继续把每个小节拆成独立文件。继续细拆会增加跳转成本和内容重复。下一次拆分应发生在真正开始编码后，例如给每个 Connector、Schema 或 Skill 建立与代码同目录的局部说明。

## 8. 最终审计结论

- **三个 Loop 设计**：通过设计审计。
- **整体运行闭环**：通过设计审计。
- **文档细分程度**：充足，不建议继续横向拆分。
- **开发指导详细度**：补充实现清单后达到编码启动要求。
- **Ideas 迁移**：有效内容已迁移并可追踪，不是逐字复制。
- **Ideas 删除**：当前不建议；应在纳入版本控制后归档。
- **组件已验证**：尚未；必须通过实现、场景和故障测试获得证据。

## 9. 附件建议复审后的补充

后续工程复审提出的数据契约、状态转换、Adapter、Skill、Golden Fixture、错误预算、人工 Review、配置和 Mini 运行路径确属必要，已补充为 17–25 分册。

以下建议没有重复新建分册，而是并入已有规范：

- Artifact 命名与保留：强化 `07-data-and-reports.md`；
- Source Registry：强化 `13-source-and-crawler-plan.md`；
- 实现文件清单：已有 `14-implementation-manifest.md`；
- Ideas 迁移：已有 `15-ideas-traceability.md`；
- Worktree：保留在 Intern、架构、安全和实现清单；
- Web UI、向量记忆、多项目并发：仍非当前必需。

补充后，文档已从“可启动编码”推进到“具备接口与验收约束的实现规格”。是否正确仍需 Mini 与 Golden Cases 的运行证据验证。

## 10. Agent 与模型路由专项补充

Agent 开发和模型路由已分别写入 `28-agent-development-guide.md` 与 `29-model-routing-and-runtime-policy.md`。专项设计坚持以下决定：

- Orchestrator 是确定性控制器，不是强模型 Agent；
- 所有 Agent 位于 L4 Capability；
- Agent 不能相互直接调用、不能自行重试、不能直接选择具体模型；
- 报告事实由模板渲染，Report Narrator 仅为可选摘要角色；
- ModelRouter 依据能力、预算、数据等级和 Golden 表现选择 Adapter；
- 没有合格模型时阻塞，不降低安全和真实性标准。

## 11. Mini 一致性纠错记录

后续实现前审计发现三项真实冲突，现已统一：

1. 项目名为 `LoopPilot`，distribution/CLI 为 `loop-pilot`，Python import/source 为 `loop_pilot` / `src/loop_pilot/`。
2. Mini 只实现 JSON 状态快照、JSONL 事件和 `StateStore` 接口；SQLite、事务检查点和恢复属于 V1。
3. Mini CLI 只提供 doctor、run、run all、status、inspect；resume、approve、reject、cancel 从 V1 开始，Mini 不注册假命令。

此纠错已同步到架构、Runtime、数据、开发顺序、实现清单、Mini 路径、Agent 指南和 Cursor 提示词。后续实现不得用“以某一份文档为准”绕过同层规格冲突。
