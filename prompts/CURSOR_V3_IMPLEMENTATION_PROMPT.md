# Cursor V3 Implementation Prompt (_legacy)

> **Legacy prompt — V3 对应长期稳定运行规划，当前未实施。**  
> 文档体系：[docs/zh/05-文档体系说明.md](../docs/zh/05-文档体系说明.md) · [docs/en-core.md](../docs/en-core.md)

## 目标（中文，远期）

跨日优先级、健康检查、报告质量收敛——**需 V1/V2 等价阶段完成后才适用**。

---

你是 Cursor Agent，在仓库 [bosprimigenious/LoopPilot](https://github.com/bosprimigenious/LoopPilot) 中继续实现 LoopPilot。请使用中文沟通，代码和文档保持现有风格，符合 lint/format 要求。

## Scope

本阶段目标是 V3：长期稳定运行与高质量决策。V3 建立在 V1/MVP 的真实每日链路和 V2 的外部来源/引用核验能力之上，重点实现跨日问题链、优先级解释、历史诊断比较、健康检查、保留策略和报告质量收敛。

V3 不追求更多高风险自动化动作。用户规则始终最高，所有学习、排序和建议都必须可解释、可审计、可关闭。

不要做：

- 不自动 commit、push、PR、部署、投稿或交易。
- 不让学习排序覆盖用户显式规则。
- 不用历史相似性替代当日验证。
- 不降低 V1/V2 的安全、恢复、Adapter、Router、引用核验和来源可信度标准。
- 不修改 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md`。

## Read Before Coding

编码前必须阅读：

- `docs/development/09-versions.md`
- `docs/development/10-testing-and-acceptance.md`
- `docs/development/11-daily-operation.md`
- `docs/development/12-development-work-breakdown.md`
- `docs/development/14-implementation-manifest.md`
- `docs/development/17-data-contracts.md`
- `docs/development/18-state-transition-spec.md`
- `docs/development/22-error-and-budget-policy.md`
- `docs/development/23-human-review-protocol.md`
- `docs/development/24-configuration-spec.md`
- `docs/development/28-agent-development-guide.md`
- `docs/development/29-model-routing-and-runtime-policy.md`
- `docs/development/31-v1-v2-v3-implementation-roadmap.md`
- 当前 V1/V2 已实现的 StateStore、Artifact、Inbox、Router、Connector、报告和测试。

如果 V1/V2 关键能力未完成，不要实现依赖它们的 V3 自动决策。先报告缺口。

## First Response Before Edits

在改文件前，先用中文回复：

1. 你确认 V1/V2 哪些能力已稳定。
2. 本轮 V3 小切片属于跨日问题链、优先级解释、风险评估、Reviewer Simulation、健康检查、历史诊断还是报告质量。
3. 预计修改哪些文件和数据契约。
4. 计划新增哪些长期运行或回归测试。
5. 本切片如何保持用户规则最高优先级。

## Implementation Target

按以下顺序推进 V3：

1. 跨日问题链：连接昨日 next action、用户反馈、失败诊断、审批决定、DailyNews 候选和今天任务选择。
2. 优先级解释：为每个候选记录用户规则、任务价值、证据强度、历史阻塞、预算、风险和选择/未选择原因。
3. InternLoop 风险评估增强：回归范围、静态分析、diff 风险、依赖风险、敏感路径、回滚建议和人工决定点。
4. PaperLoop Reviewer Simulation 增强：独立评价、实验设计建议、研究方向演化、一致性追踪和历史 reviewer concern 对比。
5. 长期运行健康检查：SQLite 增长、Artifact 保留、缓存失效、锁清理、配置漂移、Adapter 成功率、费用趋势和调度健康。
6. 历史诊断比较：把今天的失败与过去类似失败对比，给出“相同点、不同点、这次应避免什么”。
7. 报告质量收敛：每日总报告顶部只突出最重要的一件事，细节进入 run 报告和证据链。

每次只实现一个可解释、可测试、可关闭的小切片。优先做数据契约和确定性规则，再考虑 Agent 摘要。

## CLI / Config

V3 可以新增或扩展：

- 健康检查命令或 `doctor` 子项，检查状态增长、锁、缓存、Adapter 健康、费用和 scheduler。
- 报告或 inspect 增强，展示跨日链路、优先级解释和历史诊断比较。
- 保留策略配置：Artifact、cache、model logs、GitHub snapshots、news cache、old checkpoints。
- 用户规则和排序权重配置，但用户显式规则必须不可被模型或学习逻辑覆盖。

配置要求：

- 所有学习/排序特性必须可关闭。
- 排序权重必须有默认值和 Schema 校验。
- 健康检查不能修改业务状态，除非用户明确执行 cleanup/repair 类命令。
- cleanup 必须支持 dry-run。

## Tests

V3 必须重点补齐：

- 用户显式规则高于历史学习排序。
- 同一候选跨日不会重复创建任务。
- 昨日 BLOCKED 能正确影响今天选择，但不会自动变成成功。
- 历史相似失败只作为建议，不跳过当日测试。
- Intern 风险评估能识别 diff 越界、依赖变更、敏感路径和回滚缺失。
- Paper Reviewer Simulation 与 WritingAgent 保持独立上下文。
- 健康检查识别锁遗留、缓存过期、状态膨胀、配置漂移和 Adapter 高失败率。
- 保留策略 dry-run 不删除文件，真实执行有审计记录。
- 每日报告在无任务、成功、阻塞、失败、部分完成时都能说明最重要的一件事。

完成前至少运行：

```bash
pytest -q
git diff --check
```

长期运行相关能力需要补充固定回归或模拟多日 fixture。如果无法真实连续运行，必须说明用哪些 fixture 模拟。

## Discipline

- V3 的“学习”只能调整候选排序和解释，不能绕过用户规则、Policy、预算、Adapter 能力和事实核验。
- 所有跨日结论必须有状态、Artifact、用户反馈或来源证据支撑。
- 报告 Agent 只能压缩和解释，不能改写事实字段。
- 健康检查默认只读，cleanup/repair 必须显式、可审计、支持 dry-run。
- 历史诊断比较不能替代当前测试、引用核验或来源核验。
- 不提交，不 push，除非用户明确要求。

## Completion Report

完成一个 V3 切片后，用中文报告：

- 修改的文件。
- 新增的长期运行、决策解释、健康检查或报告质量能力。
- 用户规则最高优先级如何被保证。
- 运行的测试和结果。
- 未运行的长期测试及原因。
- 数据保留、隐私、成本或误排序风险。
- 下一步建议。
