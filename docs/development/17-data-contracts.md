# 17 数据契约与 Schema

本文定义跨组件传递的稳定对象。正式实现必须在 `schemas/` 中提供对应 JSON Schema，并用同一组 Golden 数据验证生产者和消费者。

## 1. 通用字段

所有对象必须包含：

```yaml
schema_version: "1.0"
id: stable-unique-id
created_at: RFC3339 timestamp with timezone
source: producer component id
content_hash: sha256 canonical payload
```

未知字段默认拒绝；Schema 升级必须提供 migration。

## 2. RunRequest

```yaml
run_id: "2026-06-20T073000+0800-intern-001"
loop_type: intern | paper | daily_news
trigger: manual | schedule | resume  # resume 从 V1 开始
objective: string | null
workspace_id: string
config_snapshot_hash: sha256
parent_run_id: string | null
requested_by: owner | scheduler
```

## 3. RunRecord

```yaml
run_id: string
attempt_id: integer
phase: RunPhase
outcome: succeeded | partial | no_action | deferred | blocked | failed | exhausted | cancelled | null
started_at: timestamp
soft_deadline_at: timestamp
hard_deadline_at: timestamp
finished_at: timestamp | null
current_round: integer
budgets: BudgetSnapshot
workspace_snapshot: ArtifactReference
last_checkpoint_id: string | null
terminal_reason: string | null
report_status: pending | generated | failed
review_status: pending | accepted | rejected | needs_more_info | manual_fix | archived | null
```

## 4. LoopTask 与 TaskPlan

```yaml
task_id: string
title: string
origin: user | yesterday | project | inbox | failure
priority: critical | high | normal | low
objective: string
acceptance_criteria: [string]
allowed_paths: [string]
forbidden_paths: [string]
required_evidence: [string]
estimated_minutes: integer
status: proposed | selected | running | completed | rejected | expired
```

`TaskPlan` 额外包含 `steps`、`tools`、`validation_commands`、`risks`、`approval_requirements` 和 `rollback_plan`。

## 5. RoundRecord / LoopTrace

```yaml
round_id: integer
state_before: RunState
plan_artifact: ArtifactReference
input_artifacts: [ArtifactReference]
actions: [ActionRecord]
output_artifacts: [ArtifactReference]
evaluation_id: string | null
decision: pass | retry | human | stop
reason_code: string
started_at: timestamp
finished_at: timestamp
```

完整 Trace 是 RunRecord、按序 RoundRecord、状态事件和最终 Artifact Manifest 的组合，不维护第二套相互矛盾的 trace 状态。

## 6. AgentInput / AgentOutput

```yaml
agent_id: string
role: string
objective: string
context_artifacts: [ArtifactReference]
constraints: [string]
allowed_tool_ids: [string]
required_output_schema: string
remaining_budget: BudgetSnapshot
```

```yaml
agent_id: string
status: success | insufficient_context | refused | error
summary: string
claims: [ClaimRecord]
proposed_actions: [ActionProposal]
produced_artifacts: [ArtifactReference]
uncertainties: [string]
```

AgentOutput 不得直接写 RunState，只能提供结构化建议。

## 7. EvaluationResult / RetryDecision

```yaml
evaluation_id: string
verdict: pass | retryable_fail | needs_human | fatal
checks:
  - check_id: string
    status: pass | fail | not_run | not_configured
    evidence: [ArtifactReference]
    message: string
blocking_findings: [Finding]
non_blocking_findings: [Finding]
```

```yaml
retry: boolean
reason_code: string
new_evidence: [ArtifactReference]
changed_assumption: string | null
next_plan_delta: [string]
estimated_minutes: integer
```

`retry=true` 时 `new_evidence` 或 `changed_assumption` 至少有一个非空。

## 8. ArtifactReference / ArtifactManifest

```yaml
artifact_id: string
kind: report | patch | log | source | checkpoint | draft | evaluation
path: workspace-relative path
media_type: string
sha256: string
size_bytes: integer
created_by: component id
contains_sensitive_data: boolean
```

Manifest 记录所有 ArtifactReference、Run 终态、保留等级和父子关系。

## 9. PaperClaim / EvidenceItem

```yaml
claim_id: string
text: string
document_path: string
start_line: integer | null
claim_type: contribution | result | comparison | causal | generalization | background
strength: strong | moderate | qualified
evidence_ids: [string]
support_status: supported | partial | unsupported | contradicted
```

```yaml
evidence_id: string
evidence_type: experiment | citation | table | figure | source_text
source_ref: ArtifactReference
locator: string
verified_at: timestamp
verification_level: metadata | abstract | fulltext | reproduced
supports: [claim_id]
limitations: [string]
```

## 10. SourceItem / DailyNewsItem

```yaml
source_item_id: string
canonical_url: string
source_id: string
source_tier: A | B | C
title: string
authors: [string]
published_at: timestamp | null
event_at: timestamp | null
fetched_at: timestamp
content_hash: sha256
raw_artifact: ArtifactReference | null
```

DailyNewsItem 增加 `category`、`confirmed_facts`、`inferences`、`relevance_score`、`reliability_score`、`actionability_score`、`confidence`、`cross_sources` 和 `route_decision`。

## 11. ReviewRecord

ReviewRecord 从 V1 开始由 CLI 持久化。Mini 只在 Markdown 报告中给出人工 Review 建议，不提供状态回写命令。

```yaml
review_id: string
run_id: string
decision: accept | reject | needs_more_info | run_next_round | manual_fix | archive
reason: string
selected_artifacts: [ArtifactReference]
task_status_after: string
inbox_status_after: string | null
reviewed_at: timestamp
```

Review 不改写原 Run 的 outcome；它记录用户是否采纳结果，并驱动任务或 Inbox 状态。

## 12. Markdown 契约

Markdown 报告不是自由文本，必须包含 YAML front matter：

```yaml
---
schema_version: "1.0"
run_id: string
loop_type: intern | paper | daily_news
terminal_state: string
generated_at: timestamp
artifact_manifest: relative/path
---
```

正文标题由模板固定；缺失字段写“未执行/未知”，不得删节制造完整假象。
