# 34 0.x 版本路线图（0.1 → 1.0）

> **与 [33-version-roadmap.md](33-version-roadmap.md) 的关系**：33 为 semver 标签与阶段边界的**权威索引**；本文提供 0.1–0.4 早期草案细节，并包含 **0.5 Public Beta / PyPI 完整规格**（2026-06-20 扩展）。semver 命名冲突时以 33 为准；0.5 实现清单以本文 §6 为准。

本文是 LoopPilot **对外版本命名**的路线图，取代简单使用 "V1/V2/V3" 作为阶段称呼的方式。

> **口径说明**：`09-versions.md` 与 `31-v1-v2-v3-implementation-roadmap.md` 保留历史语义与任务分解，但**阶段推进、对外沟通、验收门槛以本文 0.x 体系为准**。详见 [§10 Legacy 映射](#10-legacy-映射)。

## 1. 版本总览

| 版本 | 名称 | 核心能力 | 预估剩余工作量 | 预估工期 |
|------|------|----------|----------------|----------|
| **0.1** | Mini-MVP | 三条 dry-run Loop 跑通 | 还差 25–35% | 1–3 天 |
| **0.2** | Practical MVP | 受控真实 workspace，dry-run/report 为主 | 还差 45–55%（自当前） | 5–10 天 |
| **0.3** | Real Adapter MVP | Mock→Real Adapter，严格安全限制 | 还差 60–70%（自当前）；0.2→0.3 再加 25–30% | 1–2 周 |
| **0.4** | Daily Automation / Recovery | SQLite、恢复、审批、OS scheduling | 还差 10–20%（若 0.3 完成） | 3–4 周 |
| **0.5** | Public Beta / PyPI | 发布质量、安装体验、文档、开源协作 | 还差 15–25%（若 0.4 完成） | 1–2 周 |
| **1.0** | Stable personal production | 长期稳定个人生产 | — | — |

**当前聚焦**：完成 **0.1 Mini-MVP**，然后进入 **0.2 Practical MVP**。**不要现在冲 0.3**。

```
0.1 Mini-MVP ──► 0.2 Practical MVP ──► 0.3 Real Adapter MVP
                                              │
                                              ▼
                    0.4 Daily Automation ◄───┘
                              │
                              ▼
                    0.5 Public Beta / PyPI
                              │
                              ▼
                    1.0 Stable production
```

## 2. 0.1 Mini-MVP

### 2.1 目标

证明 LoopPilot 受控闭环在**离线 fixture** 下成立：编排、状态机、Policy Gate、Artifact Manifest、JSONL trace、Markdown 报告。

### 2.2 验收标准

- 三条 Loop（Intern / Paper / DailyNews）均能从 Observe 走到 Report。
- `loop-pilot doctor`、`pytest -q`、三条 `--dry-run` 及 `run all --fixture-set mini --dry-run` 通过。
- `runtime.allow_real_adapters: false` 默认生效；MockAdapter 为唯一可用 Adapter。
- JSON StateStore；无 `resume/approve/reject/cancel` 假命令。
- 失败时生成可读报告与 `error-traceback.txt`。

详见 [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md)。

### 2.3 禁止项

- 不把 mock 结果包装成真实仓库修复、论文推进或新闻判断。
- 不暴露 V1+ 命令占位或假成功。
- 不接入真实 Cursor CLI、API 模型、在线爬虫。

### 2.4 安全门槛

- 仅 MockAdapter；`allow_real_adapters` 默认 `false`。
- 敏感值脱敏；trace 不含密钥。

### 2.5 验收命令

```bash
python -m pip install -e ".[dev]"
loop-pilot doctor
pytest -q
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
loop-pilot status
```

---

## 3. 0.2 Practical MVP

### 3.1 目标

在**受控真实 workspace** 上验证 Loop 业务逻辑与报告链路；仍以 dry-run / report 为主，**不依赖 Real Adapter**。

用户应能：

- 配置真实 Intern 仓库路径、Paper 工作副本、DailyNews 离线/快照源。
- 在 allowlisted workspace 内观察、诊断、生成报告，但**默认不写入**或仅 `--allow-write` 显式开启有限写入。
- 验证 worktree 生命周期、路径边界、测试链调用（可 mock 模型输出）、引用/证据检查逻辑。

### 3.2 验收标准

- InternLoop：真实仓库 `--workspace` + `--dry-run` 或 `--allow-write` 有限任务，diff 越界时 BLOCKED。
- PaperLoop：真实论文副本，unsupported claim 时 `partial` / SOURCE REQUIRED，不编造引用。
- DailyNewsLoop：真实快照/离线源（非 live crawl），候选路由到 Intern/Paper Inbox。
- `run all` 在真实配置下顺序执行并聚合每日总报告。
- 配置 Schema 支持 workspace、allowed_paths、validation 命令数组。
- 全部 Mini 测试仍通过；新增 0.2 workspace 场景测试通过。

### 3.3 禁止项

- 不启用 Real Adapter（`allow_real_adapters` 仍为 `false`）。
- 不做 SQLite recovery、`resume/approve/reject/cancel`。
- 不做 OS 定时任务、PyPI 发布。
- 不 auto commit/push/PR/deploy。

### 3.4 安全门槛

- workspace 必须在 allowlist；PolicyEngine 拦截越界路径与危险命令。
- dry-run 默认不产生工作区写入。
- `--allow-write` 需显式传递且范围受 Policy 约束。

### 3.5 验收命令（示例）

```bash
loop-pilot doctor
loop-pilot run intern --workspace /path/to/repo --dry-run
loop-pilot run paper --workspace /path/to/paper --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --dry-run
```

---

## 4. 0.3 Real Adapter MVP（0.3.0-adapter-mvp）

> **重要**：0.3 ≠ 旧称 "V1"。0.3 是 V1-alpha 的**前置**，只解决 Mock→Real Adapter 与受控真实运行，**不包含** SQLite recovery、复杂审批、定时任务。

### 4.1 目标

在严格安全限制下，让 **Real Adapter 真正生效**，三条 Loop 可在受控环境中调用真实 Cursor CLI / OpenAI-compatible API，完成有限 Intern/Paper/DailyNews 任务。

### 4.2 核心模块清单

#### 4.2.1 Adapter 层

| 模块 | 说明 | 参考 |
|------|------|------|
| `BaseAdapter` 协议 | `capabilities()`、`healthcheck()`、`execute()`、`estimate_cost()`、`normalize_error()` | `19-adapter-specifications.md` |
| `MockAdapter` 完整化 | timeout、invalid schema、rate limit、usage、transcript | 现有 `mock_adapter.py` |
| `CodingCLIAdapter` | Cursor CLI（及可选 Codex/Claude Code 配置）；参数数组、超时、stdout/stderr artifact | `30-adapter-and-model-router-roadmap.md` §5 |
| `OpenAICompatibleAdapter` / `APIModelAdapter` | DeepSeek、OpenAI-compatible、Anthropic-compatible；结构化输出、脱敏 | 同上 |
| `AdapterRegistry` + factory | 按配置实例化；`allow_real_adapters=false` 时拒绝 cli/api 类 | 现有 `registry.py` |
| `adapters list` / `adapters doctor` CLI | 列出已注册 Adapter、健康检查 | 新增 CLI |

#### 4.2.2 ModelRouter

| 能力 | 说明 |
|------|------|
| 能力路由 | 按 tools、file write、structured output、network、context 过滤 |
| 数据等级 | `SECRET` 拒绝；`SENSITIVE` 不发往未授权 Adapter |
| 预算 / deadline | 硬过滤，不足时 BLOCKED |
| fallback | 同 role 备选 Adapter；记录排除原因 |
| 路由日志 | 候选、选择理由、fallback 原因写入 trace/artifact |

参考：`29-model-routing-and-runtime-policy.md`、`30-adapter-and-model-router-roadmap.md`。

#### 4.2.3 ToolBroker

| 能力 | 说明 |
|------|------|
| 文件读写 | allowlisted 路径；dry-run 模式 |
| Git / worktree | 生命周期、用户未提交改动保护 |
| 命令执行 | 白名单、超时、参数数组（无 shell 拼接） |
| HTTP 读取 | 有限 Connector；rate limit |
| 审计 | 每次 Tool 调用写入 trace；敏感字段脱敏 |

Agent 与 Loop **不得绕过 ToolBroker** 直接调用 shell 或文件 API。

#### 4.2.4 各 Loop 要求

**InternLoop**

- 真实仓库 + 批准 worktree + CodingCLIAdapter。
- 测试链捕获、diff review、越界 diff 阻断。
- 任务选择：用户任务 > 昨日遗留 > 真实失败 > DailyNews 候选。
- `--allow-write` 显式开启；默认 dry-run。

**PaperLoop**

- 真实论文 workspace；APIModelAdapter 用于 research/writing/evaluation role。
- 引用 key、BibTeX、DOI/arXiv 核验；claim-evidence 映射。
- 证据不足 → SOURCE REQUIRED / BLOCKED，不编造。

**DailyNewsLoop**

- `--real-sources`：RSS/Atom、GitHub snapshot、论文元数据（有限 Connector）。
- 去重、置信度、Inbox 路由；单源失败不终止主 Loop。
- 第一次 GitHub 快照建基线，第二次起算增量。

### 4.3 验收标准

- `loop-pilot adapters list` 显示 mock + 已配置 real adapters（未 enable 时标记 disabled）。
- `loop-pilot adapters doctor` 对 mock 返回 OK；对未配置密钥的 real adapter 返回明确 BLOCKED/WARN。
- `allow_real_adapters: false` 时，任何 cli/api adapter 调用被 Router/Registry 拒绝。
- `allow_real_adapters: true` + 显式 CLI flag 时，Intern/Paper/DailyNews 各完成至少一个受控真实 run。
- 全部 0.1/0.2 测试仍通过；新增 adapter/router/toolbroker 单元与集成测试通过。

### 4.4 验收命令（示例）

```bash
loop-pilot doctor
loop-pilot adapters list
loop-pilot adapters doctor
loop-pilot run intern --workspace ... --allow-write
loop-pilot run paper --workspace ... --allow-write
loop-pilot run daily-news --real-sources
loop-pilot run all --real-sources --allow-write-intern --dry-run-paper
```

### 4.5 0.3 明确不做

| 不做 | 归属版本 |
|------|----------|
| auto push / PR / deploy | 永不自动（个人工具边界） |
| SQLite recovery / `resume` | **0.4** |
| 复杂 approval 工作流 | **0.4** |
| Web UI | 非当前路线 |
| PyPI 发布 | **0.5** |
| OS 定时任务 / scheduler | **0.4** |
| 向量库 / RAG | 非 0.3 范围 |

### 4.6 安全门槛

- `runtime.allow_real_adapters` **默认 `false`**；启用需配置 + CLI 双重确认。
- PolicyEngine：路径、命令、diff、依赖、删除规则全部生效。
- `SECRET` / `SENSITIVE` 数据等级 enforced by Router。
- 所有 Adapter 调用：超时、取消、原始输出 artifact、脱敏。
- workspace allowlist；无 allowlist 则 BLOCKED。
- 真实 Adapter 命令使用参数数组，禁止 shell 字符串拼接。

### 4.7 实施顺序（0.3 内部）

1. BaseAdapter 协议 + MockAdapter 完整化
2. AdapterRegistry + `allow_real_adapters` 门控
3. ModelRouter 能力路由（非品牌路由）
4. ToolBroker 最小实现
5. CodingCLIAdapter（Cursor CLI 优先）
6. OpenAICompatibleAdapter
7. InternLoop 真实接入
8. PaperLoop 真实接入
9. DailyNewsLoop `--real-sources`
10. `adapters list/doctor` CLI + 集成测试

详细任务分解见 [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) §4.4–4.8（按 Legacy 映射阅读）。

---

## 5. 0.4 Daily Automation / Recovery

### 5.1 目标

让 LoopPilot 可**每天自动运行、中断可恢复、人工可审批**。

### 5.2 核心能力

- SQLite StateStore、migration、事务检查点。
- `resume`、`approve`、`reject`、`cancel`、`report` CLI。
- checkpoint/recovery、跨进程锁、审批协议。
- `scripts/install_scheduler.py`（dry-run + 实际安装）。
- `scripts/backup_state.py`、`scripts/migrate_state.py`。
- 每日 `run all` 真实链 + 总报告。

### 5.3 验收标准

- 强制中断后可 `resume`，不重复写入 Artifact。
- approval/reject/cancel 可审计。
- scheduler dry-run 不写系统任务；实际安装不重复。
- JSON Store Mini 测试仍通过；SQLite 场景全覆盖。

### 5.4 禁止项

- resume 不绕过 Policy Gate。
- 不允许 Agent 自行修改 approval 状态。
- scheduler 不写业务逻辑、不存密钥。

### 5.5 安全门槛

- 锁冲突有明确错误语义；非法状态恢复拒绝。
- 备份与 migration 可重复、可 dry-run。

参考：31 文档 §4.2、§4.3、§4.9、§4.10。

---

## 6. 0.5 Public Beta / PyPI（0.5.0-public-beta）

### 6.1 定位

**0.4 = 内部可用**（你自己每天稳定用：SQLite、recovery、scheduler、approval）。  
**0.5 = 外部可用**（别人也能安装、运行、理解、贡献：Public Beta / PyPI Release）。

0.5 **核心不是堆功能**，而是：

- 发布质量（wheel/sdist、manifest、版本纪律）
- 安装体验（`pip install`、5–10 分钟跑通 demo）
- 文档与示例（getting started、概念、安全边界）
- 开源协作（CONTRIBUTING、SECURITY、CoC、LICENSE、CHANGELOG）
- CI release 流水线（Trusted Publisher 优先）

建议版本名：

| 用途 | 标签 |
|------|------|
| Git tag / GitHub Release | `0.5.0-public-beta` 或 `0.5.0-pypi-beta` |
| PyPI 预发布 | `0.5.0b1`（PEP 440 beta） |

完整 semver 链：

```text
0.1.0-mini → 0.2.0-practical-mvp → 0.3.0-adapter-mvp
  → 0.4.0-recovery-and-automation → 0.5.0-public-beta → 1.0.0-stable
```

### 6.2 0.4 vs 0.5 对比

| 维度 | **0.4 recovery-and-automation** | **0.5 public-beta** |
|------|--------------------------------|------------------------|
| **受众** | 维护者本人（个人生产） | 外部用户、贡献者、早期采用者 |
| **分发** | 源码 / `pip install -e ".[dev]"` | **PyPI** `pip install loop-pilot` |
| **安装门槛** | 需 clone 仓库、读开发文档 | 5–10 分钟 quick start + `init demo` |
| **文档** | `docs/development/` 开发规格 | 开源 README + `docs/getting-started` + `docs/zh/` |
| **示例** | fixture / 个人 workspace | `examples/` 四套 demo |
| **CI** | `ci.yml`（lint + test + doctor） | + `release.yml`（build、twine、PyPI、GitHub Release） |
| **协作** | 可选 | CONTRIBUTING、SECURITY、CoC、LICENSE、CHANGELOG **必须** |
| **CLI 扩展** | resume/approve/reject/cancel | + `init`、`init demo`、`summary today` |
| **证明什么** | 每日长跑、中断可恢复、审批可审计 | 陌生人能复现 Mini demo、能 fork 并跑测试 |
| **不要求** | PyPI、CONTRIBUTING、公开 quick start | 商业化、SaaS、Web UI、插件市场、多用户 |

**一句话**：0.4 = 「我自己每天能可靠跑」；0.5 = 「别人能 pip 装上、看懂、贡献」。

### 6.3 必须实现（写入规格）

#### 6.3.1 PyPI 分发

- [ ] PyPI distribution 名：`loop-pilot`（与 CLI 一致）
- [ ] `pip install loop-pilot` 后 5–10 分钟内跑通 demo（见 §6.6 验收命令）
- [ ] `pyproject.toml` 声明正确的 entry point、`packages`、可选 extras（`dev`）
- [ ] 包内**不含** `outputs/`、`memory/`、`.env`、私有 workspace 路径、密钥

#### 6.3.2 `loop-pilot init`

- [ ] `loop-pilot init` — 在当前目录生成最小 `loop-pilot.yaml` + 目录骨架
- [ ] `loop-pilot init demo` — 生成 `loop-pilot-demo/` 目录结构，含 fixture 配置与示例说明
- [ ] init 产物默认 `allow_real_adapters: false`、`state_backend: json`（与 0.1 安全边界一致）

#### 6.3.3 GitHub Actions

- [ ] `.github/workflows/ci.yml` — ruff、pytest、doctor、dry-run 矩阵（0.1 基线不退化）
- [ ] `.github/workflows/release.yml` — tag/manual 触发：build wheel + sdist → `twine check` → PyPI upload → GitHub Release
- [ ] PyPI 上传优先 **Trusted Publisher**（OIDC）；备选 API token 仅用于本地调试

#### 6.3.4 README 与文档

- [ ] 根目录 **README 重写为开源 README**（英文主体 + 链到 `docs/zh/` 中文说明）
- [ ] 用户文档（新建）：
  - `docs/getting-started.md`
  - `docs/concepts.md`
  - `docs/configuration.md`
  - `docs/safety.md`
  - `docs/adapters.md`
  - `docs/loops/intern.md`
  - `docs/loops/paper.md`
  - `docs/loops/daily-news.md`

#### 6.3.5 示例目录

- [ ] `examples/intern_demo/` — InternLoop fixture 最小示例
- [ ] `examples/paper_demo/` — PaperLoop fixture 示例
- [ ] `examples/daily_news_demo/` — DailyNews 快照示例
- [ ] `examples/full_demo/` — `run all --fixture-set mini --dry-run` 一键演示

#### 6.3.6 开源协作文件

- [ ] `CONTRIBUTING.md` — 开发环境、分支、测试、PR 流程
- [ ] `SECURITY.md` — 漏洞报告渠道、敏感数据处理原则
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `LICENSE`（与仓库策略一致）
- [ ] `CHANGELOG.md` — Keep a Changelog 格式，与 tag 对齐

#### 6.3.7 包发布质量检查清单

发布前必须逐项通过：

- [ ] `python -m build` 成功，产出 wheel + sdist
- [ ] `twine check dist/*` 无错误
- [ ] `pipx install dist/*.whl`（或干净 venv）后 `loop-pilot doctor` OK
- [ ] 包内容审计：无 `outputs/`、`memory/`、`.env`、测试 artifact、`var/artifacts/` 残留
- [ ] 默认配置 `allow_real_adapters: false`
- [ ] 版本号与 CHANGELOG、Git tag、PyPI 一致

### 6.4 0.5 CLI 范围

| 命令 | 0.5 状态 | 说明 |
|------|----------|------|
| `init` / `init demo` | **新增** | 快速 bootstrap |
| `doctor` | 稳定 | 环境、配置、路径检查 |
| `run *` | 稳定 | 含 `run all --fixture-set mini --dry-run` |
| `status` | 稳定 | |
| `inspect` | 稳定 | |
| `adapters list` / `adapters doctor` | 稳定（0.3+） | 未配置 real adapter 时明确 WARN |
| `summary today` | **新增** | 每日总报告摘要（依赖 0.4 daily-summary） |
| `approve` / `reject` / `resume` / `cancel` | **stable 或 experimental** | 若 0.4 recovery 未完全稳定，文档与 `--help` 标 `experimental` |
| `report` | 同 approval 组 | |

### 6.5 明确不做（0.5）

| 排除项 | 说明 |
|--------|------|
| 商业化 / 付费 tier | 个人开源工具 |
| 云服务 / SaaS | 无托管运行 |
| 多用户 / 租户 | 单用户本地工具 |
| Web UI | 非当前路线 |
| 插件市场 | 归属 1.0+ 或永不 |
| 企业权限 / SSO | 非范围 |
| 自动 PR / deploy | 全版本禁止 |
| 向量库 / RAG | 非 0.5 |

### 6.6 验收命令

**外部用户路径（PyPI 安装）**：

```bash
pip install loop-pilot
loop-pilot init demo
cd loop-pilot-demo && loop-pilot doctor && loop-pilot run all --fixture-set mini --dry-run
```

**贡献者路径（源码）**：

```bash
git clone https://github.com/bosprimigenious/LoopPilot.git
cd loop-pilot && pip install -e ".[dev]" && pytest -q
```

**发布者路径（maintainer）**：

```bash
python -m build && twine check dist/*
# CI release.yml 绿；GitHub Release 附 wheel/sdist
```

**0.5 完成定义**：上述三组命令全部通过 + §6.3.7 检查清单勾选 + CHANGELOG 发布。

### 6.7 Release notes 模板

GitHub Release 与 CHANGELOG 条目使用以下结构：

```markdown
## [0.5.0b1] - YYYY-MM-DD

### Added
- PyPI distribution `loop-pilot` (beta)
- `loop-pilot init` / `loop-pilot init demo`
- User docs: getting-started, concepts, configuration, safety, adapters, loops/*
- Examples: intern_demo, paper_demo, daily_news_demo, full_demo
- CI release workflow (Trusted Publisher)

### Changed
- README rewritten for open-source quick start (EN + docs/zh/)

### Security
- Default `allow_real_adapters: false` unchanged
- Package excludes outputs/, memory/, .env

### Known limitations (beta)
- SQLite recovery commands may be marked experimental if 0.4 not fully stable
- No Web UI, no multi-user, no plugin marketplace

### Upgrade from 0.4.x
- pip install loop-pilot==0.5.0b1
- loop-pilot init demo  # optional fresh demo workspace
```

### 6.8 与 1.0 的区别

| | **0.5 public-beta** | **1.0 stable** |
|---|---------------------|----------------|
| 目标 | 可安装、可复现、可贡献 | 长期个人生产稳定 |
| 功能 | 打包 0.4 能力 + 文档/示例 | 跨日记忆、优先级解释、Connector 扩展 |
| 语义 | beta：API/CLI 可能小改 | stable：破坏性变更需 major |
| 验收 | 陌生人 10 分钟跑通 demo | 连续运行无状态污染、决策可审计 |
| 扩展 | 不做插件框架 | 可选插件/Connector 深化 |

0.5 是**对外发布的 beta**；1.0 是**对个人生产环境的长期承诺**。

### 6.9 安全门槛

- 包与示例中无密钥、无私有路径；`doctor` 对 WSL/Windows 路径混用 WARN。
- 默认 `allow_real_adapters: false`；real adapter 文档强调双重确认。
- SECURITY.md 定义 responsible disclosure 流程。
- release 流水线 OIDC 优先，不在 CI 日志中打印 token。

---

## 7. 1.0 Stable personal production

### 7.1 目标

长期稳定个人生产：跨日记忆、优先级解释、健康检查、历史诊断。

### 7.2 核心能力（对应旧 V2/V3 部分能力）

- 扩展 Connector：GitHub 增量、论文全文证据、新闻交叉核验。
- 多模型质量/成本统计、故障注入回归集。
- 跨日问题链、优先级学习（用户规则始终最高）。
- InternLoop 风险评估增强；PaperLoop Reviewer Simulation。
- 长期运行健康检查、Artifact 保留策略。
- 每日报告突出「最重要的一件事」。

### 7.3 验收标准

- 连续运行无未解释外部写入、状态丢失、重复任务。
- 历史证据可解释今日任务选择。
- 见 `09-versions.md` V2/V3 验收项（作为 1.0 子集逐步实现）。

---

## 8. 阶段推进规则

1. **顺序推进**：0.1 → 0.2 → 0.3 → 0.4 → 0.5 → 1.0；不可跳过未验收阶段。
2. **测试门禁**：每阶段全部强制场景通过才可进入下一阶段。
3. **文档先行**：新设计先改文档（本文 + 对应 spec），再改代码。
4. **Mini 基线不退化**：每阶段完成后 Mini/0.1 测试仍必须通过。
5. **提前开发允许**：独立组件可提前开发，但不得提前接入每日主运行链。

---

## 9. 与相关文档关系

| 文档 | 关系 |
|------|------|
| [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) | 0.1 验收记录 |
| [33-next-steps-0.2.md](33-next-steps-0.2.md) | 当前行动项：先 0.1 后 0.2 |
| [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md) | 0.5 规划决策日志 |
| [09-versions.md](09-versions.md) | Legacy 能力描述；冲突以本文为准 |
| [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) | Legacy 任务分解；见 §10 映射 |
| [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md) | 0.3 Adapter/Router 技术细节 |
| [25-mini-run-path.md](25-mini-run-path.md) | 0.1→0.3 最小路径 |

---

## 10. Legacy 映射

### 10.1 旧版本名 → 0.x

| 旧称呼 | 0.x 对应 | 说明 |
|--------|----------|------|
| Mini / Mini-MVP | **0.1** | 名称统一为 Mini-MVP = 0.1 |
| V1 / V1-MVP / V1-alpha | **0.2 + 0.3 + 0.4** | 旧 "V1" 被拆成三阶段；**0.3 ≠ V1** |
| V1 Adapter 接入 | **0.3** | Real Adapter MVP |
| V1 SQLite/recovery/scheduler | **0.4** | Daily Automation |
| V1 PyPI / 开源发布 / CONTRIBUTING | **0.5** | Public Beta；**不是 0.4** |
| V1 真实 workspace | **0.2**（无 real adapter）+ **0.3**（有 real adapter） | 分阶段 |
| V2 | **1.0 子集**（Connector/核验扩展） | 不单独称 0.6 |
| V3 | **1.0**（长期稳定/决策质量） | 合并进 1.0 |

### 10.2 旧文档 § 映射表

| 31 文档章节 | 0.x 阶段 |
|-------------|----------|
| §4.1 锁定 Mini 基线 | 0.1 |
| §4.6 真实 InternLoop | 0.2（workspace）+ 0.3（real adapter） |
| §4.7 真实 PaperLoop | 0.2 + 0.3 |
| §4.8 DailyNews 真实来源 | 0.2（快照）+ 0.3（`--real-sources`） |
| §4.2 SQLite/migration | 0.4 |
| §4.3 checkpoint/recovery/approval | 0.4 |
| §4.4 Adapter 契约 | 0.3 |
| §4.5 ModelRouter | 0.3 |
| §4.9 scheduler | 0.4 |
| §4.10 run all 真实每日链 | 0.4 |
| §4.11 PyPI / 开源 README / examples | **0.5** |
| §5 V2 | 1.0 子集 |
| §6 V3 | 1.0 |

### 10.3 旧 Prompt 文件映射

| Prompt 文件 | 建议对应阶段 |
|-------------|--------------|
| `CURSOR_MINI_IMPLEMENTATION_PROMPT.md` | 0.1（历史，勿覆盖） |
| `CURSOR_V1_MVP_IMPLEMENTATION_PROMPT.md` | 0.2–0.4（按章节拆分使用） |
| `CURSOR_V2_IMPLEMENTATION_PROMPT.md` | 1.0 Connector 扩展 |
| `CURSOR_V3_IMPLEMENTATION_PROMPT.md` | 1.0 长期稳定 |

### 10.4 与 09-versions.md 的冲突处理

`09-versions.md` 将 V1 描述为「SQLite + 真实 workspace + OS 定时」的合体。新口径：

- **0.2** 负责「真实 workspace + dry-run/report」。
- **0.3** 负责「Real Adapter + 受控真实运行」。
- **0.4** 负责「SQLite + recovery + approval + scheduler」。
- **0.5** 负责「PyPI + 开源文档 + 示例 + release CI + 协作文件」。

阅读 `09-versions.md` 时请按上表拆分理解；架构与安全原则不变，仅**发布粒度**更细。

---

## 11. 完成度与时间估计（2026-06-20 基线）

| 里程碑 | 估计剩余 | 说明 |
|--------|----------|------|
| 到 0.1 | 25–35% | Mini-MVP 八项任务大部分完成，见 32 文档 |
| 到 0.2 | 45–55% | 含 workspace 配置、真实路径验证 |
| 到 0.3 | 60–70% | 含全部 Adapter/Router/ToolBroker |
| 0.2 → 0.3 增量 | 25–30% | 主要在 Adapter 层与真实调用 |
| 到 0.4 | 75–85%（自当前） | 含 SQLite、recovery、scheduler；0.3→0.4 约 22–32 人日 |
| 到 0.5 | **80–90%** | **若 0.4 完成，到 0.5 还差 15–25%**；主要是打包、文档、示例、release |
| 0.1 工期 | 1–3 天 | |
| 0.2 工期 | 5–10 天 | 在 0.1 完成后 |
| 0.3 工期 | 1–2 周 | 在 0.2 完成后 |
| 0.4 工期 | 3–4 周 | 在 0.3 完成后 |
| 0.5 工期 | 1–2 周 | 在 0.4 完成后；**不堆功能，重发布质量** |
