# Cursor V1/MVP Implementation Prompt (_legacy)

> **Legacy prompt — do not use for current work without version confirmation.**  
> - **Current focus (2026-06):** 0.3 → use [CURSOR_0.3_ADAPTER_MVP_PROMPT.md](CURSOR_0.3_ADAPTER_MVP_PROMPT.md)  
> - **Doc system:** [docs/zh/05-文档体系说明.md](../docs/zh/05-文档体系说明.md) · [docs/en-core.md](../docs/en-core.md)

> **遗留文件名说明**  
> 本文件名为历史「V1/MVP」保留，**不代表当前应实现的单一版本**。  
> - **近 term 顺序**：`0.1.0-mini`（已完成）→ `0.2.0-practical-mvp`（已完成）→ `0.3.0-adapter-mvp`（进行中）  
> - **0.3 ≠ 旧称 V1**：0.3 只证明真实 Adapter 安全可用  
> - **0.4.0-daily-runner** = 旧文档「V1」主体（SQLite、恢复、`resume`/`approve`、OS 调度）  
> 权威编号见 `docs/development/33-version-roadmap.md`。实施前确认目标版本，勿一次性实现全文范围。

## 目标（中文，Legacy V1 范围 — 现对应 0.4+）

本文件描述的是**旧 V1/MVP 全集**（含 SQLite、审批、调度）。当前仓库尚未到达该阶段；若只需 Adapter，请改用 0.3 prompt。

---

