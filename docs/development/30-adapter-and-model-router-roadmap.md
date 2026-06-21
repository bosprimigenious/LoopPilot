# 30 Adapter 与 ModelRouter 接入路线图

## 1. 背景与结论

本文规划 LoopPilot 如何接入 Cursor CLI、Codex CLI、Claude Code CLI、DeepSeek API，以及 Adapter + ModelRouter 的 V1/MVP 架构。结论先行：

- 当前代码已经具备 Mini 雏形，但还不能安全接入真实 Cursor CLI、Codex、Claude Code 或 DeepSeek。
- Loop 和 Agent 只应申请逻辑 `model_role`，不得写死模型品牌、CLI 产品或 API Provider。
- `ModelRouter` 根据 `models.yaml`、能力声明、预算、健康状态和数据策略选择 Adapter。
- `ModelAdapter` 统一连接 `MockAdapter`、`CodingCLIAdapter`、`APIModelAdapter` 等实现。
- Cursor CLI、Codex CLI、Claude Code CLI 不直接接入 Loop，也不由 Agent 自行调用；它们只是 `CodingCLIAdapter` 的不同配置。
- DeepSeek 更适合通过 `APIModelAdapter` 接入；只有本地存在受控 DeepSeek CLI wrapper 时，才考虑作为 `CodingCLIAdapter` 的一种配置。

本路线图依据：

- `19-adapter-specifications.md`：统一 Adapter 接口、`AdapterResult`、CLI/API Adapter 安全要求。
- `29-model-routing-and-runtime-policy.md`：逻辑 ModelRole、路由过滤、fallback、隐私、成本和变更规则。
- `28-agent-development-guide.md`：Agent 不直接实例化 Adapter、不绕过 Tool Broker、只声明 `model_role`。
- `12-development-work-breakdown.md`：Tool 与模型基础、Policy Engine、Loop 接入的依赖顺序。
- `09-versions.md`：Mini、V1、V2、V3 的能力边界。

## 2. 目标架构

目标调用链如下：

```text
Loop / Agent
  只声明 model_role
        ↓
ModelRouter
  读取 models.yaml
  按能力、数据等级、健康、预算、deadline 过滤
        ↓
ModelAdapter
  ├── MockAdapter
  ├── CodingCLIAdapter
  │     ├── Cursor CLI
  │     ├── Codex CLI
  │     └── Claude Code CLI
  └── APIModelAdapter
        ├── DeepSeek API
        ├── OpenAI-compatible API
        └── Anthropic-compatible API
```

关键边界：

- `Loop` 定义阶段、停止条件、产物和允许角色。
- `Agent` 只提交结构化请求、目标 Schema、权限需求和 `model_role`。
- `ModelRouter` 是确定性组件，只做选择、过滤和记录理由，不做模型推理。
- `ModelAdapter` 负责真实调用、输出归一、错误归一、审计记录和资源控制。
- `Tool Broker` 负责文件、Git、命令、网络等确定性能力，不能由 Agent 或模型绕过。

## 3. 当前实现现状

当前实现处于 Mini 可验证阶段：

- `src/loop_pilot/adapters/mock_adapter.py` 已有 `MockAdapter`，可从 fixture 返回确定性结果。
- `MockAdapter` 已有简化 `AdapterCapabilities`，覆盖 tools、file write、structured output、streaming、dry-run、context、network 等基础能力字段。
- `MockAdapter` 已有简化 `AdapterResult`，包含 `status`、`structured_output`、`duration_ms`、`error_code`、stdout/stderr artifact。
- `MockAdapter` 支持 `timeout`、`invalid_schema` 等场景化返回，但尚未实现真实取消、成本估算、完整 transcript、tool calls 和 usage 结构。
- `src/loop_pilot/models/router.py` 已有确定性 `ModelRouter`，能按 role 返回 adapter id，并在未知 adapter 时退回 mock。
- `config/models.yaml` 仍是 Mini mock 配置，role 使用 `planning/coding/research/writing/screening/evaluation`，尚未迁移到 `reasoning_strong/coding_agent/research_analysis/...` 等逻辑角色。

