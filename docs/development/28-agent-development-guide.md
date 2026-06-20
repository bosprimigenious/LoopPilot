# 28 Agent 开发规范

## 1. 目的

本文定义 LoopPilot Agent 的设计、实现、调用关系、输入输出、权限、失败、日志和测试。Agent 不是自由聊天机器人，而是由确定性 Runtime 管理、具有严格契约的推理角色。

## 2. 实现语言与基础技术

核心运行层使用 Python，最低基线为 Python 3.11；正式实现时通过 `pyproject.toml` 固定实际支持版本和依赖版本。

| 能力 | 方案 |
|---|---|
| CLI | Typer 或等价成熟 CLI 库 |
| 数据契约 | Pydantic + JSON Schema |
| 配置 | YAML + Schema 校验 |
| Mini 状态 | 本地 JSON `StateStore` |
| Mini Trace | JSONL |
| V1 状态与恢复 | SQLite `StateStore` |
| HTTP | httpx 或等价可超时客户端 |
| RSS/HTML | feedparser、BeautifulSoup 或来源专用解析器 |
| 报告 | Markdown 模板 |
| 测试 | pytest |
| 终端显示 | Rich，可选 |

TypeScript 不用于首个核心 Runtime；未来 Web UI 可以独立使用，不得反向控制状态机。

## 3. 四类能力边界

| 类型 | 职责 | 模型 | 示例 |
|---|---|---:|---|
| Agent | 判断、规划、诊断、写作、取舍 | 通常需要 | DevAgent、ResearchCriticAgent |
| Skill | 可复用、有步骤和契约的能力 | 可选 | minimal-patch、claim-evidence-analysis |
| Tool | 确定性本地操作 | 不需要 | Git、pytest、读写文件 |
| ModelAdapter | 连接具体模型或 CLI | 是 | CodingCLIAdapter、APIModelAdapter |

Connector 是外部数据读取适配器，属于基础设施，不是 Agent。

## 4. Agent 基础接口

概念接口：

```python
class Agent(Protocol):
    id: str
    role: str
    model_role: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    allowed_tools: frozenset[str]
    forbidden_actions: frozenset[str]

    def run(self, context: AgentContext) -> AgentResult:
        ...
```

`AgentContext` 必须包含：

- `run_id`、`round_id`、`task_id`；
- 经过裁剪的 Context Bundle；
- Artifact 引用而非任意全盘路径；
- 当前预算；
- Policy 约束；
- 允许 Tool；
- 目标输出 Schema；
- cancellation token 和 deadline。

`AgentResult` 必须包含：

```yaml
status: success | insufficient_context | refused | error
summary: string
produced_artifacts: []
claims: []
proposed_actions: []
risks: []
uncertainties: []
requires_human: boolean
retry_recommendation: none | retry_with_new_evidence | stop
```

AgentResult 不能直接修改 `RunPhase`、`RunOutcome`、预算或审批状态。

## 5. 调用规则

```text
Orchestrator（确定性代码）
  ├── 选择当前阶段允许的 Agent
  ├── Context Builder 生成 AgentContext
  ├── Tool Broker 执行 Agent 提出的获批 Tool 请求
  ├── Model Router 选择 ModelAdapter
  └── 校验 AgentResult 后提交下一状态
```

严格禁止：

- Agent 直接调用另一个 Agent；
- Agent 直接实例化 ModelAdapter；
- Agent 绕过 Tool Broker 执行 shell、Git 或网络写入；
- Agent 自行重试；
- Worker 为自己的结果判定 PASS；
- Report Agent 改写运行事实。

Agent 间协作只能通过 Orchestrator 和已持久化 Artifact 完成。

## 6. 六层架构中的 Agent

| 层 | 是否放 Agent | 说明 |
|---|---:|---|
| L0 Trigger | 否 | CLI、Scheduler 只产生 RunRequest |
| L1 Control | 否 | Orchestrator、预算、审批必须确定性 |
| L2 Loop Definition | 否 | 定义阶段、角色、停止条件和输出 |
| L3 Runtime | 否 | 状态机、Retry、Policy、Artifact 必须确定性 |
| L4 Capability | 是 | 所有 Agent、Skill、Tool、Connector、Adapter |
| L5 State & Evidence | 否 | Mini JSON/JSONL；V1 SQLite；报告、缓存和工作区 |

所谓“OrchestratorAgent”在本项目中不成立。需要复杂任务选择时，由 L4 的 PlannerAgent 提交建议，L1 Orchestrator 依据 Schema、Policy 和预算决定是否采用。

## 7. InternLoop Agent

### CodeContextAgent

- 输入：仓库地图、Git 状态、昨日任务、测试/CI 日志。
- 输出：相关文件、基线、风险、任务候选。
- 权限：只读文件、搜索、只读 Git；默认无网络。
- 模型角色：`analysis_medium`；纯扫描步骤使用 Tool。
- 失败：上下文缺失、仓库过大、项目说明冲突。

### EngineeringPlannerAgent

- 输入：Context、候选任务、预算和 Policy。
- 输出：单任务 TaskPlan。
- 权限：只读；不能修改文件和执行命令。
- 模型角色：`reasoning_strong`。
- 限制：必须给出验收条件、允许路径和验证命令。

### DevAgent

- 输入：已批准 TaskPlan、相关文件和失败证据。
- 输出：修改提案或 worktree 内受控修改。
- 权限：批准路径写入、白名单命令请求；无 push/部署。
- 模型角色：`coding_agent`。
- 失败：范围扩大、依赖缺失、需要业务决策。