你是 Cursor Agent，在仓库 [bosprimigenious/LoopPilot](https://github.com/bosprimigenious/LoopPilot) 中继续实现 LoopPilot。请使用中文沟通，代码和文档保持现有风格，符合 lint/format 要求。

## Scope

本阶段目标是把 Mini 从 fixture 闭环推进到 V1/MVP：可用于每天真实工作。V1/MVP 必须支持真实但有限的 InternLoop、PaperLoop、DailyNewsLoop，每条 Loop 约 30 分钟预算，具备 SQLite 状态、事务检查点、恢复、审批、真实 Adapter、能力路由、真实 worktree/论文工作副本、DailyNews Inbox、scheduler dry-run 和 `run all` 每日链。

必须保护 Mini 历史：

- 不要修改、覆盖或重写 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md`。
- 不要把 Mini mock 能力包装成真实能力。
- Mini CLI 仍只暴露已实现命令；`resume`、`approve`、`reject`、`cancel` 从 V1 开始，不能做空占位或假成功。

本阶段不要实现 V2/V3 的扩展来源、长期学习排序、复杂健康分析或自动化高风险动作。

## Read Before Coding

编码前必须阅读并对齐这些文件：

- `docs/development/09-versions.md`
- `docs/development/10-testing-and-acceptance.md`
- `docs/development/11-daily-operation.md`
- `docs/development/12-development-work-breakdown.md`
- `docs/development/14-implementation-manifest.md`
- `docs/development/19-adapter-specifications.md`
- `docs/development/23-human-review-protocol.md`
- `docs/development/24-configuration-spec.md`
- `docs/development/28-agent-development-guide.md`
- `docs/development/29-model-routing-and-runtime-policy.md`
- `docs/development/31-v1-v2-v3-implementation-roadmap.md`
- `src/loop_pilot/adapters/mock_adapter.py`
- `src/loop_pilot/models/router.py`
- `src/loop_pilot/runtime/orchestrator.py`
- `config/models.yaml`

如果发现文档冲突：

- 架构以 `docs/development/01-architecture.md` 为准。
- 运行流程以 `docs/development/02-runtime-mechanism.md` 为准。
- 版本范围以 `docs/development/09-versions.md` 为准。
- 是否完成以 `docs/development/10-testing-and-acceptance.md` 为准。
- V1/MVP 执行顺序以 `docs/development/31-v1-v2-v3-implementation-roadmap.md` 为准。

## First Response Before Edits

在改文件前，先用中文回复：

1. 你已阅读哪些文档和代码。
2. 当前 Mini 边界是什么。
3. 本轮准备实现 V1/MVP 的哪一个小切片。
4. 预计修改哪些文件。
5. 准备运行哪些测试。

不要在第一次回复中直接大范围改代码。先确认工作切片足够小，能独立测试和回滚。

## Implementation Target

按以下依赖顺序推进，不要跳步：

1. 锁定 Mini 基线：跑现有测试，确认 `run all`、报告和 Mini CLI 没有退化。
2. SQLite StateStore：新增 `src/loop_pilot/storage/sqlite.py`、`src/loop_pilot/storage/migrations.py` 和对应测试，保留 `StateStore` 接口。
3. checkpoint/recovery/approvals：新增 `runtime/checkpoints.py`、`runtime/recovery.py`、`runtime/approvals.py`，实现合法恢复、审批状态回写和锁遗留处理。
4. Adapter 契约：抽出统一接口，扩展 `MockAdapter` 的 result、usage、artifact、timeout、cancelled、invalid schema、rate-limit、refusal 和 dry-run 场景。
5. ModelRouter 能力路由：实现能力、数据等级、结构化输出、工具/文件写、健康状态、预算、deadline、fallback 和 BLOCKED 决策。
6. 真实 InternLoop 最小接入：worktree 生命周期、用户改动保护、CodingCLIAdapter、测试链、diff review、敏感文件扫描和越界阻断。
7. 真实 PaperLoop 最小接入：论文工作副本、引用 key/BibTeX/DOI/arXiv 核验、claim-evidence 映射、缺证据停止。
8. DailyNews Inbox：真实有限来源、缓存/游标、去重、事件日期核验、两个 Inbox、GitHub star 快照基线。
9. scheduler dry-run：新增幂等安装/打印脚本，不写密钥，不绕过 CLI。
10. `run all` 每日链：顺序运行三条 Loop，保留单 Loop 失败/阻塞事实，并生成每日总报告。

每次只做一个可测试切片。不要一次性大改三条 Loop。

## CLI / Config

V1/MVP 允许新增或完善：

- `loop-pilot resume <run-id>`
- `loop-pilot approve <run-id>`
- `loop-pilot reject <run-id> --reason "..."`
- `loop-pilot cancel <run-id>`
- `loop-pilot report <run-id>`
- `scripts/install_scheduler.py --dry-run`
- `scripts/backup_state.py`
- `scripts/migrate_state.py`

配置要求：

- 命令必须是参数数组，不允许未经解析的 shell 字符串。
- 密钥只写环境变量名称，例如 `auth_env`，不写明文值。
- `models.yaml` 应表达逻辑 role、adapter 候选、能力要求和 fallback 策略。
- `loop-pilot.yaml` 需要明确 state、artifact、checkpoint、timezone、dry_run 和并发限制。
- Intern/Paper/DailyNews 配置必须保留路径、预算、权限和来源边界。

## Tests

每个切片必须配套测试。优先补齐这些测试：

- SQLite Store：事务成功、事务失败、非法状态恢复、migration 幂等、artifact manifest 索引。
- Recovery：强制中断恢复、重复 resume、锁遗留、过期 approval、cancel 后不可继续。
- Adapter：Mock success/timeout/cancelled/invalid schema/rate limit/refusal/dry-run/脱敏。
- Router：capability hard filter、fallback、BLOCKED、SECRET 拒绝、SENSITIVE 未授权拒绝、coding role 不落到无文件写 adapter。
- Intern：用户未提交改动保护、worktree 隔离、测试失败诊断、diff 越界阻断、依赖缺失审批。
- Paper：缺引用停止、DOI/arXiv 核验、证据冲突请求人工决定、修订后评价变化。
- DailyNews：多来源去重、事件日期和发布时间区分、第一次 GitHub 快照不声称增量、单源失败隔离。
- CLI：V1 命令真实回写状态，不是假成功。

完成前至少运行：

```bash
pytest -q
git diff --check
```

如果测试太慢，先运行相关子集，再说明未运行的完整测试和原因。

## Discipline

- Agent、Tool、Connector、ModelAdapter 的边界不能混淆。
- Orchestrator 是确定性控制层，不写具体代码修改、论文写作或网页抓取逻辑。
- Agent 不能直接调用另一个 Agent，不能直接实例化 ModelAdapter，不能绕过 Tool Broker。
- Worker 不能为自己的结果判定 PASS。
- Report Agent 不能改写运行事实。
- 无合格 Adapter 时必须 BLOCKED，而不是降低标准。
- 搜索摘要不能替代引用全文核验。
- 预算不足不能跳过安全、Policy 和事实检查。
- 不自动 commit、push、PR、部署、投稿或交易。
- 不覆盖用户未提交改动。
- 不提交，不 push，除非用户明确要求。

## Completion Report

完成一个切片后，用中文报告：

- 修改的文件。
- 本切片实现了哪些 V1/MVP 能力。
- Mini 是否保持兼容，特别说明 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md` 未被修改。
- 运行的测试和结果。
- 未运行的测试及原因。
- 已知风险、下一步建议和是否可以进入下一个 V1/MVP 切片。
