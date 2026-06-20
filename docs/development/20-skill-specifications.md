# 20 Skill 执行规格

## 1. Skill 卡片模板

每个 `SKILL.md` 必须包含：

```text
Skill ID / Version / Purpose
When to use / When not to use
Caller
Input Schema / Output Schema
Allowed Tools / Forbidden Actions
Deterministic Steps / Model Steps
Failure Codes
Evidence Requirements
Example Input / Example Output
Unit Tests / Golden Cases
```

## 2. 共享 Skill

| Skill | 输入 | 输出 | 主要失败 |
|---|---|---|---|
| context-budgeting | 候选 Artifact、token 预算 | Context Bundle | CONTEXT_MISSING/TOO_LARGE |
| task-selection | 候选任务、预算、历史 | Selected LoopTask | NO_ACTION/AMBIGUOUS |
| risk-gate | TaskPlan、Policy | PolicyDecision | POLICY_DENIED |
| evidence-citation | 结论、EvidenceItem | 带证据结论 | EVIDENCE_MISSING |
| failure-diagnosis | 错误、日志、状态 | Diagnosis | ROOT_CAUSE_UNKNOWN |
| markdown-reporting | RunRecord、Manifest | Markdown report | REPORT_RENDER_FAILED |

## 3. InternLoop Skill

### repository-mapping

- 输入：仓库路径、项目说明、文件树、Git 状态。
- 输出：入口、模块、测试、配置、相关文件与风险。
- 工具：只读文件、搜索、Git。
- 失败：未知构建系统、仓库过大、说明冲突。

### minimal-patch

- 输入：批准的 TaskPlan、相关代码、验收条件。
- 输出：受限文件修改与修改理由。
- 禁止：无关重构、删除失败测试、修改禁止路径。
- 失败：范围扩大、依赖用户决策、无法构造验证。

### test-debugging

- 输入：命令、stdout/stderr、退出码、diff。
- 输出：失败分类、证据位置、根因假设和下一动作。
- 约束：必须引用日志，不能只输出“可能有问题”。

### diff-review

- 输入：基线、diff、TaskPlan。
- 输出：范围、风险、无关改动、敏感信息和回归判断。
- 该 Skill 主要由确定性 Tool 完成，模型只解释复杂影响。

## 4. PaperLoop Skill

### literature-query

- 输入：研究问题、关键词、时间窗、来源白名单。
- 输出：去重后的 SourceItem 候选。
- 失败：SOURCE_UNAVAILABLE、覆盖不足、查询过宽。

### citation-verification

- 输入：候选来源、待支持 claim。
- 输出：EvidenceItem、支持程度、稳定标识和正文位置。
- 禁止：仅凭标题生成 BibTeX；把搜索摘要当全文证据。

### claim-evidence-analysis

- 输入：论文段落、实验 Artifact、已核验引用。
- 输出：PaperClaim 列表与 support_status。
- 失败：无法定位 claim、证据冲突、数据文件缺失。

### experiment-sufficiency

- 输入：论文 claim、实验清单、投稿/任务配置。
- 输出：已有、缺失、优先级与理由。
- 约束：根据任务配置，不机械套通用清单。

### related-work-coverage

- 输入：研究主题分类、草稿、文献矩阵。
- 输出：覆盖类别、遗漏、差异表述风险。

### reviewer-simulation

- 输入：E1–E5 的诊断证据。
- 输出：主要 concern、位置、修复类型和优先级。
- 禁止：脱离证据自由打分。

## 5. DailyNewsLoop Skill

### source-screening

- 输入：SourceItem、来源注册表。
- 输出：来源等级、是否需要交叉核验。

### event-date-verification

- 输入：多个报道、原始公告。
- 输出：事件发生、公告、报道三个时间及置信度。

### news-deduplication

- 输入：规范 URL、标题、内容哈希、实体与事件时间。
- 输出：事件簇、主来源和重复项。

### importance-ranking

- 输入：事件簇、用户项目、阈值。
- 输出：分项分数、保留/过滤理由。

### relevance-routing

- 输入：高置信度 DailyNewsItem。
- 输出：Intern/Paper/Watch/Ignore，及可执行候选任务。

## 6. Skill 完成定义

- Schema 已实现并验证。
- 成功、证据不足、拒绝、工具失败 Golden Case 通过。
- Tool 权限最小化。
- 输出可被调用方直接消费。
- 错误使用统一错误码。
- 文档示例与实现测试共享同一 fixture。