### TestDiagnoserAgent

- 输入：真实命令、stdout/stderr、退出码、diff。
- 输出：失败分类、根因证据和修复建议。
- 权限：只读验证 Artifact；不能改代码。
- 模型角色：`analysis_medium` 或 `reasoning_strong`。
- 注意：测试由 Tool 执行，Retry 由 Orchestrator 决定。

### InternReportNarrator（可选）

基础报告由模板生成。只有复杂诊断需要归纳时才调用该 Agent；它只能写“诊断与建议”段，不能写状态、命令和测试事实。

## 8. PaperLoop Agent

### ResearchContextAgent

- 输入：草稿、实验、notes、文献矩阵和昨日任务。
- 输出：Paper State、弱点和候选缺口。
- 权限：只读论文工作区。
- 模型角色：`research_analysis`。

### LiteratureScoutAgent

- 输入：研究问题、关键词、来源白名单和时间窗。
- 输出：SourceItem 候选和筛选理由。
- 权限：通过 Connector 网络读取；不能修改正文。
- 模型角色：`screening_economical`。
- 注意：抓取、去重和元数据核验由 Tool 完成。

### GapDiagnoserAgent

- 输入：Paper State、Claim、Evidence 和评价结果。
- 输出：最重要缺口及优先级。
- 权限：只读。
- 模型角色：`reasoning_strong`。

### WritingAgent

- 输入：已批准 Revision Plan、可信 Evidence、可写章节。
- 输出：一个章节或论证单元的修订。
- 权限：仅论文副本的批准章节。
- 模型角色：`writing_strong`。
- 禁止：创造数字、引用和实验事实。

### ResearchCriticAgent

- 输入：E1–E5 的确定性/结构化检查及修订稿。
- 输出：Reviewer concern、风险和修复优先级。
- 权限：只读；不能修改草稿。
- 模型角色：`evaluation_strong_independent`。
- 隔离：不能看到 WritingAgent 的自评，只看实际 Artifact。

### PaperReportNarrator（可选）

只负责将复杂研究诊断压缩为易读建议；事实、引用状态和检查结果仍由模板渲染。

## 9. DailyNewsLoop Agent

### NewsScoutAgent

- 输入：主题、来源注册表、游标和时间窗。
- 输出：SourceItem 候选。
- 权限：网络只读；不能写主 Loop 工作区。
- 模型角色：通常不需要，查询扩展时用 `screening_economical`。

### SourceRankerAgent

- 输入：已去重和核验的事件簇、评分特征。
- 输出：保留/过滤建议及理由。
- 权限：只读。
- 模型角色：`screening_economical`。
- 约束：可信度门槛、条目上限由代码执行，Agent 不能突破。

### DailyNewsSynthesisAgent

- 输入：通过阈值的 DailyNewsItem。
- 输出：事实摘要、影响推断和候选动作。
- 权限：只写日报草稿；不能创建正式主 Loop Task。
- 模型角色：`summary_economical`。
- 路由：Orchestrator 校验后才写 Inbox。

## 10. 权限矩阵

| Agent | 读文件 | 写文件 | 命令 | 网络 | Git 写 | 修改事实数据 |
|---|---:|---:|---:|---:|---:|---:|
| CodeContext | 限定 | 否 | 只读 | 否 | 否 | 否 |
| EngineeringPlanner | Artifact | 否 | 否 | 否 | 否 | 否 |
| Dev | 限定 | 批准路径 | 白名单请求 | 默认否 | 否 | 否 |
| TestDiagnoser | Artifact | 否 | 否 | 否 | 否 | 否 |
| ResearchContext | 论文只读 | 否 | 否 | 否 | 否 | 否 |
| LiteratureScout | Artifact | 否 | 否 | 只读 | 否 | 否 |
| Writing | 限定 | 批准章节 | 否 | 否 | 否 | 否 |
| ResearchCritic | Artifact | 否 | 否 | 可选只读 | 否 | 否 |
| NewsScout | 缓存 | 仅缓存提案 | 否 | 只读 | 否 | 否 |
| SourceRanker | Artifact | 否 | 否 | 否 | 否 | 否 |
| NewsSynthesis | Artifact | 日报草稿 | 否 | 否 | 否 | 否 |

权限由 Tool Broker 强制执行，不依赖 Prompt 自律。

## 11. Retry 与人工审批

```text
Worker → Evaluator → Diagnoser/Reflector → Orchestrator → 下一 Round
```

只有 Orchestrator 可以增加 Round。Agent 可以建议 Retry，但必须提供新证据、改变的假设和下一计划差异。

以下情况停止并请求人工决定：秘密/生产配置、删除、依赖变更、push/部署、引用无法核验、缺实验数据、付费调用超预算、范围扩大或证据矛盾。

## 12. Agent 文件结构

```text
src/loop_pilot/agents/<agent_name>/
├── agent.py
├── input.py
├── output.py
├── prompt.md
├── permissions.yaml
├── contract.yaml
└── tests/
```

共享基类只提供契约校验、调用记录和取消支持，不封装具体业务 Prompt。

## 13. Agent 测试与完成定义

每个 Agent 必须具备：

- 输入/输出 Schema 单元测试；
- 成功、拒绝、证据不足和 Adapter 失败 Golden Case；
- dry-run；
- 权限边界和越权请求测试；
- timeout/cancellation；
- 输出敏感信息扫描；
- 确定性 Tool 与模型判断分界测试；
- 不同 Adapter 的契约兼容测试。

没有契约、权限、错误路径和 Golden Case 的 Agent 不得进入 Loop。
