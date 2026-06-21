# 31 V1/MVP、V2、V3 实施路线图

> **版本编号已更新 — 请先读 [33-version-roadmap.md](33-version-roadmap.md)**  
> 本文保留历史「V1/V2/V3」实施细节，供对照与追溯。**新工作必须使用 semver 编号。**
>
> | 旧称呼 | 新编号 | 要点 |
> |---|---|---|
> | Mini | **0.1.0-mini** | 当前工程焦点（Phase A） |
> | V1 中的 Adapter / ModelRouter / 真实 Connector | **0.3.0-adapter-mvp** | **0.3 ≠ 旧称 V1** |
> | V1 中的 SQLite / 恢复 / 审批 CLI / OS 调度 | **0.4.0-daily-runner** | 旧「V1/MVP」每日自动化主体 |
> | V1 中的真实工作区与 Markdown 审阅 | **0.2.0-practical-mvp** | safety-first，dry-run 为主 |
> | V1 中的 PyPI / 开源 README / CONTRIBUTING / examples | **0.5.0-public-beta** | **不是 0.4**；Public Beta 发布质量 |
> | V2 | 拆入 0.3 / 0.4 / 1.0 | Connector 与核验扩展 |
> | V3 | **1.0.0-stable** | 长期个人生产 |
>
> 下文「V1/MVP」若无特别说明，指 **0.2 + 0.3 + 0.4 的合并历史范围**；实施时请按 33 拆阶段，**不要一次性实现整段 V1**。

本文用于 Mini（**0.1**）完成后的阶段推进。它不是重新定义架构，而是把 `09-versions.md`、`10-testing-and-acceptance.md`、`11-daily-operation.md`、`12-development-work-breakdown.md`、`14-implementation-manifest.md`、`19-adapter-specifications.md`、`24-configuration-spec.md`、`28-agent-development-guide.md`、`29-model-routing-and-runtime-policy.md` 和当前代码状态整理成可执行顺序。

## 1. Mini 当前状态与边界

Mini 的目标是证明 LoopPilot 的受控闭环成立，不是进入每天真实工作的版本。当前代码和配置体现了这个边界：

- `src/loop_pilot/adapters/mock_adapter.py` 已提供确定性 `MockAdapter`，支持 fixture 返回、timeout 和 invalid schema 等基础场景，但尚未实现 Coding CLI、API 模型、WebSearch 或 HTTP/RSS/HTML Connector 的真实 Adapter。
- `src/loop_pilot/models/router.py` 目前只按 role 取单个 adapter id，并在未知 adapter 时回退到 `mock`；它还不是 `29-model-routing-and-runtime-policy.md` 中要求的能力、预算、deadline、数据等级、健康状态和 fallback 决策器。
- `config/models.yaml` 所有 role 都指向 `mock`，说明当前运行链不能被视为真实模型/CLI 工作流。
- `src/loop_pilot/runtime/orchestrator.py` 已负责创建 run、加锁、调用三条 Loop、保存 run 和 artifact manifest，并提供 Mini `run_all` 固定顺序；它尚未包含 V1 的 SQLite 事务检查点、恢复、审批状态回写和 scheduler 安装链。

因此 Mini 的边界必须保持清晰：

