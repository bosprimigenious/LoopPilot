# 19 Model、CLI 与 Web Adapter 规范

## 1. 统一接口

```text
capabilities() -> AdapterCapabilities
healthcheck() -> HealthStatus
execute(request, timeout, cancellation) -> AdapterResult
estimate_cost(request) -> CostEstimate
normalize_error(error) -> LoopPilotError
```

所有 Adapter 必须支持超时、取消、结构化错误、原始输出留存、敏感字段脱敏和调用指标。

## 2. AdapterResult

```yaml
status: success | timeout | cancelled | error
structured_output: object | null
stdout_artifact: ArtifactReference | null
stderr_artifact: ArtifactReference | null
transcript_artifact: ArtifactReference | null
tool_calls: [ToolExecution]
usage:
  input_tokens: integer | null
  output_tokens: integer | null
  cost: decimal | null
  duration_ms: integer
error_code: string | null
```

## 3. MockAdapter（Mini 必需）

- 从固定 fixture 返回确定结果。
- 支持成功、超时、无效 Schema、限流和拒绝场景。
- 不访问网络、不修改真实工作区。
- 用于状态机、重试和报告的确定性测试。

## 4. CodingCLIAdapter

适配 Cursor CLI、Codex CLI 或同类编码 CLI，具体产品由配置选择。

强制约束：

- `cwd` 必须是批准的 worktree；
- 环境变量使用白名单；
- 捕获 stdout、stderr、退出码和原始 transcript；
- 设置硬 timeout 和进程组终止；
- 执行前后记录 Git/文件快照；
- 禁止 CLI 自行 push、部署或访问禁止路径；
- 退出码非零或输出 Schema 失败时不得进入 PASS；
- dry-run 只允许读取和生成计划，不落盘修改。

## 5. APIModelAdapter

适配 OpenAI-compatible、Anthropic-compatible 或其他模型 API。

- 输入为 AgentInput 和显式 JSON Schema；
- 结构化输出解析失败最多修复一次；
- 429/5xx 可退避重试，认证/权限/无效请求不可重试；
- 记录实际模型、token、费用、request id 和延迟；
- Provider 切换只能使用预配置 fallback，不改变 Agent 约束。

## 6. WebSearchAdapter

- 只执行网络读取；
- 返回 SourceItem，不直接返回最终新闻或论文结论；
- 保存查询、时间范围、域名过滤、结果 URL 和抓取时间；
- 搜索摘要只用于候选发现，正式证据需要打开原始来源；
- 超时或部分失败必须标记覆盖不完整。

## 7. HTTP/RSS/HTML Connector Adapter

- 优先 ETag、Last-Modified、cursor 和缓存；
- 429/5xx 有限重试；
- robots/条款不允许时禁用 HTML 抓取；
- HTML selector 失效触发 SOURCE_SCHEMA_CHANGED；
- 单源失败不能终止其他源；
- 原始响应中的 cookie、token、个人字段不得进入报告。

## 8. 能力声明

每个 Adapter 声明：

```yaml
supports_tools: boolean
supports_file_write: boolean
supports_structured_output: boolean
supports_streaming: boolean
supports_dry_run: boolean
max_context_tokens: integer | null
network_required: boolean
```

Planner 只能选择满足任务要求的 Adapter；不允许尝试调用后才发现关键能力缺失。

## 9. Adapter 验收

- 健康检查不产生副作用。
- timeout 能终止底层操作。
- 原始输出与结构化结果均可审计。
- 错误能映射到统一错误类型。
- dry-run 不产生写入。
- 同一 fixture 的 Mock 结果可重复。
- Adapter 被替换后 Loop 领域逻辑无需修改。
