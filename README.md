# LoopPilot

> Loop Engineering Ecosystem 的运行时层：受控 AI 工作闭环、可审计产物、默认安全。

> **当前状态（2026-06-21）：0.4.0b1 stabilization in progress。** 0.4-d summary/schedule 实现存在，但 Full 0.4 因全量回归失败、0.4-c 未完成、migration v3 冲突及失败路径审计缺口而 **NOT READY**。权威补救计划见 [0.4 Stabilization and Truthful Acceptance](docs/development/50-0.4-stabilization-and-truthful-acceptance.md)。

**LoopPilot** is a controlled runtime for loop-engineered personal AI workflows. It runs development, research, and information loops with explicit safety gates, auditable artifacts, and reproducible dry-run workflows.

English interface spec: [docs/en-core.md](docs/en-core.md)

---

## 30 秒理解

LoopPilot 不是聊天机器人，也不是普通定时脚本。

它是一个面向个人长期使用的 **AI 工作闭环运行时**：

```text
Observe → Plan → Act → Check → Evaluate → Report → Review
```

当前默认使用：

```text
MockAdapter + dry-run + ToolBroker + trace + report
```

真实模型、真实 CLI、真实 API 都需要**显式开启**。

### Loop Engineering Ecosystem

```text
LoopPilot
  Runtime Layer
  负责运行、编排、记录、恢复、审阅

agentic-rubric-runner
  Evaluation Layer
  负责评分、审计、benchmark、发布门禁
```

**LoopPilot 负责「跑」，agentic-rubric-runner 负责「判」。**

未来无人值守模式必须经过 **evaluation gate**，而不是让模型自己宣布成功。

---

## 三条核心 Loop

| Loop | 做什么 | 当前状态 |
|------|--------|----------|
| **InternLoop** | 解决一个开发问题，运行测试，生成工程报告 | 支持 fixture / demo dry-run；ToolBroker 已接入 |
| **PaperLoop** | 推进一个论文缺口，检查证据，生成修订报告 | 支持 fixture / demo dry-run；工作区读写经 ToolBroker |
| **DailyNewsLoop** | 从离线快照筛选高价值信号，生成 candidate-actions | 支持 demo source profile；**显式** `inbox import-daily-news` 导入 Inbox（0.4-b） |

> **说明：** Inbox / Queue / Today 属于 **0.4 Personal Daily Loop**。0.3 阶段 DailyNewsLoop 主要生成 `candidate-actions.json` 和报告产物。

---

## 当前版本状态

**当前主线版本：`0.3.0b1`**

| 版本 | 状态 | 说明 |
|------|------|------|
| **0.1** Mini MVP | ✅ Completed | fixture dry-run，三条 Loop 最小回归 |
| **0.2** Practical MVP | ✅ Completed | demo workspace / demo profile 可运行 |
| **0.3.0a1** Adapter Safety Alpha | ✅ Completed | Adapter gate、blocked trace、CI verify |
| **0.3.0b1** ToolBroker Beta | ✅ Completed automated acceptance | ToolBroker 全 Loop 强制、自动化验收通过；**live run 仍为 MANUAL** |
| **0.4** Personal Daily Loop | 🔄 In progress | 0.4-a/b 已交付；0.4-d 已实现；**0.4-c 阻塞** Full 0.4 |
| **0.5** Safe Autonomy | 📋 Spec drafted; impl paused | SafetyGate → schedule `--yes` → `run daily --unattended --safe`（无 daemon）；**等 0.4-c** — [docs](docs/development/50-personal-daily-loop-0.5-spec.md) |
| **0.6+** Real Adapter Long Run | 📋 Planned | Cursor CLI / Codex / DeepSeek 长期运行与预算控制 |
| **1.x** | 📋 Planned | 1.0 个人稳定 → 1.1 智能 → 1.2 协作 → 1.3 团队 preview |

详细路线图：

- [docs/zh/03-版本路线图.md](docs/zh/03-版本路线图.md)
- [docs/development/34-version-roadmap-0x.md](docs/development/34-version-roadmap-0x.md)