因此，当前代码适合 Mini 和回归 fixture，不适合直接运行真实编码 CLI 或外部模型 API。

## 4. 接口缺口

V1/MVP 接入真实 Adapter 前，至少需要补齐以下接口和运行能力。

### 4.1 BaseAdapter 协议

需要将当前分散在 `MockAdapter` 内的概念提升为共享协议：

- `capabilities() -> AdapterCapabilities`
- `healthcheck() -> HealthStatus`
- `execute(request, timeout, cancellation) -> AdapterResult`
- `estimate_cost(request) -> CostEstimate`
- `normalize_error(error) -> LoopPilotError`

协议应明确 request、timeout、cancellation、artifact、usage、错误类型和敏感字段脱敏规则。

### 4.2 完整 AdapterResult

当前 `AdapterResult` 只是简化结构。V1/MVP 应对齐 `19-adapter-specifications.md`：

- `status: success | timeout | cancelled | error`
- `structured_output`
- `stdout_artifact`
- `stderr_artifact`
- `transcript_artifact`
- `tool_calls`
- `usage.input_tokens`
- `usage.output_tokens`
- `usage.cost`
- `usage.duration_ms`
- `error_code`

CLI Adapter 和 API Adapter 必须都返回相同结构，Loop 不应关心底层是 CLI 还是 API。

### 4.3 CodingCLIAdapter

`CodingCLIAdapter` 是 Cursor CLI、Codex CLI、Claude Code CLI 的统一承载层。它需要支持：

- 配置化命令模板、参数、工作目录、timeout、输出 Schema。
- `cwd` 只能是批准 worktree。
- 环境变量使用 allowlist，禁止默认继承完整用户环境。
- 进程硬 timeout、取消 token、进程组终止和退出码捕获。
- stdout、stderr、原始 transcript 和结构化输出留存为 Artifact。
- CLI 执行前后记录 Git 和文件 snapshot。
- 禁止 push、部署、访问禁止路径和越权写入。
- dry-run 模式只允许读取和生成计划，不落盘修改。
- 输出 Schema 失败或退出码非零时不得进入 PASS。

Cursor CLI、Codex CLI、Claude Code CLI 的差异应体现在 `models.yaml` 的 adapter 配置中，而不是体现在 Loop 或 Agent 代码中。

### 4.4 APIModelAdapter

`APIModelAdapter` 用于 DeepSeek API、OpenAI-compatible API、Anthropic-compatible API 等 Provider。它需要支持：

- Provider endpoint、模型名、auth env var、timeout、重试策略的配置化。
- 输入为 AgentInput 和显式 JSON Schema。
- 结构化输出解析失败最多修复一次。
- 429/5xx 有限退避重试。
- 认证、权限、无效请求、能力不足不重试同 Adapter。
- 记录 request id、实际模型、token、费用、延迟和缓存命中。
- Provider fallback 只能在同一 `model_role` 且满足策略时发生。

DeepSeek 默认应通过该 Adapter 接入；除非本地 DeepSeek CLI wrapper 能满足 `CodingCLIAdapter` 的全部约束，否则不应进入编码 CLI 链路。

### 4.5 ModelRouter 能力过滤

当前 `ModelRouter.resolve(role)` 只读取 role 到 adapter 的映射。V1/MVP 应升级为：

- 读取 `model_roles` 而非旧 `roles`。
- 根据 `require` 过滤 capabilities。
- 根据健康状态、预算、deadline 和数据等级过滤候选。
- 支持同 Role fallback。
- 无合格 Adapter 时返回 BLOCKED，而不是默默降级。
- 记录 selected adapter、排除候选、原因、预算和数据等级。

### 4.6 models.yaml 迁移

当前配置：

```yaml
roles:
  planning: {adapter: mock}
  coding: {adapter: mock}
  research: {adapter: mock}
  writing: {adapter: mock}
  screening: {adapter: mock}
  evaluation: {adapter: mock}
```

