# 29 模型路由与运行策略

## 1. 目的

本文规定 Agent 如何申请模型能力、ModelRouter 如何选择具体 Adapter、何时降级、何时停止，以及如何记录质量、成本和故障。Agent 代码不得写死模型供应商或产品名。

## 2. ModelRouter 的性质

ModelRouter 是确定性组件，不是 Agent。它根据配置和运行条件选择满足要求的 Adapter：

```text
Agent 请求 ModelRole
  ↓
过滤：能力、数据策略、上下文、工具、结构化输出
  ↓
过滤：健康状态、预算、deadline
  ↓
按配置优先级选择 Adapter
  ↓
记录选择理由和候选排除原因
```

## 3. 逻辑 ModelRole

| Role | 用途 | 必需能力 |
|---|---|---|
| reasoning_strong | 任务规划、Gap 诊断 | 强推理、结构化输出 |
| coding_agent | 代码读取与修改 | 文件编辑/Tool、长代码上下文 |
| analysis_medium | 上下文总结、错误归因 | 稳定结构化分析 |
| research_analysis | 论文状态和证据分析 | 长上下文、引用谨慎 |
| writing_strong | 论文修订 | 高质量写作、遵守证据约束 |
| evaluation_strong_independent | Research Critic | 独立上下文、强推理 |
| screening_economical | 大量候选筛选 | 低成本、批处理、JSON |
| summary_economical | 日报与复杂诊断摘要 | 低成本、忠实压缩 |

测试、安全、状态、预算、去重和硬阈值不属于 ModelRole，由确定性代码负责。

## 4. Agent 默认路由

| Agent | 主 Role | 可接受降级 |
|---|---|---|
| CodeContextAgent | analysis_medium | 确定性扫描 + summary_economical |
| EngineeringPlannerAgent | reasoning_strong | 无强能力 Adapter 时停止 |
| DevAgent | coding_agent | 另一个 coding_agent Adapter |
| TestDiagnoserAgent | analysis_medium | reasoning_strong（复杂失败） |
| ResearchContextAgent | research_analysis | reasoning_strong |
| LiteratureScoutAgent | screening_economical | analysis_medium |
| GapDiagnoserAgent | reasoning_strong | 无安全降级 |
| WritingAgent | writing_strong | reasoning_strong |
| ResearchCriticAgent | evaluation_strong_independent | 另一独立强模型 |
| NewsScoutAgent | 无/Tool | screening_economical 仅扩展查询 |
| SourceRankerAgent | screening_economical | 确定性排名 |
| DailyNewsSynthesisAgent | summary_economical | analysis_medium |

## 5. 具体 Adapter 候选

系统可以配置 Cursor CLI、Codex、OpenAI-compatible API、Anthropic-compatible API、DeepSeek-compatible API 或 MockAdapter，但它们只是候选实现。

- 编码 CLI：适合 `coding_agent`，必须在批准 worktree 运行。
- 强推理 API/CLI：适合规划、研究诊断和独立评价。
- 经济模型 API：适合筛选和摘要。
- MockAdapter：Mini、故障注入和回归测试必需。

是否启用某个具体产品，取决于本机可用性、当前能力、费用、数据策略和通过的 Adapter 测试，不能由文档中的品牌推荐自动决定。

## 6. 路由配置

```yaml
model_roles:
  reasoning_strong:
    candidates: [primary_reasoner, fallback_reasoner]
    require:
      structured_output: true
      tools: false
    no_capable_adapter: block

  coding_agent:
    candidates: [primary_coding_cli, fallback_coding_cli]
    require:
      file_write: true
      tool_calls: true
      dry_run: true
    no_capable_adapter: block

  screening_economical:
    candidates: [cheap_api]
    no_capable_adapter: deterministic_only
```

Adapter 的 endpoint、命令、模型名、auth 环境变量和 timeout 在 `models.yaml` 定义。

## 7. 选择因子

按硬过滤后软排序：

### 硬过滤

- 所需 Tool/文件能力；
- 结构化输出支持；
- 上下文容量；
- 数据是否允许离开本机；
- Adapter 健康状态；
- 剩余预算和时间；
- 是否满足独立评价要求。

