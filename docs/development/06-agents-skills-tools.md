# 06 Agent、Skill、Tool、Connector 与模型

## 1. 严格职责

| 类型 | 职责 | 示例 |
|---|---|---|
| Agent | 理解、规划、权衡和复杂诊断 | Planner、DevAgent、ResearchCritic |
| Skill | 可复用的稳定工作方法 | minimal-patch、claim-evidence-analysis |
| Tool | 确定性本地动作 | Git、文件、test、lint、parser |
| Connector | 外部系统读取适配 | GitHub、arXiv、Crossref、新闻源 |
| Model | 为 Agent 提供推理能力 | 通过逻辑角色配置 |

Agent 不等于进程，Skill 不等于一个随手命名的 Prompt，Connector 不负责业务判断。

## 2. Agent 契约

每个 Agent 必须声明：

- purpose；
- input schema；
- output schema；
- allowed tools；
- forbidden actions；
- evidence requirements；
- timeout；
- failure modes。

Worker 和 Evaluator 使用独立提示上下文。Evaluator 不接收 Worker 的“我已经完成”作为证据，只读取实际 diff、日志、草稿和来源。

## 3. 必要 Skills

### 共享

- context-budgeting
- task-selection
- risk-gate
- evidence-citation
- failure-diagnosis
- markdown-reporting

### InternLoop

- repository-mapping
- minimal-patch
- test-debugging
- diff-review

### PaperLoop

- paper-state-analysis
- literature-query
- citation-verification
- claim-evidence-analysis
- experiment-sufficiency
- related-work-coverage
- reviewer-simulation

### DailyNewsLoop

- source-screening
- event-date-verification
- news-deduplication
- importance-ranking
- relevance-routing

## 4. Tool 安全等级

| 等级 | 动作 | 默认策略 |
|---|---|---|
| Read | 读文件、搜索、git status | 自动允许 |
| Local Write | 写隔离副本、报告 | 计划范围内允许 |
| Execute | test、lint、build、解析脚本 | 白名单允许 |
| Network Read | API、RSS、官方页面 | 配置来源允许 |
| External Write | push、发消息、远程更新 | 默认禁止 |
| Destructive | 删除、覆盖、部署、密钥 | 禁止或人工批准 |

## 5. Model Router

业务代码只使用逻辑角色：

```yaml
models:
  planning: strong_reasoning_model
  coding: coding_model
  research: research_reasoning_model
  writing: writing_model
  screening: economical_model
  evaluation: independent_reasoning_model
```

模型选择可替换，但必须满足对应 Agent 的结构化输出、上下文、工具调用和稳定性要求。强模型用于任务选择、代码修复、研究诊断和最终评价；便宜模型只用于候选筛选、分类和初步摘要。

## 6. 调用记录

每次调用记录：

- Agent 和逻辑模型角色；
- 实际 provider/model；
- 输入与输出哈希；
- token、费用和延迟；
- 工具调用；
- 重试与错误；
- Schema 校验结果。

模型失败只能有限重试或切换预设备用模型，不能静默改变任务目标。