V1/MVP 目标应迁移为逻辑角色：

```yaml
model_roles:
  reasoning_strong:
    candidates: [mock_reasoner]
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

  research_analysis:
    candidates: [research_api]

  writing_strong:
    candidates: [writing_api]

  evaluation_strong_independent:
    candidates: [critic_api]

  screening_economical:
    candidates: [cheap_api]
    no_capable_adapter: deterministic_only

  summary_economical:
    candidates: [cheap_summary_api]
```

具体 adapter 示例：

```yaml
adapters:
  cursor_cli:
    kind: coding_cli
    command: cursor
    args: [...]
    timeout_seconds: 900
    env_allowlist: [...]

  codex_cli:
    kind: coding_cli
    command: codex
    args: [...]
    timeout_seconds: 900
    env_allowlist: [...]

  claude_code_cli:
    kind: coding_cli
    command: claude
    args: [...]
    timeout_seconds: 900
    env_allowlist: [...]

  deepseek_api:
    kind: api_model
    provider: deepseek
    endpoint: https://api.deepseek.com
    auth_env: DEEPSEEK_API_KEY
    timeout_seconds: 120
```

以上只是配置形态，不能视为默认启用。真实启用必须通过健康检查、golden case、故障测试和数据策略审核。

## 5. V1/MVP 实施计划

推荐先做 Adapter 层，再接 Loop。实施顺序如下。

### 5.1 Adapter 基础协议

- 定义 `BaseAdapter`、`AdapterCapabilities`、`AdapterResult`、`HealthStatus`、`CostEstimate`。
- 将 `MockAdapter` 改为实现共享协议。
- 保留 fixture 确定性，补齐 timeout、cancelled、invalid schema、rate limit、refusal 等 golden/fault 场景。
- 建立 Adapter 调用日志和脱敏规则。

完成门：

- 同一 request 在 Mock fixture 下可重复。
- `AdapterResult` 字段完整。
- 错误能映射到统一 `LoopPilotError`。

### 5.2 CodingCLIAdapter

- 实现受控进程启动、timeout、cancellation、进程组终止。
- 实现 cwd allowlist、env allowlist、命令模板校验。
- 实现执行前后 Git/file snapshot。
- 实现 stdout/stderr/transcript artifact。
- 实现结构化输出解析和失败归一。
- 增加 Cursor CLI、Codex CLI、Claude Code CLI 的配置示例，但不默认启用。

完成门：

- timeout 能终止真实子进程。
- dry-run 不产生写入。
- 非零退出码和 Schema 失败不会被判为成功。
- 未批准路径写入被拦截或报告为失败。

### 5.3 APIModelAdapter

- 实现 OpenAI-compatible 基础调用形态。
- 增加 DeepSeek API 配置样例。
- 实现 auth env 读取、请求 timeout、429/5xx retry、认证错误不重试。
- 实现 JSON Schema 输出解析和一次修复。
- 记录 token、费用、request id、延迟和实际模型。

完成门：

- 认证缺失能明确失败且不泄露密钥。
- 429/5xx 按策略重试。
- invalid schema 只修复一次，仍失败则返回统一错误。

### 5.4 ModelRouter 升级

- 将 `roles` 迁移到 `model_roles`。
- 实现候选 Adapter 能力过滤。
- 加入健康状态、预算、deadline、数据等级过滤。
- 支持 fallback 和 BLOCKED 结果。
- 记录选择理由和排除原因。

完成门：

- `coding_agent` 不会落到无 file write / tool call 能力的 Adapter。
- `SECRET` 数据不会进入任何模型。
- 无合格 Adapter 时显式 BLOCKED。
- 主 Adapter 不健康时只能 fallback 到同 Role 合格 Adapter。

### 5.5 Golden 与 Fault 测试

