# Cursor V2 Implementation Prompt

你是 Cursor Agent，在仓库 [bosprimigenious/loop-pilot](https://github.com/bosprimigenious/loop-pilot) 中继续实现 LoopPilot。请使用中文沟通，代码和文档保持现有风格，符合 lint/format 要求。

## Scope

本阶段目标是 V2：扩大查询和验证能力。V2 建立在 V1/MVP 已经稳定的 SQLite 恢复、审批、Adapter 契约、ModelRouter、真实 Intern/Paper/DailyNews 最小链路之上。

V2 只扩展真实 Connector、引用核验、GitHub 增量快照、多模型质量/成本统计和故障注入，不改变 V1 的安全边界。

不要做：

- 不实现 V3 的长期优先级学习和跨日策略演化。
- 不增加自动 commit、push、PR、部署、投稿或交易。
- 不让更多来源绕过去重、置信度、原始来源核验和预算限制。
- 不修改 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md`。

## Read Before Coding

编码前必须阅读：

- `docs/development/09-versions.md`
- `docs/development/10-testing-and-acceptance.md`
- `docs/development/11-daily-operation.md`
- `docs/development/12-development-work-breakdown.md`
- `docs/development/13-source-and-crawler-plan.md`
- `docs/development/14-implementation-manifest.md`
- `docs/development/19-adapter-specifications.md`
- `docs/development/21-test-fixtures-and-golden-cases.md`
- `docs/development/22-error-and-budget-policy.md`
- `docs/development/24-configuration-spec.md`
- `docs/development/28-agent-development-guide.md`
- `docs/development/29-model-routing-and-runtime-policy.md`
- `docs/development/31-v1-v2-v3-implementation-roadmap.md`
- 当前 V1/MVP 已实现的 Connector、Adapter、Router、DailyNews、Paper 和测试文件。

如果 V1/MVP 能力缺失，不要绕过它实现 V2。先报告缺口，并建议回到 V1/MVP 补齐。

## First Response Before Edits

在改文件前，先用中文回复：

1. 你确认 V1/MVP 已具备哪些基础能力。
2. 本轮 V2 小切片属于 GitHub、论文元数据、引用核验、新闻交叉核验、模型统计还是故障注入。
3. 预计修改哪些文件和配置。
4. 计划新增哪些测试和 fixture。
5. 本切片如何证明不会破坏主 Loop。

## Implementation Target

按以下顺序推进 V2：

1. GitHub Connector 扩展：repository、release、issue、security advisory、star snapshot、增量排名和缓存修复工具。
2. 论文元数据扩展：至少两个可配置来源，统一稳定标识、去重、来源可信度和不完整覆盖标记。
3. 文献矩阵：记录 claim、source、证据位置、支持强度、冲突、citation key、更新时间和核验状态。
4. 引用全文证据位置：正式证据必须来自原始来源或可信全文片段；无法访问全文时输出 coverage incomplete。
5. 政治/财经/官方新闻交叉核验：区分事实、推断、发生时间、发布时间、原始来源和转述来源。
6. 多模型路由统计：按 role、adapter、agent golden case、失败率、延迟、费用、fallback 和 schema 通过率记录。
7. 故障注入与固定回归：断网、429/5xx、HTML selector 失效、SQLite 事务失败、锁遗留、测试进程挂起、外部修改。

每次只实现一个独立可验收切片。新增 Connector 必须先以受限来源和 fixture 测试接入，再进入每日主链。

## CLI / Config

V2 可以新增或扩展：

- source 配置项：`id`、`type`、`tier`、`enabled`、`endpoint`、`categories`、`rate_limit`、`cache_ttl`、`auth_env`、`parser`、`terms_checked`。
- Connector 级别 dry-run、cache、cursor、ETag、Last-Modified 和 schema changed 错误。
- GitHub snapshot 修复或重建脚本，但它必须是可选维护脚本，不是每日主链隐藏依赖。
- 模型统计导出或报告摘要，但原始调用记录必须脱敏并进入审计 Artifact。

配置禁止项：

- 不写明文密钥。
- 不允许无限来源、无限条目或无限重试。
- 不允许关闭强制 Policy Gate。
- 不允许用 CLI 参数隐藏覆盖安全策略。

## Tests

V2 必须重点补齐：

- GitHub 第一次快照只建基线，第二次以后才计算 star 增量。
- release/issue/security advisory 读取失败不会终止其他来源。
- DOI/arXiv/论文元数据去重和稳定标识合并。
- 引用证据位置缺失时不进入 verified。
- 新闻条目区分发生时间和发布时间。
- 多来源同事件去重，低置信度隔离。
- 429/5xx 有限重试，认证/权限错误不重试同 Adapter。
- HTML selector 失效映射为 SOURCE_SCHEMA_CHANGED。
- Router 统计记录 fallback、成本、延迟、schema 结果和数据等级。
- 固定回归场景覆盖 V1 成功链路和 V2 外部失败链路。

完成前至少运行：

```bash
pytest -q
git diff --check
```

如果不能联网测试，必须使用 fixture 和 mocked HTTP，并说明真实联网验证尚未运行。

## Discipline

- Connector 是外部数据读取适配器，不是 Agent。
- 搜索摘要只用于候选发现，正式证据需要打开原始来源。
- 单源失败不能终止主 Loop。
- 新 Adapter 必须先通过 Adapter 单元测试、Agent Golden Cases、质量/成本对比，再作为 fallback 观察，最后才可提升为 primary。
- 品牌名和“感觉更强”不能作为路由条件。
- V2 不能降低 V1 的安全、恢复、审批和预算标准。
- 不提交，不 push，除非用户明确要求。

## Completion Report

完成一个 V2 切片后，用中文报告：

- 修改的文件。
- 新增的 Connector、核验能力、统计能力或故障注入场景。
- 对 V1 主链的影响和兼容性说明。
- 运行的测试和结果。
- 未运行的测试及原因。
- 数据来源、成本、隐私或联网限制风险。
- 下一步建议。