### 软排序

- 对该 Agent 的 Golden Case 通过率；
- 最近失败率和延迟；
- 单次估算成本；
- 缓存可用性；
- 配置优先级。

品牌名和“感觉更强”不能作为未量化的路由条件。

## 8. 数据与隐私路由

每次调用先标记数据等级：

```text
PUBLIC       可公开论文、公开代码和新闻
PROJECT      私有但非敏感项目内容
SENSITIVE    未公开论文、内部代码、个人数据
SECRET       密钥、token、凭据（禁止进入模型）
```

Adapter 声明可处理的数据等级。`SECRET` 永不进入任何模型；SENSITIVE 默认只发往用户明确允许的 Adapter，且先做最小上下文与脱敏。

## 9. Fallback 与降级

允许 Fallback：

- 同一 Role 的另一个已验证 Adapter；
- 筛选/摘要转为确定性规则或缓存；
- 非强制扩展任务延后。

禁止 Fallback：

- 用便宜摘要模型替代强规划或 Research Critic；
- 用搜索摘要替代引用全文核验；
- 在没有 coding 能力时让普通聊天模型直接写 worktree；
- 因预算不足跳过安全和真实性检查。

没有合格 Adapter 时必须 BLOCKED，而不是偷偷降低完成标准。

## 10. Retry 策略

- Rate limit/5xx：同 Adapter 有限退避，最多配置次数。
- Timeout：同 Adapter 最多一次；第二次考虑同 Role fallback。
- 无效 Schema：修复提示一次；仍失败则 fallback/停止。
- 认证、权限、内容策略、能力不足：不重试同 Adapter。
- Agent 业务判断失败不属于 Adapter Retry，应回到 Loop 的诊断流程。

任何重试都消耗模型调用、token、时间和费用预算。

## 11. 独立评价策略

Worker 与 Evaluator 至少满足一种隔离：

- 不同 Adapter/模型；或
- 同一模型但独立会话、不同 Prompt、只读取最终 Artifact；
- 关键事实再由确定性 Tool 验证。

ResearchCritic 不读取 WritingAgent 的内部推理；TestDiagnoser 不把 DevAgent 的自我声明当作测试证据。

## 12. 成本、延迟和质量记录

每次路由和调用记录：

- requested role；
- selected Adapter/model；
- 被排除候选及原因；
- 输入/输出 token；
- 费用和估算/实际标识；
- 首 token 与总延迟；
- timeout、retry、fallback；
- Schema 通过；
- Agent Golden Case 版本；
- cache hit；
- 数据等级。

日报只显示汇总，原始调用记录进入审计 Artifact 并脱敏。

## 13. 缓存策略

- 模型缓存键包含 Agent 版本、Prompt 哈希、Schema、输入 Artifact 哈希和模型标识。
- 代码工作区、论文草稿或来源变化后缓存失效。
- 任务规划、审批、实时新闻和最终评价默认不复用陈旧缓存。
- 缓存命中仍记录来源和生成时间。

## 14. ModelRouter 测试

必须覆盖：

- 每个 Role 正确选择主 Adapter；
- 主 Adapter 不健康时 Fallback；
- 无合格 Adapter 时 BLOCKED；
- 预算不足时不启动调用；
- SENSITIVE 数据不路由到未授权 Adapter；
- SECRET 被拒绝；
- coding Role 不落到无文件能力模型；
- schema/timeout/rate-limit 错误路径；
- 独立 Evaluator 不读取 Worker 私有上下文；
- 路由日志完整且脱敏。

## 15. 变更规则

新增或替换 Adapter 时：

1. 实现 `19-adapter-specifications.md` 接口；
2. 通过 Adapter 单元和故障测试；
3. 运行对应 Agent Golden Cases；
4. 对比质量、成本和延迟；
5. 更新 `models.yaml`，不修改 Agent 代码；
6. 先作为 fallback 观察，再提升为 primary。

未经上述验证，不得因为新模型流行或价格便宜直接进入每日主运行链。