- Adapter golden：成功、timeout、cancelled、invalid schema、rate limit、refusal、auth missing。
- Router golden：每个 Role 正确选择主 Adapter、fallback、blocked、预算不足、敏感数据拒绝。
- CLI fault：超时进程、非零退出码、越权路径、污染环境变量、输出不合 Schema。
- API fault：429、5xx、401/403、bad request、费用超预算。

完成门：

- Adapter 被替换后 Loop 领域逻辑无需修改。
- 所有失败路径都有可审计 artifact 和统一错误类型。

## 6. 三条 Loop 接入方式

### 6.1 InternLoop

InternLoop 的真实编码能力应通过：

```text
InternLoop / DevAgent
  → model_role: coding_agent
  → ModelRouter
  → CodingCLIAdapter
  → Cursor CLI / Codex CLI / Claude Code CLI
```

要求：

- `CodeContextAgent` 继续使用 `analysis_medium` 或确定性扫描。
- `EngineeringPlannerAgent` 使用 `reasoning_strong`，只生成计划和验收条件。
- `DevAgent` 使用 `coding_agent`，但只在批准 worktree 和批准路径内写入。
- 测试、Git、文件快照由 Tool/Runtime 执行，不由模型自证。
- `TestDiagnoserAgent` 读取真实命令输出和 diff，不接受 DevAgent 自我声明。

### 6.2 PaperLoop

PaperLoop 更适合以 API 模型为主：

```text
PaperLoop
  → research_analysis / writing_strong / evaluation_strong_independent
  → ModelRouter
  → APIModelAdapter
```

建议映射：

- `ResearchContextAgent`：`research_analysis`
- `LiteratureScoutAgent`：`screening_economical`，抓取和核验仍由 Connector/Tool 完成。
- `GapDiagnoserAgent`：`reasoning_strong`
- `WritingAgent`：`writing_strong`
- `ResearchCriticAgent`：`evaluation_strong_independent`

要求：

- 写作模型不得创造数字、引用或实验事实。
- Critic 与 Writer 必须满足独立评价策略。
- 引用核验和证据位置必须由确定性 Tool 或 Connector 支撑。
- API fallback 不能把强评价降级为便宜摘要模型。

### 6.3 DailyNewsLoop

DailyNewsLoop 首先依赖 Connector 和确定性工具，模型只做扩展查询、筛选和忠实摘要：

```text
DailyNewsLoop
  → connectors/tools
  → screening_economical / summary_economical
  → ModelRouter
  → APIModelAdapter or MockAdapter
```

建议映射：

- `NewsScoutAgent`：通常无模型；查询扩展时使用 `screening_economical`。
- `SourceRankerAgent`：`screening_economical`。
- `DailyNewsSynthesisAgent`：`summary_economical`。

要求：

- 采集、去重、时间核验、来源可信度门槛由确定性代码执行。
- 模型不能把搜索摘要当作正式证据。
- Connector 单源失败不能破坏主 Loop。
- 日报只展示事实摘要和影响推断，原始调用记录进入脱敏审计 Artifact。

## 7. 安全边界

接入真实 CLI/API 前必须满足以下边界：

- Agent 不直接调用 CLI、API、shell、Git 或网络写入。
- Cursor CLI、Codex CLI、Claude Code CLI 只能通过 `CodingCLIAdapter` 运行。
- DeepSeek API 只能通过 `APIModelAdapter` 或等价受控 Adapter 运行。
- `SECRET` 永不进入任何模型。
- `SENSITIVE` 只发往用户明确允许且通过测试的 Adapter。
- CLI `cwd` 必须是批准 worktree。
- CLI 环境变量必须 allowlist。
- CLI 执行前后必须记录 Git/file snapshot。
- 禁止 push、部署、删除未批准路径、修改生产配置。
- 超时、取消、非零退出码、Schema 失败和能力不足都必须归一为可审计失败。
- 没有合格 Adapter 时必须 BLOCKED，不得让 Agent 自行寻找替代路径。

## 8. 测试验收

V1/MVP 的测试验收应覆盖三层。

