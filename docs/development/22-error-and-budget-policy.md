# 22 错误分类与预算策略

## 1. 统一错误表

| Error code | 默认重试 | Reflect | 当前 Loop | 其他 Loop |
|---|---:|---:|---|---|
| CONFIG_INVALID | 否 | 否 | BLOCKED | 不影响 |
| CONTEXT_MISSING | 否 | 否 | BLOCKED | 不影响 |
| MODEL_RATE_LIMIT | 最多 2 | 否 | 退避 | 不影响 |
| MODEL_TIMEOUT | 最多 1 | 是 | 可重试 | 不影响 |
| MODEL_OUTPUT_INVALID | 修复 1 次 | 是 | 可重试 | 不影响 |
| TOOL_FAILED | 视分类 | 是 | 可重试/失败 | 不影响 |
| TOOL_TIMEOUT | 最多 1 | 是 | 停止进程 | 不影响 |
| POLICY_DENIED | 否 | 否 | BLOCKED | 不影响 |
| EVALUATION_FAILED | 最多剩余轮次 | 是 | 可重试 | 不影响 |
| SOURCE_UNAVAILABLE | 每源 2 次 | 否 | 降级/部分 | 不影响 |
| SOURCE_SCHEMA_CHANGED | 否 | 否 | 隔离该源 | 不影响 |
| STORAGE_FAILED | 否 | 否 | FAILED | 暂停新 Run |
| WORKSPACE_CHANGED | 否 | 否 | WAITING_APPROVAL | 不影响 |
| BUDGET_EXCEEDED | 否 | 否 | EXHAUSTED | 不影响 |
| HUMAN_REQUIRED | 否 | 否 | WAITING_APPROVAL | 不影响 |
| REPORT_RENDER_FAILED | 单独重建 1 次 | 否 | 保留结果 | 不影响 |

## 2. 错误报告字段

```yaml
error_id: string
code: stable error code
component: string
message: sanitized string
retryable: boolean
attempt: integer
evidence: [ArtifactReference]
state_at_failure: RunState
recommended_action: string
caused_by: error_id | null
```

## 3. 默认预算

```yaml
global_daily:
  max_cost: user_configured
  max_model_calls: user_configured

intern:
  max_duration_minutes: 30
  finalization_reserve_minutes: 5
  max_rounds: 3
  max_model_calls: 8
  max_changed_files: 5
  max_changed_lines: 400

paper:
  max_duration_minutes: 30
  finalization_reserve_minutes: 5
  max_rounds: 3
  max_model_calls: 12
  max_new_sources: 10
  max_modified_sections: 1

daily_news:
  max_duration_minutes: 30
  finalization_reserve_minutes: 5
  max_model_calls: 6
  max_fetched_items_per_source: 50
  max_kept_items: 10
```

这些是安全默认值，不是对所有项目都正确的性能结论。

## 4. 预算检查点

预算在 Run 创建、每次模型/工具调用前、每个 Round 后和软截止时检查。估算动作超过剩余预算时不得启动。

## 5. 降级顺序

1. 缩小候选数和上下文。
2. 使用缓存和已经验证的证据。
3. 将筛选任务切换到配置的经济模型。
4. 跳过非强制扩展检查并明确标记未运行。
5. 保存 PARTIAL/EXHAUSTED，而不是突破硬预算。

强制安全、真实性和验收检查不得因省成本而跳过。

## 6. 成本报告

每份 Run 报告记录每个 Agent 的调用数、token、费用、延迟和缓存命中。无法获得精确费用时写 `unknown`，不能填估算为实际值。每日总报告汇总预算使用和被预算阻止的动作。