---

## 当前能做什么 / 不能做什么

### 适合

- 个人本地 demo
- 个人项目 dry-run
- 开发任务受控分析
- 论文任务受控分析
- DailyNews 离线信号筛选
- 生成 trace / report / tool-results
- 验证 ToolBroker 和 Adapter gate

### 不适合直接做

- 无人值守每日自动运行
- 自动 commit / push / deploy
- 真实 API 长期调用
- 自动 approve / reject / resume
- 生产级个人任务 OS

这些属于 **0.4 / 0.5 之后**的能力。

---

## 快速开始

### 安装开发环境

```bash
pip install -e ".[dev]"
python scripts/bootstrap_local.py   # optional, first time only
loop-pilot doctor
pytest -q
```

### 运行 0.1 fixture 回归

```bash
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
```

### 运行 0.2 demo workspace

```bash
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
```

### 运行 0.3 Adapter 探测

默认情况下，真实 Adapter 会被拦截：

```bash
loop-pilot adapters list
loop-pilot adapters doctor

loop-pilot run intern \
  --workspace examples/intern_demo \
  --adapter cursor_cli \
  --dry-run
```

预期结果：

- `blocked`
- `allow_real_adapters=false`
- `adapter-call-trace.jsonl` generated

真实 Adapter 需要显式开启：

```bash
loop-pilot run paper \
  --workspace examples/paper_demo \
  --adapter deepseek \
  --allow-real-adapters \
  --dry-run
```

> **注意：** DeepSeek / Cursor CLI controlled live run 仍属于 **MANUAL 验收层**，不在默认 CI 中运行。

---

## 安全模型

LoopPilot **默认安全**。

### 默认策略

- 不自动 commit
- 不自动 push
- 不自动 deploy
- 不自动 approve
- 不读取 `.env`
- 不提交 API key
- 真实 Adapter 默认 disabled
- 所有工具动作必须经过 **ToolBroker**

### ToolBroker 负责

- file read / write
- git / worktree
- command execution
- HTTP fetch
- audit log
- dry-run enforcement
- blocked reason

相关文档：

- [SECURITY.md](SECURITY.md)
- [docs/development/37-adapter-safety-policy.md](docs/development/37-adapter-safety-policy.md)
- [docs/development/38-toolbroker-design.md](docs/development/38-toolbroker-design.md)

---

## 核心产物

每次 Loop 运行会生成可审计产物。

| 文件 | 说明 |
|------|------|
| `artifact-manifest.json` | 本次运行所有产物索引 |
| `tool-results.json` | ToolBroker 调用记录 |
| `adapter-call-trace.jsonl` | Adapter 调用和 blocked 记录 |
| `patch.diff` | InternLoop 可能生成的补丁 |
| `proposed-revision.md` | PaperLoop 可能生成的修订稿 |
| `candidate-actions.json` | DailyNewsLoop 输出的候选行动 |
| `review-required.md` | 需要人工审阅的事项 |
| `next-actions.md` | 下一步建议 |
| `report.md` | Loop 总结报告 |

**0.4 之后会引入：**

- SQLite StateStore
- run status
- review queue
- `daily-summary.md`
- `recovery-scan`

---

## Runtime Phases

LoopPilot 的长期目标是将每次运行拆成稳定阶段：

```text
START
  ↓
PREFLIGHT
  ↓
RECOVERY_SCAN
  ↓
LOAD_CONTEXT
  ↓
PLAN
  ↓
ACT
  ↓
CHECK
  ↓
EVALUATE
  ↓
REPORT
  ↓
REVIEW_REQUIRED / DONE / BLOCKED
```

原则：

- 执行阶段不自己宣布成功
- 评估阶段判断是否达标
- 审阅阶段决定是否继续
- 无人值守必须经过 gate

---

## 0.4 Personal Daily Loop

0.4 让 LoopPilot 从「能跑 Loop」升级为「**个人每日任务 OS**」。