### 8.1 Adapter 层

- `MockAdapter` fixture 可重复。
- `CodingCLIAdapter` 能终止 timeout 进程。
- `CodingCLIAdapter` 能捕获 stdout、stderr、exit code、transcript。
- `CodingCLIAdapter` dry-run 不写入。
- `CodingCLIAdapter` 拒绝未批准 cwd、路径和环境变量。
- `APIModelAdapter` 正确处理 auth missing、429、5xx、invalid schema。
- 所有 Adapter 返回完整 `AdapterResult`。

### 8.2 Router 层

- 每个逻辑 Role 正确选择主 Adapter。
- 主 Adapter 不健康时 fallback。
- 无合格 Adapter 时 BLOCKED。
- 预算不足不启动调用。
- `SECRET` 被拒绝。
- `SENSITIVE` 不路由到未授权 Adapter。
- `coding_agent` 不落到无文件能力模型。
- 路由日志包含选择理由和候选排除原因。

### 8.3 Loop 层

- InternLoop 能通过 `coding_agent` 在测试 worktree 完成受控修改。
- PaperLoop 能通过 API 模型推进一个证据受限修订，并在证据不足时停止。
- DailyNewsLoop 能在 Connector 部分失败时继续处理其他来源。
- 三条 Loop 的报告只引用真实状态、命令输出、Artifact 和核验结果。
- Adapter 失败不会破坏状态机，也不会误报 PASS。

## 9. 里程碑顺序

推荐里程碑如下：

1. `M0`：冻结当前 Mini mock 路径，确保三条 Loop fixture 继续可运行。
2. `M1`：抽出 `BaseAdapter` 协议和完整 `AdapterResult`，让 `MockAdapter` 对齐新协议。
3. `M2`：升级 `models.yaml` schema，引入 `model_roles`、candidates、capability require 和 no-capable 策略。
4. `M3`：升级 `ModelRouter`，实现能力过滤、健康过滤、预算/deadline/data policy、fallback 和 BLOCKED。
5. `M4`：实现 `CodingCLIAdapter` 的进程、安全、snapshot、artifact 和故障测试。
6. `M5`：实现 `APIModelAdapter`，先支持 DeepSeek/OpenAI-compatible 基础路径。
7. `M6`：将 InternLoop 的 `DevAgent` 接到 `coding_agent`，先只跑受控 fixture/worktree。
8. `M7`：将 PaperLoop 的研究、写作、独立评价角色接到 API Adapter。
9. `M8`：将 DailyNewsLoop 的筛选和摘要角色接到经济 API Adapter，同时保持 Connector 确定性。
10. `M9`：运行三 Loop golden/fault 场景，形成真实 Adapter 启用清单。

## 10. 暂不做事项

以下事项不进入 V1/MVP：

- 不让 Loop 或 Agent 直接调用 Cursor CLI、Codex CLI、Claude Code CLI 或 DeepSeek。
- 不把某个品牌模型写死为默认主链路。
- 不在没有 Adapter 测试前启用真实 CLI 写入真实仓库。
- 不让普通聊天 API 模型替代 `coding_agent` 修改 worktree。
- 不用便宜摘要模型替代 `reasoning_strong` 或 `evaluation_strong_independent`。
- 不实现浏览器自动化登录模型服务作为 Provider 接入方式。
- 不把 API key、token、用户完整环境变量写入 trace 或 artifact。
- 不允许模型自行 push、部署、安装依赖或修改生产配置。
- 不在 V1/MVP 追求复杂质量学习排序；先使用可解释的配置优先级、健康状态、成本和 golden 通过率。

## 11. README / 开发索引链接建议

建议在 `docs/development/README.md` 的阅读顺序中新增：

```markdown
29. [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)：Cursor CLI、Codex、Claude Code、DeepSeek 的 Adapter 与 ModelRouter 接入路线图。
```

本次仅新增路线图文档，不修改索引。是否更新索引可作为后续单独文档维护任务。