- 可以手动运行 `doctor`、`run`、`run all`、`status`、`inspect`。
- 可以用 JSON StateStore、JSONL 事件、Markdown 报告和 fixture 验证三条 Loop 的成功、阻塞、失败、耗尽语义。
- 可以证明 InternLoop、PaperLoop、DailyNewsLoop 的 Observe 到 Report 闭环。
- 不应该暴露 `resume`、`approve`、`reject`、`cancel` 的假实现。
- 不应该把 mock 结果包装成真实仓库修复、真实论文推进或真实新闻判断。
- 不应该修改或覆盖 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md`，该文件只保留 Mini 历史提示词。

## 2. V1/MVP 目标

> **新编号**：本节描述的「每天真实工作」完整能力对应 **0.4.0-daily-runner**，其实现依赖 **0.2**（配置与审阅）和 **0.3**（真实 Adapter）。勿将本节整体等同于单版本 0.3。

V1/MVP 的目标是“可用于每天真实工作”，而不是只在示例 fixture 中稳定。达到 **0.4.0-daily-runner**（旧称 V1/MVP 终点）时，用户应该能在 WSL 或本机环境中按日运行：

```bash
loop-pilot run daily-news
loop-pilot run intern
loop-pilot run paper
loop-pilot run all
loop-pilot resume <run-id>
loop-pilot approve <run-id>
loop-pilot reject <run-id> --reason "..."
loop-pilot cancel <run-id>
loop-pilot report <run-id>
```

V1/MVP 的用户价值是：

- DailyNewsLoop 读取真实但有限的数据源，生成高价值候选，并把可信候选路由到 Intern/Paper Inbox。
- InternLoop 能在真实仓库的批准 worktree 中选择一个有限任务，运行真实测试链，产出可审计 diff 和开发报告。
- PaperLoop 能在真实论文工作副本中推进一个明确缺口，保留引用/证据核验结果，无法核验时停止而不是编造。
- 每条 Loop 约 30 分钟硬停止，25 分钟工作、5 分钟收尾。
- 运行中断后可以恢复，重复触发不会重复写入或污染状态。

## 3. V1/MVP 为什么必须先做 Adapter + Router 层

> **新编号**：本节对应 **0.3.0-adapter-mvp**（Adapter + ModelRouter），在 **0.4** 每日调度之前完成。

V1/MVP 不能只把 Mini fixture 换成真实路径。必须先把 Adapter 和 ModelRouter 作为基础设施补齐，原因如下：

- 当前 `ModelRouter.resolve()` 只能返回 adapter id，无法判断 adapter 是否具备文件写入、Tool 调用、结构化输出、dry-run、上下文容量、网络能力和数据等级许可。真实 Intern/Paper/DailyNews 会直接依赖这些能力。
- `MockAdapter` 可以验证状态机和报告，但不能验证真实 CLI 进程超时、退出码、stdout/stderr、transcript、token/费用、网络失败、429/5xx、认证失败、Schema 修复和 fallback。
- 如果先写真实 Loop 业务逻辑而不抽象 Adapter，代码会把 Cursor CLI、API 模型、RSS/HTTP 源和业务阶段耦合在一起，后续很难满足 `19-adapter-specifications.md` 的“替换 Adapter 后 Loop 领域逻辑无需修改”。
- V1 的安全性依赖 Router 的硬过滤：无合格 `coding_agent` 时必须 BLOCKED，不能让普通聊天模型写 worktree；`SECRET` 永不进入模型；预算不足不能跳过 Policy 和事实检查。
- V1 的验收需要路由日志、候选排除原因、fallback 原因、调用指标和脱敏 Artifact。没有这些证据，每日报告无法审计，也无法判断真实失败是模型失败、Adapter 失败、Policy 阻塞还是业务证据不足。

结论：按 [33-version-roadmap.md](33-version-roadmap.md)，任务顺序应为 **0.3 Adapter 契约 + ModelRouter** → **0.4 SQLite/恢复/调度** → **0.5 PyPI/开源发布** → 真实 Intern、Paper、DailyNews 每日链对外可复现。历史文档曾将「状态底座」与 Adapter 并列写入 V1；现明确 SQLite 生产恢复属 **0.4**，Adapter 属 **0.3**，PyPI 与开源协作属 **0.5**。

## 4. V1/MVP 详细实施顺序

### 4.1 锁定 Mini 基线

- 跑通 Mini 的现有单元、集成和场景测试。
- 确认 `run all` 顺序仍为 DailyNews、Intern、Paper。
- 确认 Mini CLI 不出现 V1 命令占位。
- 将后续工作放入新文件和 V1 模块，不覆盖 Mini 提示词和 Mini 历史说明。

验收门槛：

- Mini 三条 Loop 仍能从 Observe 到 Report。
- `git diff --check` 无格式错误。
- `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md` 没有被本阶段改动。

不可做事项：

- 不把 V1 命令注册为空实现。
- 不把 mock 数据声明为真实结果。
- 不在 Mini JSON Store 中塞入 SQLite 专属字段。

### 4.2 StateStore/SQLite、migration 与事务检查点

> **新编号：0.4.0-daily-runner**（不属于 0.3 adapter-mvp）。

- 在 `src/loop_pilot/storage/` 增加 SQLite StateStore 和 migration 模块，保留现有 `StateStore` 接口。
- 设计 run、round、event、artifact manifest、approval、inbox、checkpoint 的最小表结构。
- 实现原子保存 run 状态、事件追加和 artifact manifest 索引。
- 增加显式 migration 命令或脚本，migration 必须可重复执行并记录版本。
- 增加 `scripts/backup_state.py` 和 `scripts/migrate_state.py` 的 dry-run/非 dry-run 行为。

验收门槛：

- JSON Store 的 Mini 测试继续通过。
- SQLite Store 覆盖成功、阻塞、失败、耗尽、非法状态恢复和事务失败。
- 中途异常不会产生半写 run 终态。

不可做事项：

- 不用 SQLite 取代 `StateStore` 接口。
- 不让配置中途修改影响正在运行的 Run。
- 不在 migration 中静默删除旧状态。

### 4.3 checkpoint/recovery、resume 与审批协议

> **新编号：0.4.0-daily-runner**

- 增加 `runtime/checkpoints.py`、`runtime/recovery.py`、`runtime/approvals.py`。
- 记录每个阶段的安全检查点：输入上下文、预算、Policy 约束、已完成 Tool/Adapter 调用、artifact 引用和下一步建议。
- 实现 `resume <run-id>`，只从合法 checkpoint 恢复。
- 实现 `approve`、`reject`、`cancel`，审批必须写入 SQLite 并成为后续 Policy 判断输入。
- 锁遗留、非法状态恢复、重复 resume 和过期 approval 都必须有明确错误语义。

验收门槛：

- 强制中断后可恢复，不重复写入 Artifact。
- approval/reject/cancel 可审计，报告能解释人工决定。
- 锁冲突不会破坏已存在 run。

不可做事项：

- 不允许 Agent 自行增加 Round 或修改 approval 状态。
- 不允许 resume 绕过 Policy Gate。
- 不允许把失败恢复成 PASS。

### 4.4 Adapter 契约与 MockAdapter 完整化

> **新编号：0.3.0-adapter-mvp**（Mock 完整化可在 0.1 部分落地；真实 Adapter 属 0.3）

- 抽出统一 Adapter 接口：`capabilities()`、`healthcheck()`、`execute()`、`estimate_cost()`、`normalize_error()`。
- 对齐 `AdapterResult` 字段：status、structured_output、stdout/stderr/transcript artifact、tool_calls、usage、error_code。
- 让 `MockAdapter` 支持 success、timeout、cancelled、invalid schema、rate limit、refusal、partial output、cost usage 等 fixture。
- 所有 Adapter 调用保存原始输出 Artifact，并执行敏感字段脱敏。

验收门槛：

- Mock fixture 可重复，覆盖 Adapter 验收场景。
- timeout/cancellation 不破坏状态。
- dry-run 不产生真实工作区写入。

不可做事项：

- 不让 Loop 直接依赖具体模型品牌。
- 不把原始 token、cookie、密钥写进报告。
- 不在 Adapter 内部决定业务 PASS。

### 4.5 ModelRouter 能力路由

> **新编号：0.3.0-adapter-mvp**

- 将 `models.yaml` 从简单 `roles` 迁移到逻辑 `model_roles` 与 `adapters` 配置，保留兼容读取仅限未发布分支内部重构，不做长期双轨。
- Router 按能力、数据等级、结构化输出、工具/文件写、健康状态、预算、deadline、独立评价要求硬过滤。
- Router 记录被排除候选和选择理由。
- 实现 fallback：同 role 已验证 adapter、筛选/摘要确定性降级、非强制扩展任务延后。
- 实现 BLOCKED：无强规划、无合格 coding、无可信引用核验、预算不足、安全检查不足。

验收门槛：

- 覆盖 `29-model-routing-and-runtime-policy.md` 的 ModelRouter 测试清单。
- `SECRET` 被拒绝，`SENSITIVE` 不发往未授权 Adapter。
- `coding_agent` 不会落到无文件能力模型。

不可做事项：

- 不用品牌名和主观强弱作为路由条件。
- 不因预算不足跳过安全检查。
- 不用搜索摘要替代引用全文核验。

### 4.6 真实 InternLoop 最小接入

- 增加真实仓库配置：workspace、default_branch、allowed_paths、forbidden_paths、validation 命令数组、权限开关。
- 实现 worktree 生命周期和用户未提交改动保护。
- 实现 CodingCLIAdapter 或等价 coding CLI Adapter，必须在批准 worktree 中运行。
- 实现测试链捕获、失败分类、diff review、敏感文件扫描和越界 diff 阻断。
- 任务选择顺序：用户明确任务、昨日遗留、真实失败，最后才是 DailyNews 候选。

验收门槛：

- 能在真实仓库解决一个有限任务，不污染主工作区。
- 测试通过但 diff 越界时不宣布成功。
- 依赖缺失时不擅自安装，输出 BLOCKED 或 NEEDS_APPROVAL。

不可做事项：

- 不自动 commit、push、PR 或部署。
- 不覆盖用户已有未提交改动。
- 不让 DevAgent 为自己的结果判定 PASS。

### 4.7 真实 PaperLoop 最小接入

- 增加论文 workspace、main_document、bibliography、read_only_paths、modifiable_sections、research_topics 配置。
- 实现论文工作副本和修订 diff。
- 实现引用 key 检查、BibTeX 去重、DOI/arXiv 稳定标识核验和 claim-evidence 映射。
- 实现 GapDiagnoser、WritingAgent、ResearchCritic 的最小契约和 Golden Cases。
- 证据不足时写 `SOURCE REQUIRED` 或 BLOCKED，不生成不存在的引用、数字或实验。

验收门槛：

- 能推进真实论文一个缺口并给出下一方向。
- 无法核验引用时停止，报告说明缺什么证据。
- 修订后重新评价并显示诊断变化。

不可做事项：

- 不自动跑昂贵实验。
- 不自动投稿。
- 不把 reviewer simulation 当硬分数。

### 4.8 DailyNews Inbox 与真实来源最小接入

- 增加来源配置：id、type、tier、enabled、endpoint、categories、rate_limit、cache_ttl、auth_env、parser、terms_checked。
- 实现 RSS/Atom、GitHub repository/release/security、论文元数据源的最小 Connector。
- 实现 ETag/Last-Modified/cursor/cache、规范 URL、内容哈希、跨来源去重和事件日期核验。
- 实现两个 Inbox：开发候选进入 Intern Inbox，研究候选进入 Paper Inbox；候选必须有过期时间、来源、置信度和路由理由。
- 第一次 GitHub 快照只建立基线，第二次以后才计算 star 增量。

验收门槛：

- 单源失败不终止主 Loop。
- 低置信度消息不进入正式 Top News 或 Inbox。
- 无重大新闻时输出空类别，不凑数。

不可做事项：

- 不做全网社交媒体抓取。
- 不做自动交易判断。
- 不用总 star 冒充 24 小时增长。

### 4.9 scheduler dry-run 与 OS 运行

> **新编号**：dry-run 可在 0.3 验证；**非 dry-run 调度安装属 0.4.0-daily-runner**。

- 增加 `scripts/install_scheduler.py`，先实现 `--dry-run` 打印 systemd timer、cron 或 Windows Task Scheduler/WSL 方案。
- 文档说明 WSL 推荐使用 systemd user timer 或 Windows Task Scheduler 调用 `wsl.exe`，二者只能选择一种作为当前机器主入口。
- scheduler 只触发 CLI，不绕过锁、预算、配置快照和 StateStore。

验收门槛：

- dry-run 不写系统计划任务。
- 重复安装不会创建重复任务。
- 调度触发和手动触发的 run 语义一致。

不可做事项：

- 不在 scheduler 中写业务逻辑。
- 不让多个调度器同时触发同一 Loop。
- 不把密钥写进调度命令。

### 4.10 `run all` 真实每日链

- 保持顺序执行：DailyNewsLoop、InternLoop、PaperLoop。
- 每条 Loop 独立预算，`run all` 只做编排和每日总报告聚合。
- 每日总报告顶部只回答：开发是否解决、论文推进了什么、外部最多三件事、需要用户做什么决定。
- `run all` 中某条 Loop BLOCKED/FAILED 不应抹掉其他 Loop 的结果。

验收门槛：

- 连续多次运行没有重复任务、锁死和状态污染。
- 成功、阻塞、失败报告均可读且事实正确。
- 每次约 30 分钟硬停止且保留收尾。

不可做事项：

- 不并发运行三条 Loop。
- 不让 DailyNews 直接创建正式主任务，必须经 Inbox 和 Orchestrator 校验。
- 不把每日报告写成无证据的信息罗列。

## 5. V2 目标与实施顺序

V2 的目标是扩大查询和验证能力，让系统从“可每天用”进化为“外部信息和引用验证更可靠”。V2 不应改变 V1 的安全边界，而应扩展 Connector、核验和回归覆盖。

实施顺序：

1. GitHub Connector 扩展：repository、release、issue、security advisory、star snapshot、增量排名和缓存修复工具。
2. 论文元数据扩展：arXiv、DOI/Crossref、Semantic Scholar/OpenAlex 等至少两个可配置来源，统一 SourceItem 和稳定标识。
3. 文献矩阵：记录 claim、source、证据位置、支持强度、冲突、引用 key 和更新时间。
4. 引用全文证据位置：从摘要候选升级到原文或可信全文片段核验；无法访问全文时降级为明确的不完整覆盖。
5. 新闻来源交叉核验：政治、财经和官方公告区分发生时间、发布时间、原始来源和转述来源。
6. 多模型质量/成本统计：按 role、agent golden case、失败率、延迟和费用记录，支持 fallback 观察期。
7. 故障注入与固定回归：覆盖断网、429/5xx、schema changed、SQLite 事务失败、锁遗留、测试进程挂起和工作区外部修改。

V2 验收门槛：

- “今日热门 GitHub”基于真实快照增量，而非总 star 猜测。
- 论文引用能追溯到稳定标识和支持位置。
- 重大新闻区分事实、推断、发生时间和发布时间。
- Connector 失败不会破坏主 Loop。
- 新 Adapter 先作为 fallback 观察，再提升为 primary。

V2 不可做事项：

- 不让更多来源绕过置信度、去重和原始来源核验。
- 不把搜索摘要当作正式证据。
- 不为了覆盖率引入无限来源和不可控成本。
- 不把模型质量统计写成品牌偏好。

## 6. V3 目标与实施顺序

V3 的目标是长期稳定运行和高质量决策。它关注跨日记忆、优先级解释、健康检查和历史诊断，而不是继续扩大抓取范围。

实施顺序：

1. 跨日问题链：把昨日 next action、用户反馈、失败诊断、审批决定和今天任务选择连接成可解释链路。
2. 优先级学习：基于用户规则、任务价值、历史阻塞、时间预算和证据强度调整候选排序；用户显式规则始终最高。
3. InternLoop 风险评估增强：更完整的回归、静态分析、diff 风险、依赖风险和可回滚建议。
4. PaperLoop Reviewer Simulation 增强：独立评价、实验设计建议、一致性追踪和研究方向演化。
5. 长期运行健康检查：StateStore 增长、Artifact 保留、缓存失效、锁清理、配置漂移、Adapter 成功率和费用趋势。
6. 历史诊断比较：今天的失败与过去类似失败对比，避免重复无效尝试。
7. 报告质量收敛：每日总报告突出“最重要的一件事”，细节进入可点击 run 报告和证据链。

V3 验收门槛：

- 连续运行期间无未解释外部写入、状态丢失和重复任务。
- 每日报告能准确说明最重要的一件事，而不是罗列信息。
- 历史证据能解释为什么今天选择当前任务和研究方向。
- 三条 Loop 的成功、阻塞和失败语义长期一致。

V3 不可做事项：

- 不让学习排序覆盖用户明确规则。
- 不把历史相似性当作无需验证的结论。
- 不引入自动部署、自动投稿、自动交易等高风险动作。
- 不为了“智能”降低可审计性。

## 7. 阶段验收总门槛

| 阶段 | 新编号 | 必须证明 | 不能进入下一阶段的情况 |
|---|---|---|---|
| Mini | **0.1.0-mini** | 三条 Loop 的 fixture 闭环、报告、状态和失败语义成立 | mock 被包装成真实能力；CLI 出现 0.4 假命令 |
| Practical | **0.2.0-practical-mvp** | 真实工作区配置、Markdown 审阅、报告契约 | 未 dry-run 即写入真实目录 |
| Adapter MVP | **0.3.0-adapter-mvp** | 真实 Adapter、Router live、受控写入、有限 Connector | 宣称 0.4 恢复/调度已验收 |
| Daily Runner | **0.4.0-daily-runner**（旧 V1 主体） | 每日运行；SQLite 恢复和审批可用 | 无合格 Adapter 仍宣称成功；中断不可恢复；状态污染 |
| Public Beta | **0.5.0-public-beta** | PyPI 可安装；init demo；文档与示例完整 | 包含密钥/私有路径；陌生人无法 10 分钟跑通 demo |
| V2（历史） | 拆入 0.3+/1.0 | 真实 Connector、引用核验、增量快照、多模型统计和故障注入稳定 | 来源失败破坏主 Loop；搜索摘要替代证据；成本不可控 |
| V3（历史） | **1.0.0-stable** | 长期运行、跨日决策解释、健康检查和历史诊断稳定 | 用户规则被学习排序覆盖；报告不可审计；重复任务无法解释 |

所有阶段共同要求：

- 所有单元和强制场景通过。
- 没有未解释的高严重度故障。
- 成功、阻塞、失败报告均可读且事实正确。
- 密钥和敏感信息扫描通过。
- `git diff --check` 通过。

## 8. WSL 部署/运行注意事项

推荐把 LoopPilot 的真实每日运行放在 WSL 内执行，尤其是需要 Python、pytest、Git worktree、CLI Adapter 和 Linux 风格路径时。

注意事项：

- 使用绝对 Linux 路径配置 workspace、state_dir、artifact_dir、checkpoint_dir，避免 Windows 路径和 WSL 路径混用。
- Windows 仓库路径如果通过 `/mnt/c/...` 访问，需确认文件权限、换行符、执行位和 Git 性能；长期运行更推荐把活跃工作区放在 WSL ext4 文件系统中。
- 模型/API 密钥只通过 WSL 环境变量或安全 secret 管理传入，配置文件只写 `auth_env` 名称，不写明文值。
- scheduler 只能有一个主入口：要么 WSL systemd/cron，要么 Windows Task Scheduler 调用 `wsl.exe --cd <workspace> loop-pilot run all`。
- 调度命令必须先激活项目虚拟环境或调用固定解释器路径，避免系统 Python 漂移。
- WSL 睡眠、网络恢复和 Windows 重启会造成中断，V1 必须依赖 checkpoint/recovery，而不是依赖进程常驻。
- 真实 Adapter 执行命令必须使用参数数组，不允许 shell 字符串拼接。
- 所有 artifact、日志和 SQLite 备份应保留在同一 WSL 文件系统或明确备份位置，避免跨文件系统半写。

## 9. Prompt 文件使用方式

Mini 历史提示词继续保留在 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md`，后续阶段使用独立文件：

- `prompts/CURSOR_V1_MVP_IMPLEMENTATION_PROMPT.md`
- `prompts/CURSOR_V2_IMPLEMENTATION_PROMPT.md`
- `prompts/CURSOR_V3_IMPLEMENTATION_PROMPT.md`

每个阶段开始前，先把对应 Prompt 复制给 Cursor Agent。阶段 Agent 必须先阅读本路线图和相关规范，再动手改代码。