> **0.4 不是无人值守。** 无人值守属于 **0.5 Unattended Safe Mode**。

### 四个子阶段

| 阶段 | 目标 | 不做什么 |
|------|------|----------|
| **0.4-a** | 状态可靠：SQLite、migration、backup、verify、recovery-scan | 不做 Inbox / Scheduler |
| **0.4-b** | 任务入口：Inbox、Queue、Today | ✅ 已交付（2026-06-21） |
| **0.4-c** | 个人审阅：review、approve、reject、defer、cancel、resume | 不做无人值守 |
| **0.4-d** | 每日总结与调度预览：summary、schedule dry-run | 不默认安装定时任务 |

### 0.4-a 目标命令

```bash
loop-pilot db status
loop-pilot db migrate --dry-run
loop-pilot db migrate
loop-pilot db verify
loop-pilot db backup --dry-run
loop-pilot recovery-scan
```

> 需要 `runtime.state_backend=sqlite`。默认 `json` 后端保持 0.1 回归不变。

### 0.4-b 已交付命令

```bash
loop-pilot inbox add "fix login test" --source manual --loop intern --priority 2
loop-pilot inbox list
loop-pilot inbox archive <inbox-id>
loop-pilot queue promote <inbox-id> --loop intern
loop-pilot queue list
loop-pilot queue demote <queue-id>
loop-pilot today
loop-pilot today add <inbox-id>
loop-pilot today add-queue <queue-id>
loop-pilot inbox import-daily-news --from var/artifacts/daily-news/<run-id>/candidate-actions.json [--dry-run]
```

> DailyNews **不会**自动导入 Inbox；必须显式 `import-daily-news`。

### 0.4-c 目标命令

```bash
loop-pilot review list
loop-pilot approve <run-id>
loop-pilot reject <run-id> --reason "needs more tests"
loop-pilot defer <run-id> --until 2026-06-25
loop-pilot cancel <run-id>
loop-pilot resume <run-id>
loop-pilot report <run-id>
```

### 0.4-d 目标命令

```bash
loop-pilot summary today
loop-pilot summary week
loop-pilot schedule print
loop-pilot schedule install --dry-run
```

详细规格：[docs/development/40-personal-daily-loop-0.4-spec.md](docs/development/40-personal-daily-loop-0.4-spec.md)

---

## Unattended Roadmap

**无人值守不是 0.4-a 的功能。**

推荐路线：

```text
0.4-d
  schedule print
  schedule install --dry-run
  run daily --dry-run

0.5
  run daily --unattended --safe
  schedule install --yes
  unattended status
  unattended disable

0.6+
  real Adapter long-run
  budget control
  notification
  external evaluation gate
```

无人值守安全模式必须满足：

- 全局锁
- SQLite backup
- `db verify`
- `recovery-scan`
- ToolBroker enforced
- budget limit
- timeout limit
- summary report
- review queue
- no auto commit
- no auto push
- no auto deploy
- no auto approve

---

## Evaluation with agentic-rubric-runner

| 层 | 项目 | 职责 |
|----|------|------|
| Runtime | **LoopPilot** | 运行、编排、记录、恢复、审阅 |
| Evaluation | **[agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner)** | 评分、审计、benchmark、unattended gate、发布门禁 |

### LoopPilot 生成

- reports
- traces
- tool-results
- adapter-call-trace
- artifact-manifest
- candidate-actions

### agentic-rubric-runner 用于

- 评分
- 审计
- benchmark
- unattended gate
- 发布门禁

### 计划中的集成

```bash
agentic-rubric eval-run \
  --profile looppilot-intern \
  --out var/artifacts/intern/<run-id>

agentic-rubric eval-run \
  --profile looppilot-paper \
  --out var/artifacts/paper/<run-id>

agentic-rubric eval-run \
  --profile looppilot-daily-news \
  --out var/artifacts/daily-news/<run-id>
```

未来输出：

- `agent_eval.json`
- `agent_eval_report.md`
- `score_gate.json`

gate 结果：`pass` / `needs_review` / `blocked`

---

## CLI Reference

| Command | 说明 |
|---------|------|
| `loop-pilot doctor` | 环境与配置检查 |
| `loop-pilot run intern` | 运行 InternLoop |
| `loop-pilot run paper` | 运行 PaperLoop |
| `loop-pilot run daily-news` | 运行 DailyNewsLoop |
| `loop-pilot run all` | 运行组合 Loop |
| `loop-pilot adapters list` | 查看 Adapter |
| `loop-pilot adapters doctor` | 检查 Adapter |
| `loop-pilot db ...` | 0.4-a 状态管理 |
| `loop-pilot inbox ...` | 0.4-b 任务入口 |
| `loop-pilot queue ...` | 0.4-b 队列管理 |
| `loop-pilot today` | 0.4-b 今日任务 |
| `loop-pilot review ...` | 0.4-c 审阅 |
| `loop-pilot summary ...` | 0.4-d 总结 |
| `loop-pilot schedule ...` | 0.4-d 调度预览 |

---

## 命名规范

| 用途 | 名称 |
|------|------|
| 产品 / 项目 | **LoopPilot** |
| CLI / PyPI | `loop-pilot` |
| Python 包 | `loop_pilot` |

不要使用未分隔的小写 `looppilot`。

---

## 文档入口

| 读什么 | 去哪 |
|--------|------|
| 日常中文理解 | [docs/zh/README.md](docs/zh/README.md) |
| 英文接口规格 | [docs/en-core.md](docs/en-core.md) |
| 开发文档索引 | [docs/development/README.md](docs/development/README.md) |
| 0.x 版本路线图 | [docs/development/34-version-roadmap-0x.md](docs/development/34-version-roadmap-0x.md) |
| 0.2 验收 | [docs/development/35-practical-mvp-0.2-acceptance.md](docs/development/35-practical-mvp-0.2-acceptance.md) |
| 0.3 验收 | [docs/development/36-adapter-mvp-0.3-acceptance.md](docs/development/36-adapter-mvp-0.3-acceptance.md) |
| 0.3 安全策略 | [docs/development/37-adapter-safety-policy.md](docs/development/37-adapter-safety-policy.md) |
| ToolBroker 设计 | [docs/development/38-toolbroker-design.md](docs/development/38-toolbroker-design.md) |
| 0.4 个人每日 Loop | [docs/development/40-personal-daily-loop-0.4-spec.md](docs/development/40-personal-daily-loop-0.4-spec.md) |
| 开发计划 | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) |

---

## Development

```bash
git clone https://github.com/bosprimigenious/LoopPilot.git
cd LoopPilot

python -m pip install -e ".[dev]"
python scripts/bootstrap_local.py
loop-pilot doctor
pytest -q
ruff check .
```

---

## CI / Acceptance

当前主线验收口径：

```bash
pytest -q
ruff check .
python scripts/verify_0_3_acceptance.py
loop-pilot run all --fixture-set mini --dry-run
loop-pilot run all --profile demo --dry-run
```

**0.3.0b1 验收结果（2026-06-21）：**

| 检查项 | 结果 |
|--------|------|
| `pytest -q` | ✅ 157 passed |
| `python scripts/verify_0_3_acceptance.py` | ✅ 20/20 PASS |
| `ruff check .` | ✅ PASS |
| `loop-pilot adapters list` | ✅ PASS |
| `loop-pilot adapters doctor` | ✅ PASS |

> Controlled live run（Cursor CLI / DeepSeek API）不在默认 CI 中；需 MANUAL 验收。

---

## Security Notes

不要提交 `.env`、API key、模型密钥、生产配置或私有 workspace。

真实 Adapter 必须显式开启：

```bash
--allow-real-adapters
```

涉及真实写入时还需要额外确认：

```bash
--allow-write
```

默认行为应该是：

- dry-run
- mock
- blocked by default
- auditable artifacts
- human review required

---

## License

Apache-2.0.
