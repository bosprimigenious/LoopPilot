# 33 版本路线图（0.1 — 1.0）

本文是 LoopPilot **权威版本编号与阶段边界**。所有新文档、Prompt、Issue 和 PR 描述应优先使用本文的 semver 标签（`0.1.0-mini`、`0.2.0-practical-mvp` 等），而不是历史称呼「V1」「V2」。

> **关键澄清：0.3 ≠ V1。**  
> 旧文档中的「V1/MVP」混合了 Adapter 接入、真实工作区、SQLite 恢复和 OS 调度。新编号将其拆分为 **0.2（实用配置）→ 0.3（真实 Adapter）→ 0.4（恢复与自动化）→ 0.5（公开测试）→ 0.6（插件生态）→ 0.7（评测基准）→ 0.8（团队协作）→ 0.9（RC）→ 1.0（稳定 API）**。  
> 详见 [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) 顶部的历史映射说明。

## 当前工程焦点

**0.1.0-mini（Mini-MVP，Phase A）** 是当前唯一应推进的实现阶段。0.2–1.0 均为**文档规划**；在完成 Phase A 验收清单前，不得把 0.3+ 能力接入每日主运行链，也不得把未验收代码标称为更高版本。

验收细节见 [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md)。

---

## 版本总览

| 版本 | 代号 | 一句话目标 | 旧称呼映射 |
|---|---|---|---|
| **0.1.0-mini** | Mini-MVP | 本地脚手架 + 三条 dry-run Loop + MockAdapter only | Mini |
| **0.2.0-practical-mvp** | Practical MVP | 真实工作区配置、真实报告、Markdown 人工审阅 | V1 前半（配置与报告） |
| **0.3.0-adapter-mvp** | Adapter MVP | 真实 Adapter、ModelRouter 上线、受控写入、真实数据源 | 旧「V1」中的 Adapter 层（**不是 V1**） |
| **0.4.0-recovery-and-automation** | Recovery & Automation | SQLite、恢复、审批、调度、daily-summary | **旧文档所称「V1」的主体** |
| **0.5.0-public-beta** | Public Beta | PyPI、文档、示例、CI 发布 | 无直接旧称 |
| **0.6.0-plugin-ecosystem** | Plugin Ecosystem | 可扩展框架：Loop/Skill/Connector/Adapter 插件 | 无直接旧称 |
| **0.7.0-evaluation-benchmark** | Evaluation Benchmark | 本地 benchmark、指标、模型对比、Golden Case | 无直接旧称（亦称 loop-eval） |
| **0.8.0-team-cloud-preview** | Team Collaboration | 多项目 RBAC、共享审批、本地 Dashboard | 无直接旧称 |
| **0.9.0-release-candidate** | Release Candidate | API/配置/文档冻结、compat 与 migration 门禁 | 无直接旧称 |
| **1.0.0-stable** | Stable | **生产就绪稳定承诺**：API、配置、迁移、安全、长跑、文档 | V3 长期稳定子集 |

```text
0.1 mini ──> 0.2 practical ──> 0.3 adapter ──> 0.4 recovery ──> 0.5 beta ──> 0.6 plugins ──> 0.7 eval ──> 0.8 team ──> 0.9 RC ──> 1.0 stable
   ↑ 当前焦点              证明真实 Adapter           每日长跑+恢复        可安装        可扩展        可评测        本地协作      接口冻结      稳定承诺
```

### 0.3 vs 0.4 一句话

| 版本 | 证明什么 | 典型触发方式 |
|---|---|---|
| **0.3** adapter-mvp | 真实 Adapter **能安全跑通**（手动 `run`、受控写入、审计 Artifact） | 开发者手动执行 |
| **0.4** recovery-and-automation | **长跑系统**能每日自动运行、中断可恢复、人工可审批、状态不污染 | OS 调度 + `run all` + `resume` |

---

## 0.1.0-mini — Mini-MVP

### 目标

证明 LoopPilot 的受控闭环在本地可安装、可测试、可 CI 验证，**不连接真实外部系统**。

### 范围（必须）

- 本地 `pip install -e ".[dev]"` 可运行。
- CLI：`doctor`、`run`、`run all`、`status`、`inspect`。
- 三条 Loop 的 **dry-run** fixture 路径：Intern、Paper、DailyNews。
- `MockAdapter` 为唯一默认 Adapter；`runtime.allow_real_adapters=false`。
- JSON / JSONL 简化状态（`StateStore` 接口，非 SQLite 生产路径）。
- pytest 单元、集成、场景测试；GitHub Actions CI。
- 失败可生成可读 Markdown 报告与 `error-traceback.txt` Artifact。

### 验收命令

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

### 安全门

- `allow_real_adapters` 默认 `false`；`ModelRouter` 与 `adapters/registry.py` 阻止 cli/api 类真实 Adapter 未经显式开启。
- 不暴露 `resume`、`approve`、`reject`、`cancel` 的假实现或占位成功。
- 不把 mock 结果包装成真实仓库修复、论文推进或新闻判断。

### 不可做（0.1）

- 不实现真实 Cursor/OpenAI/DeepSeek Adapter 的每日主链接入。
- 不实现 SQLite 生产恢复、OS 调度安装、PyPI 发布。
- 不自动 commit、push、PR、deploy。
- 不修改 `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md` 中的 Mini 历史正文（可追加附录，不覆盖）。

---

## 0.2.0-practical-mvp — Practical MVP

### 目标

在仍 **safety-first、dry-run 为主** 的前提下，让用户配置真实工作区路径、阅读真实结构的报告，并通过 Markdown 完成人工审阅闭环。

### 范围（必须）

- 真实 Intern / Paper **workspace 配置**（路径、允许/禁止目录、验证命令声明）。
- 报告模板与产物契约对齐真实目录结构（仍可在 dry-run 下生成）。
- **人工审阅 via Markdown**：报告内嵌或链接审阅指令、决策记录字段（不强制 SQLite 审批状态机）。
- 配置 Schema 与 `24-configuration-spec.md` 对齐的可编辑示例。
- 继续默认 `allow_real_adapters=false`；真实 Adapter 调用仍属 0.3。

### 验收方向

- 用户可在配置中指向真实仓库与论文副本，dry-run 产出报告路径与字段正确。
- 人工可在 Markdown 报告中完成 accept/reject 记录（文件级或 sidecar），无需 `loop-pilot approve` CLI。
- Mini 验收命令仍全部通过。

### 安全门

- 无合格 Policy / dry-run 时不得写入真实 worktree。
- 配置中的密钥只写 `auth_env` 名，不写明文。

### 不可做（0.2）

- 不把真实 Adapter 标称为已验收的每日能力。
- 不实现 SQLite 事务检查点与 `resume` 生产路径。
- 不安装 OS 计划任务。
- 不发布 PyPI。

---

## 0.3.0-adapter-mvp — Real Adapter MVP

### 目标

**安全地证明真实 Adapter 与 ModelRouter 可用**——在受控写入、显式开启和审计 Artifact 下，接入真实模型/CLI 与有限外部数据源。

> **这不是旧称「V1」。** 0.3 只证明「真实 Adapter 能安全跑通」，不证明「每天自动恢复与调度」。

### 范围（必须）

- `CursorCLIAdapter`（或等价 `CodingCLIAdapter` 配置）。
- `OpenAICompatibleAdapter` / `APIModelAdapter`（含 DeepSeek 等兼容端点）。
- `ModelRouter` **live**：能力过滤、健康检查、fallback 记录、预算/deadline 硬门。
- `ToolBroker`：Loop/Agent 不直接实例化 Adapter。
- **受控写入**：仅在批准 worktree / 论文副本内、经 Policy 与 diff 审查。
- 真实 **有限** 数据源：GitHub、arXiv、RSS 等 Connector 最小集（配置化、可降级）。
- `allow_real_adapters=true` 为显式 opt-in；默认仍为 false。

### 验收方向

- Mock 与真实 Adapter 的 fixture/集成测试分离；真实测试需 env 与 `allow_real_adapters`。
- Router 日志含候选排除原因；`SECRET` 永不进入模型。
- 单源失败不终止主 Loop；证据不足时 BLOCKED，不编造。

### 安全门

- 无合格 `coding_agent` 时 Intern 写操作 BLOCKED。
- 命令白名单、参数数组执行、敏感字段脱敏 Artifact。
- 真实 Adapter 调用保存 stdout/stderr/transcript 原始 Artifact。

### 不可做（0.3）— 明确排除

以下能力 **不属于 0.3**，留待 0.4 或更晚：

| 排除项 | 归属版本 |
|---|---|
| 自动 push / PR / deploy | 永不自动（全版本） |
| SQLite 生产恢复与跨进程锁 | **0.4** |
| `resume` / `approve` / `reject` / `cancel` CLI 生产语义 | **0.4** |
| Web UI | 不在路线图核心 |
| PyPI 发布 | **0.5** |
| OS 调度安装（非 dry-run） | **0.4** |
| 长期跨日优先级学习 | **1.0** 方向 |

---

## 0.4.0-recovery-and-automation — Recovery & Automation

**版本标签**：`0.4.0-recovery-and-automation`（亦称 daily-runner；与 0.3 adapter-mvp 严格区分）

### 定位

| | **0.3 adapter-mvp** | **0.4 recovery-and-automation** |
|---|---|---|
| 核心问题 | 真实 Adapter 是否安全可用？ | 系统能否**每天长跑**且可恢复？ |
| 状态存储 | 可仍用 JSON；SQLite 非必须 | **SQLite 生产路径** + 事务检查点 |
| CLI | `run` / `status` / `inspect` | + `resume` `approve` `reject` `cancel` `report` `pending` `recovery-scan` `summary today` |
| 调度 | 无 | OS 调度 print/install（先 dry-run） |
| 旧称 | 常被误并入「V1」 | **旧称「V1」= 0.4，不是 0.3** |

### 目标

证明 LoopPilot 可作为**个人每日长跑系统**：OS 可触发、`run all` 可串联三 Loop、进程中断后可恢复、人工审批可审计、重复运行不污染状态，并产出 `daily-summary.md` 总报告。

依赖 **0.3** 已验收的真实 Adapter；0.4 不重复发明 Adapter 契约，只把 0.3 能力纳入持久化运行与恢复语义。

### 仓库内既有 WIP（归属 0.4，非 0.1/0.2/0.3）

以下文件来自早期误标为「V1」的工作，**应映射到 0.4 里程碑**，在完成 0.1 Phase A 前不得宣称已验收：

| 路径 | 当前状态 | 0.4 目标 |
|---|---|---|
| `src/loop_pilot/storage/sqlite.py` | 部分实现 `runs` / `checkpoints` / `reviews` / `artifact_manifests` | 扩展为完整表集 + 事务 |
| `src/loop_pilot/storage/migrations.py` | schema v1 最小表 | 增量 migration 至目标 schema |
| `src/loop_pilot/runtime/checkpoints.py` | 阶段边界 checkpoint 写入 | 与 recovery 规则对齐 |
| `src/loop_pilot/runtime/recovery.py` | `build_recovery_plan` 雏形 | ACTING 中断默认 BLOCKED 等完整规则 |
| `src/loop_pilot/runtime/approvals.py` | approve/reject/cancel 雏形 | 与 `approvals` 表、过期策略对齐 |
| `src/loop_pilot/reporting/daily_summary.py` | 渲染入口雏形 | 满足 daily-summary 契约 |
| `scripts/install_scheduler.py` | print/preview only | dry-run 优先，再可选 install |
| `scripts/backup_state.py` / `migrate_state.py` | 脚本骨架 | 可重复、可 dry-run |
| `src/loop_pilot/cli.py` | `resume`/`approve`/… 需 `state_backend=sqlite` | 扩展 pending/history/recovery-scan/summary |

0.1 默认 `state_backend=json` 时上述 CLI **不得**对 Mini 用户暴露假成功；仅当显式启用 SQLite 后端时注册 0.4 命令。

---

### SQLite StateStore 表（目标 schema）

所有表通过 `schema_migrations` 版本化管理；migration 必须可重复执行。`StateStore` 接口保持不变，JSON Store 为 0.1 默认实现。

| 表 | 用途 | 关键字段（示意） |
|---|---|---|
| **runs** | Run 主记录 | `run_id` PK, `loop_type`, `phase`, `outcome`, `payload` JSON, `config_snapshot_hash`, `started_at`, `finished_at`, `updated_at` |
| **rounds** | 每 Run 多轮记录 | `round_id` PK, `run_id` FK, `round_index`, `phase`, `payload`, `created_at` |
| **artifacts** | Artifact 索引 | `artifact_id` PK, `run_id` FK, `kind`, `relative_path`, `content_hash`, `created_at` |
| **approvals** | 审批请求与决定 | `approval_id` PK, `run_id` FK, `status` (pending/approved/rejected/expired), `reason`, `requested_at`, `decided_at`, `expires_at` |
| **events** | 追加审计事件 | `event_id` PK, `run_id` FK, `event_type`, `payload` JSON, `created_at` |
| **adapter_calls** | Adapter 调用审计 | `call_id` PK, `run_id` FK, `adapter_id`, `model_role`, `status`, `usage` JSON, `artifact_refs`, `created_at` |
| **candidate_actions** | DailyNews 路由候选 | `action_id` PK, `run_id` FK, `target_loop`, `source_item_id`, `priority`, `reason`, `recommended_action`, `expires_at` |
| **checkpoints** | 恢复检查点（保留） | `checkpoint_id` PK, `run_id` FK, `phase`, `payload`, `created_at` |
| **schema_migrations** | 版本追踪 | `version` PK, `applied_at` |

**WIP 差距**：当前 migration v1 仅有 `runs`、`checkpoints`、`reviews`（应演进为 `approvals`）、`artifact_manifests`（应演进为 `artifacts`）；`rounds`、`events`、`adapter_calls`、`candidate_actions` 待 0.4 补齐。

事务要求：run 终态、checkpoint、approval 决定、artifact 索引在同一逻辑单元内提交或回滚，避免半写终态。

---

### Checkpoint / Recovery 规则

依据 [18-state-transition-spec.md](18-state-transition-spec.md) §6 与 [08-security-and-recovery.md](08-security-and-recovery.md)：

1. **进入可恢复阶段前写 checkpoint**：`POLICY_CHECK`、`WAITING_APPROVAL`、每轮 `ACTING` 开始前（若 store 支持 V1/0.4 特性）。
2. **ACTING 中断 → 默认 BLOCKED**：进程被 kill、超时、机器休眠或子进程挂起时，**不得**假设动作未发生；恢复扫描必须检查文件、Git 状态、子进程与外部副作用。
3. **恢复决策树**：
   - 无副作用证据 + checkpoint `resume_allowed=true` → 可从 checkpoint **resume**。
   - 存在部分副作用或不确定 → **BLOCKED**，写入 `terminal_reason`，要求 `approve` 后人工决定或 `cancel`。
   - `WAITING_APPROVAL` 且未 approve → 不可 resume；过期 approval → BLOCKED 并释放锁。
   - 已 `SUCCEEDED` / 已 `CANCELLED` → 不可 resume。
4. **resume 不绕过 Policy Gate**：恢复后重新进入合法 phase，不得从 `CREATED` 直跳 `ACTING`。
5. **不重复写入 Artifact**：同一 `content_hash` 的 artifact 不重复落盘；resume 复用已有引用。
6. **recovery-scan**：CLI 扫描 `phase != TERMINATED` 或 `outcome IS NULL` 的 run，输出可恢复/需人工/应清理建议。

---

### CLI（0.4 范围）

| 命令 | 必须 | 说明 |
|---|---|---|
| `loop-pilot resume <run-id>` | ✅ | 从最新合法 checkpoint 恢复；非法则明确错误 |
| `loop-pilot approve <run-id>` | ✅ | `WAITING_APPROVAL` → 允许继续 |
| `loop-pilot reject <run-id> --reason "..."` | ✅ | 终止为 BLOCKED，可审计 |
| `loop-pilot cancel <run-id> [--reason]` | ✅ | 用户取消，释放锁 |
| `loop-pilot report <run-id>` | ✅ | 摘要 + 是否可 resume |
| `loop-pilot pending` | 可选 | 列出待审批 run |
| `loop-pilot history [--limit N]` | 可选 | 近期 run 与 outcome |
| `loop-pilot recovery-scan` | 可选 | 扫描中断/遗留 run |
| `loop-pilot schedule print` | ✅ | 打印调度配置（不写系统） |
| `loop-pilot schedule install --dry-run` | ✅ | 预览安装命令/脚本 |
| `loop-pilot schedule install --yes` | 后期 | 实际注册任务（单一 OS 入口） |
| `loop-pilot summary today` | ✅ | 生成/刷新当日 `daily-summary.md` |

所有 0.4 命令要求 `runtime.state_backend=sqlite`（或等价配置）；0.1 JSON 后端下应拒绝并提示版本边界。

---

### OS 调度

**第一阶段仅 print / install dry-run**；实际注册需显式 `--yes` 且文档警告。

| 平台 | 预览输出 | 安装目标 |
|---|---|---|
| **Windows** | Task Scheduler XML / PowerShell `Register-ScheduledTask` 预览 | 每日触发 `loop-pilot run all`（经 venv 固定解释器） |
| **WSL** | `cron` 行或 `systemd` user timer unit 预览 | 推荐 ext4 路径；`wsl.exe --cd <workspace> loop-pilot run all` |
| **Linux (native)** | `systemd` timer + service 预览 | user-level timer，不存密钥 |

约束：

- 调度**只触发 CLI**，不写业务逻辑、不绕过锁/预算/配置快照。
- 全机**只有一个主调度入口**（Windows Task Scheduler **或** WSL systemd/cron，二选一）。
- `scripts/install_scheduler.py` 与 `loop-pilot schedule` 语义一致；默认 `--dry-run`。

---

### 长跑安全（Long-running safety）

| 机制 | 要求 |
|---|---|
| **跨进程锁** | 同 `loop_type` 同时仅一个活跃 run；锁文件或 SQLite 锁表；遗留锁可 `recovery-scan` 清理 |
| **健康检查** | `doctor` 报告 state_backend、锁目录、SQLite 可写、调度配置一致性 |
| **预算** | 30 分钟硬停止；软截止后禁止新 `ACTING`；`WAITING_APPROVAL` 不计入执行预算 |
| **Stale 清理** | 超过 `recovery.stale_run_ttl` 的非终止 run 标记为 BLOCKED 或进入人工队列 |
| **配置快照** | run 开始时固化 `config_snapshot_hash`；运行中改配置不影响在途 run |
| **备份** | `scripts/backup_state.py` 支持 dry-run；定期备份 SQLite 与 `var/artifacts` 索引 |

---

### daily-summary.md 要求

路径：`var/artifacts/daily/<YYYY-MM-DD>/daily-summary.md`（或与 `07-data-and-reports.md` 对齐的 `var/artifacts/daily/` 约定）。

必须包含：

1. **今日最重要结论**（最多 3 条，程序渲染，非模型臆造）。
2. **InternLoop**：是否解决昨日问题、验证状态、待 review diff 链接。
3. **PaperLoop**：推进的缺口、证据状态（含 SOURCE REQUIRED）、下一方向。
4. **DailyNews**：重大条目摘要（可空）、路由到 Inbox 的候选数。
5. **等待人工处理**：`WAITING_APPROVAL` / BLOCKED 项及 `loop-pilot pending` 可行动命令。
6. **明日优先**：来自 checkpoint 或 inbox 的推荐（标注置信度）。
7. **元数据**：日期、`run all` 涉及的 run_id 列表、总耗时、Adapter 调用次数与费用摘要（若可用）。

`loop-pilot summary today` 在 `run all` 完成后自动调用或手动刷新；某 Loop FAILED/BLOCKED 不得抹掉其他 Loop 结果。

---

### 模块清单（0.4）

| 模块 | 路径 | 职责 |
|---|---|---|
| `sqlite_store` | `src/loop_pilot/storage/sqlite.py` | SQLite StateStore 实现 |
| `migrations` | `src/loop_pilot/storage/migrations.py` | schema 版本与 DDL |
| `checkpoints` | `src/loop_pilot/runtime/checkpoints.py` | 阶段边界 checkpoint |
| `recovery` | `src/loop_pilot/runtime/recovery.py` | recovery plan、ACTING 中断策略 |
| `approvals` | `src/loop_pilot/runtime/approvals.py` | approve/reject/cancel、过期 |
| `scheduler` | `scripts/install_scheduler.py` + CLI `schedule` | 调度 print/install |
| `daily_summary` | `src/loop_pilot/reporting/daily_summary.py` | 日总报告渲染 |

配套脚本：`scripts/backup_state.py`、`scripts/migrate_state.py`。

---

### 配置 Schema 增补（`loop-pilot.yaml`）

```yaml
runtime:
  state_backend: json          # 0.1 默认；0.4 生产设为 sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
  checkpoint_dir: var/checkpoints

schedule:
  enabled: false               # 0.4 先 dry-run，再 true
  platform: auto               # windows | wsl | systemd | cron
  daily_at: "09:00"
  command: loop-pilot run all
  timezone: Asia/Shanghai

approvals:
  default_ttl_minutes: 1440    # 审批过期 → BLOCKED
  require_reason_on_reject: true

recovery:
  stale_run_ttl_hours: 72
  acting_interrupt_default: blocked   # acting 中断默认 outcome
  scan_on_startup: true
```

0.1 配置不含上述段或保持默认值；启用 SQLite 即视为进入 0.4 开发/验收模式。

---

### 验收标准（10 项）

1. **SQLite 事务**：强制中断后无半写 run 终态；migration 可重复。
2. **ACTING 中断**：注入中断后 run 为 BLOCKED（默认），`recovery-scan` 可见，`resume` 拒绝或需 approve。
3. **resume**：合法 checkpoint 可恢复且不重复 artifact。
4. **approve / reject / cancel**：状态回写 SQLite，`report` 与 `trace.jsonl` 可审计。
5. **审批过期**：超时未批复 → BLOCKED，锁释放。
6. **run all 每日链**：DailyNews → Intern → Paper；单 Loop 失败不抹掉其他结果。
7. **daily-summary.md**：`summary today` 产出满足上文七段结构。
8. **schedule dry-run**：`schedule print` / `install --dry-run` 不写系统任务。
9. **0.1 基线不退化**：`state_backend=json` 时 Mini 验收命令仍全部通过。
10. **锁与 stale**：重复触发不产生双 run；stale run 可识别并清理。

### 推荐验收命令

```bash
# 0.4 验收前：启用 sqlite 后端（专用配置或 overlay）
loop-pilot doctor                                    # 应提示 sqlite + recovery 能力
pytest tests/unit/test_sqlite_state_store.py -q
pytest tests/integration/test_v1_recovery.py -q

loop-pilot run all
loop-pilot pending
loop-pilot recovery-scan
loop-pilot resume <run-id>                           # 合法 checkpoint
loop-pilot approve <run-id>
loop-pilot reject <run-id> --reason "needs more evidence"
loop-pilot cancel <run-id>
loop-pilot report <run-id>
loop-pilot summary today
loop-pilot schedule print
python scripts/install_scheduler.py --dry-run

# 0.1 回归（json 后端）
pytest -q
loop-pilot run all --fixture-set mini --dry-run
```

---

### 不可做（0.4）

| 排除项 | 归属 |
|---|---|
| Web UI | 非核心路线 |
| PyPI 发布 | **0.5.0-public-beta** |
| 自动 push / PR / deploy / 投稿 / 交易 | 全版本禁止 |
| 向量库 / RAG / multi-user | 非 0.4 |
| 跨日优先级学习 | **1.0.0-stable** |
| 把 0.3 未验收 Adapter 接入调度主链 | 先完成 0.3 |
| 在 0.1 JSON 默认配置下注册假成功 recovery 命令 | 违反 0.1 边界 |

---

### 工作量估算（人日，单人兼职）

| 工作包 | 估算 | 说明 |
|---|---|---|
| Schema + migrations 扩展 | 3–5 | rounds/events/adapter_calls/candidate_actions/approvals |
| Checkpoint + recovery 规则落地 | 4–6 | ACTING 中断、recovery-scan |
| Approvals + CLI 完整化 | 3–4 | pending/history、过期 |
| Orchestrator 与 SQLite 集成 | 4–5 | 事务、锁、run all |
| daily-summary | 2–3 | 模板 + summary today |
| Scheduler print/dry-run | 2–3 | 三平台预览 |
| 集成测试 + 故障注入 | 4–6 | 对齐 10 项验收 |
| **合计** | **22–32** | 假设 0.3 已验收 |

---

### 0.4 vs 0.5 区分

| | **0.4 recovery-and-automation** | **0.5 public-beta** |
|---|---|---|
| 受众 | **个人**生产长跑 | **外部**可安装试用 |
| 分发 | 源码 / editable install | **PyPI** `pip install loop-pilot` |
| 文档 | 开发文档 + 个人部署笔记 | 公开 quick start、示例、changelog |
| CI | test + lint | + **release** workflow |
| 能力 | SQLite、恢复、调度、daily-summary | 打包 0.4 能力并版本化发布 |
| 不要求 | PyPI、官网、CONTRIBUTING | multi-user、SaaS、Web UI |

0.4 = 「我个人每天能可靠跑」；0.5 = 「别人能 pip 装上复现」。

### 安全门（摘要）

- 锁冲突、非法 resume、过期 approval 有明确错误语义。
- WSL/Windows 路径混用需在 `doctor` 警告。
- 备份与 migration 可 dry-run；不在调度命令中写密钥。

---

## 0.5.0-public-beta — Public Beta

### 目标

外部可安装、可阅读、可复现的公开测试版。

### 范围（必须）

- PyPI distribution：`loop-pilot`。
- 发布文档、快速开始、示例配置与 fixture 说明。
- CI：**release** 工作流（tag 触发或 manual）、版本号与 changelog 纪律。
- 与 0.4 recovery-and-automation 能力对齐的验收矩阵公开化。

### 不可做（0.5）

- 不宣称 multi-user、SaaS、Web UI 为稳定能力。
- 不在发布流水线中写入密钥。
- 不实现插件注册表、在线市场或第三方自动安装（属 **0.6**）。

---

## 0.6.0-plugin-ecosystem — Plugin Ecosystem

**版本标签**：`0.6.0-plugin-ecosystem`（亦称 extension-system）

### 一句话

LoopPilot 从「可安装的每日工具」进化为「**可扩展框架**」——他人可在不 fork 核心的前提下，以本地插件形式添加 Loop、Skill、Connector、ModelAdapter、Tool、Agent 与报告模板。

### 定位：0.5 vs 0.6 vs 1.0

| | **0.5 public-beta** | **0.6 plugin-ecosystem** | **1.0 stable** |
|---|---|---|---|
| 核心问题 | 别人能否 `pip install` 并复现？ | 别人能否**安全扩展**而不改核心？ | 扩展 API 是否**长期稳定**？ |
| 分发 | PyPI 包 + 文档 + CI release | + 插件清单、脚手架、`plugins list` | semver 承诺 + 弃用周期 |
| 扩展性 | 仅内置三条 Loop | **本地插件**注册与启用 | 稳定 Protocol + 实验性分层 |
| 市场 | 无 | **无在线市场**（本地 only） | 仍无自动第三方安装 |
| 受众 | 外部试用者 | 贡献者 / 高级用户 | 个人长期生产 |

0.5 = 能装上跑；0.6 = 能插上扩展；1.0 = 扩展契约冻结且可依赖。

---

### 插件类型

| 类型 | 说明 | 注册目标 |
|---|---|---|
| **Loop** | 完整 Observe→Report 闭环（新 `loop_type`） | `Orchestrator` loop registry |
| **Skill** | 可复用阶段能力（规划、诊断、摘要等） | Skill registry |
| **Connector** | 外部数据源（RSS、API、爬虫适配） | Connector registry |
| **ModelAdapter** | 新模型/CLI/API 后端 | `AdapterRegistry` + `ModelRouter` |
| **Tool** | 受 Policy 约束的可调用工具 | `ToolBroker` |
| **Agent** | 声明 `model_role` 与阶段契约的角色 | Agent registry |
| **Report Template** | Markdown/Jinja 报告片段或整页模板 | `ReportRenderer` template map |

内置 Intern / Paper / DailyNews 在 0.6 中视为**一等插件**（bundled），与第三方本地插件使用同一 manifest 与加载路径。

---

### 插件 Manifest Schema

每个插件在包根或 `plugins/<name>/` 下提供 `loop-pilot-plugin.yaml`（或 `pyproject.toml` `[project.entry-points."loop_pilot.plugins"]` 等价物）。

```yaml
name: my-daily-research-loop          # 唯一 id（小写、连字符）
version: 0.1.0                        # semver，与 loop-pilot requires 对齐
type: loop                            # loop | skill | connector | model_adapter | tool | agent | report_template
entrypoint: my_plugin.loop:MyLoop     # module:callable 或 module:Class
requires:
  loop_pilot: ">=0.6.0,<0.7.0"        # 宿主版本范围
  python: ">=3.11"
capabilities:                           # 供 Router / Orchestrator 硬过滤
  - structured_output
  - file_write
  - network_read
permissions:                            # 显式声明；未声明 = deny
  filesystem:
    write_paths: ["${workspace}/**"]
  network:
    hosts: ["api.github.com"]
  shell:
    allowed_commands: []                # 默认空 = deny shell
  secrets:
    env_vars: ["MY_PLUGIN_API_KEY"]   # 仅允许读取列出的 env 名
data_policy:
  max_classification: SENSITIVE       # PUBLIC | INTERNAL | SENSITIVE | SECRET（SECRET 永不进模型）
description: "Short human-readable summary"
author: "local-only"
license: MIT
```

加载时 `doctor` 与 `plugins inspect` 必须校验：manifest 完整、entrypoint 可导入、`requires` 满足、permissions 可被 PolicyEngine 解析。

---

### 插件注册 CLI（本地 only，无 marketplace）

| 命令 | 说明 |
|---|---|
| `loop-pilot plugins list` | 已发现插件：bundled / enabled / disabled |
| `loop-pilot plugins inspect <name>` | manifest、capabilities、permissions、entrypoint |
| `loop-pilot plugins enable <name>` | 写入本地 `plugins.local.yaml` 启用 |
| `loop-pilot plugins disable <name>` | 禁用（不卸载文件） |
| `loop-pilot plugins doctor` | 扫描冲突 id、缺失 requires、权限过宽 |

发现路径（按优先级）：`./plugins/`、`~/.config/loop-pilot/plugins/`、editable install 的 entry points。**无** `plugins install` 从远程拉包（0.6 明确不做）。

---

### 模板生成器

```bash
loop-pilot new loop <name>       # 生成 Loop 插件骨架 + manifest + 最小测试
loop-pilot new skill <name>
loop-pilot new connector <name>
loop-pilot new adapter <name>    # ModelAdapter 插件
```

输出目录默认 `./plugins/<name>/`，含 `loop-pilot-plugin.yaml`、`src/`、`tests/`、`README.md`，与 `examples/plugins/` 中参考实现一致。

---

### 稳定扩展 API

| 层级 | 标记 | 承诺 |
|---|---|---|
| **Stable** | `@stable` / 文档「Stable API」 | 1.0 前仅 additive；1.0 后遵循 semver |
| **Semi-stable** | `@semi_stable` | 小版本可能调整；deprecation 警告 ≥1 个小版本 |
| **Experimental** | `@experimental` | 可随时变更；默认不在 `new` 模板中暴露 |

核心 Protocol（示意，实现于 `src/loop_pilot/plugins/`）：

```python
class LoopPlugin(Protocol):
    loop_type: str
    def observe(self, ctx: LoopContext) -> Observation: ...
    def plan(self, ctx: LoopContext, obs: Observation) -> TaskPlan: ...
    # ... 与 03–05 分册对齐的阶段方法

class SkillPlugin(Protocol): ...
class ConnectorPlugin(Protocol): ...
class ModelAdapterPlugin(Protocol): ...  # 包装现有 Adapter 基类
```

Loop 核心只依赖 Protocol 与 `LoopContext`；不得 import 插件内部实现。

---

### 模块路径（0.6 目标布局）

```text
src/loop_pilot/plugins/
├── __init__.py
├── manifest.py          # 解析 loop-pilot-plugin.yaml
├── registry.py          # 发现、enable/disable、冲突检测
├── loader.py            # 安全导入 entrypoint
├── protocols.py         # Loop/Skill/Connector/... Protocol
└── policy.py            # 插件 permissions → PolicyEngine 规则

src/loop_pilot/cli_plugins.py   # plugins list/inspect/enable/disable/doctor
src/loop_pilot/cli_new.py       # new loop|skill|connector|adapter

docs/plugins/                   # 插件作者指南
examples/plugins/
├── hello-loop/                 # 最小 Loop 插件示例
└── rss-connector-stub/         # Connector 示例
```

0.6 **仅文档与目录约定**；实现前不得破坏 0.1 Mini 验收。

---

### 安全

| 原则 | 要求 |
|---|---|
| **权限声明** | 无 `permissions` 段 → 网络/shell/写文件一律 deny |
| **PolicyEngine** | 所有 Tool/Adapter/Connector 调用经统一 Policy；插件不得绕过 |
| **Secrets** | 仅允许 manifest 列出的 `env_vars`；禁止读任意 environ |
| **Shell** | `allowed_commands` 默认 `[]`；非空时需用户 `plugins enable --acknowledge-risk` |
| **数据等级** | `data_policy.max_classification`  enforced；`SECRET` 硬拒绝 |
| **审计** | 插件 id + version 写入 `trace.jsonl` 与 `adapter_calls` |
| **隔离** | 无 VM sandbox（0.6 不做）；依赖声明式权限 + 用户显式 enable |

---

### 不可做（0.6）

| 排除项 | 说明 |
|---|---|
| 在线插件市场 / registry 服务 | 仅本地发现与 enable |
| 远程代码执行 / `curl \| sh` 安装 | 用户手动放置插件目录 |
| 自动安装第三方插件 | 无 `plugins install <url>` |
| VM / WASM 沙箱 | 非 0.6 范围；依赖权限模型 |
| 修改核心 Loop 内置语义而不走插件契约 | 禁止 monkey-patch Orchestrator |
| 默认启用未审阅插件 | bundled only 默认 on；第三方默认 off |

---

### 验收标准

1. **发现**：`plugins list` 显示 bundled 三 Loop + `examples/plugins` 中示例。
2. **inspect**：manifest 字段完整、permissions 可读。
3. **enable/disable**：启用后 `run <custom-loop> --dry-run` 可调度；禁用后明确错误。
4. **new 脚手架**：`loop-pilot new loop demo` 生成可测试骨架。
5. **Policy 拒绝**：未声明 `network` 的 Connector 调用外网 → BLOCKED。
6. **Shell deny**：未声明 `shell` 的插件调用 subprocess → BLOCKED。
7. **Secret deny**：读取未声明 env → BLOCKED。
8. **Router 集成**：ModelAdapter 插件注册后 `adapters doctor` 可见。
9. **0.1–0.5 基线不退化**：无插件时 Mini dry-run 与 PyPI 安装路径仍通过。
10. **审计**：trace 含 `plugin_name` / `plugin_version`。

### 推荐验收命令

```bash
loop-pilot plugins list
loop-pilot plugins inspect hello-loop
loop-pilot plugins enable hello-loop
loop-pilot plugins doctor
loop-pilot new loop my-experiment
loop-pilot run my-experiment --dry-run
pytest tests/unit/test_plugin_registry.py -q
pytest tests/unit/test_plugin_policy.py -q
```

---

### 工作量估算

约为 **0.5 完成后工程量的 20–30%**（单人兼职约 **12–18 人日**）：

| 工作包 | 估算 |
|---|---|
| manifest + loader + registry | 4–5 |
| Protocol 与 bundled 迁移 | 3–4 |
| cli_plugins + cli_new | 2–3 |
| Policy 集成 + 安全测试 | 3–4 |
| docs/plugins + examples | 2–3 |

---

### 版本发布说明片段

**EN**

> **0.6.0-plugin-ecosystem** — LoopPilot becomes an extensible framework. Add local plugins for Loops, Skills, Connectors, and Model Adapters via `loop-pilot-plugin.yaml`, manage them with `loop-pilot plugins list|enable|disable`, and scaffold with `loop-pilot new loop|skill|connector|adapter`. No online marketplace; permissions are declarative and enforced by PolicyEngine. Stable extension APIs are introduced with experimental/semi-stable tiers ahead of 1.0.

**CN**

> **0.6.0-plugin-ecosystem** — LoopPilot 从可安装工具升级为**可扩展框架**。可通过本地 `loop-pilot-plugin.yaml` 注册 Loop/Skill/Connector/Adapter 等插件，用 `loop-pilot plugins` 管理启用状态，用 `loop-pilot new` 生成脚手架。无在线市场；权限声明式配置并由 PolicyEngine 强制执行。为 1.0 稳定 API 引入 experimental / semi-stable 分层。

---

### 0.6 vs 0.7 vs 1.0 区分

| | **0.6 plugin-ecosystem** | **0.7 evaluation-benchmark** | **1.0 stable** |
|---|---|---|---|
| 扩展 API | 可用，含 experimental 变更 | 同 0.6；评测不冻结 API | **Stable Protocol** semver 承诺 |
| 插件 | 本地 + bundled | 同左；插件可自带 benchmark | 同左 + 弃用周期文档化 |
| 评测 | 无系统化 benchmark | **Evaluation Harness** + 指标 + 模型对比 | 依赖 0.7 数据做长期健康检查 |
| 长期运行 / 学习 | 依赖 0.4 | 不实现跨日学习 | 跨日链、健康检查、优先级解释 |

0.6 = 能插上扩展；0.7 = 能**证明**扩展跑得好不好；1.0 = 契约冻结且可依赖（经 **0.9 RC**）。

---

## 0.7.0-evaluation-benchmark — Evaluation Benchmark

**版本标签**：`0.7.0-evaluation-benchmark`（亦称 loop-eval）

### 一句话

LoopPilot 从「**可扩展**」（0.6）进化为「**可评测**」：用 benchmark、指标、Golden Case 与模型对比，系统化证明 Loops / Agents / Skills / Adapters 是否真正有效——衡量成功率、成本、风险、可恢复性、人工接受率与真实任务收益。

### 定位：0.6 vs 0.7 vs 1.0

| | **0.6 plugin-ecosystem** | **0.7 evaluation-benchmark** | **1.0 stable** |
|---|---|---|---|
| 核心问题 | 别人能否写自己的 Loop/Skill/Adapter？ | **跑得好不好？**哪个模型/Agent/Skill 更可靠？ | 接口与行为是否**长期可维护**？ |
| 分发 | 本地插件 manifest + `plugins` CLI | + `eval` CLI + `benchmarks/` 套件 | semver 承诺 + 弃用周期 |
| 评测 | pytest + fixture（开发期） | **正式 Evaluation Harness** + 指标报告 | 长期趋势与健康检查 |
| 模型 | Router 可用 | **可重复对比** model-role 配置 | 同左 |
| 外部工具 | 无强制 | **agentic-rubric-runner** 作外部 evaluator（不合并仓库） | 同左 |
| Registry | 无 | `eval publish-local` / `history`（**0.8** 项目级共享依赖此契约） | 同左 + semver 承诺 |
| 受众 | 贡献者 / 高级用户 | 维护者 / 插件作者 / 自证有效性的用户 | 个人/团队长期生产 |

0.6 = 可以扩展；0.7 = 可以**评价**扩展效果；1.0 = 靠数据与稳定契约说话的长期生产。

### 0.7 要回答的问题

- InternLoop 到底修复了多少 bug？失败主要发生在哪一阶段？
- PaperLoop 的建议有多少被采纳？ResearchCritic 有没有误判？
- DailyNews 里有多少信息真的进入 Intern/Paper 任务？
- CursorCLIAdapter 比普通 API Adapter 强多少？DeepSeek 做筛选是否足够？
- 人类到底采纳了多少结果？成本是否值得？

---

### Evaluation Harness

0.7 核心模块：**Evaluation Harness**——加载 benchmark、运行指定 Loop、收集 trace/artifacts、计算指标、生成评测报告、比较不同模型/配置。

| 命令 | 说明 |
|---|---|
| `loop-pilot eval list` | 列出可用 benchmark 套件与 case |
| `loop-pilot eval run <suite>` | 运行评测（如 `intern-basic`、`paper-claims`、`daily-news-ranking`） |
| `loop-pilot eval compare <eval-id-a> <eval-id-b>` | 对比两次 eval run（成功率、成本、延迟、错误分布） |
| `loop-pilot eval report <eval-id>` | 渲染/刷新 `eval-report.md` |
| `loop-pilot eval publish-local <name>` | 发布到本地 registry（**0.8** 按 project 隔离） |
| `loop-pilot eval history` | 本地 benchmark 运行历史 |

示例：

```bash
loop-pilot eval list
loop-pilot eval run intern-basic
loop-pilot eval run paper-claims
loop-pilot eval run daily-news-ranking
loop-pilot eval run paper-claims --model-role research_critic=gpt
loop-pilot eval run paper-claims --model-role research_critic=deepseek
loop-pilot eval compare eval-001 eval-002
loop-pilot eval report <eval-id>
```

Harness 默认在 **MockAdapter + dry-run** 下运行，保证可离线、可 CI；真实 Adapter 对比需显式 `--allow-real-adapters` 与 env。

---

### Benchmark Suite 结构

```text
benchmarks/
├── intern/
│   ├── python_bugfix_basic/
│   ├── failing_test_repair/
│   ├── unsafe_path_block/
│   ├── lint_fix/
│   └── dependency_error/
├── paper/
│   ├── unsupported_claim/
│   ├── fake_citation/
│   ├── missing_related_work/
│   ├── number_inconsistency/
│   └── experiment_gap/
└── daily_news/
    ├── duplicate_filter/
    ├── star_delta_ranking/
    ├── stale_news_block/
    ├── low_confidence_filter/
    └── route_to_loop/
```

每个 benchmark case 必须包含：

```text
input/           固定输入（代码、论文片段、新闻快照等）
expected/        结构化期望结果（outcome、关键字段）
rubric.yaml      验收断言（非低级 1–5 分表）
metadata.yaml    case_id、loop_type、tags、difficulty、requires_mock
```

`rubric.yaml` 定义 **pass/fail 断言**，可与 [21-test-fixtures-and-golden-cases.md](21-test-fixtures-and-golden-cases.md) 的 `assertions.yaml` 语义对齐；与 `tests/fixtures/` 可共享场景但 **benchmarks/** 为 0.7 权威评测目录。

---

### Metrics System（按 Loop）

#### InternLoop

| 指标 | 说明 |
|---|---|
| `task_success_rate` | 终态 SUCCEEDED 占比 |
| `test_pass_rate` | 目标测试由 fail→pass 占比 |
| `patch_acceptance_rate` | 人工或 rubric 接受的 patch 占比 |
| `unsafe_action_block_rate` | 危险路径被 Policy 拦截占比 |
| `unrelated_diff_rate` | diff 越界 / 无关文件修改占比 |
| `mean_rounds_to_success` | 成功 case 平均轮次 |
| `mean_runtime_seconds` | 平均耗时 |
| `model_cost_per_success` | 每次成功的模型费用（若可用） |

#### PaperLoop

| 指标 | 说明 |
|---|---|
| `claim_detection_recall` | 应检出的 claim 检出率 |
| `unsupported_claim_precision` | 标为 unsupported 的精确率 |
| `citation_verification_accuracy` | 引用核验正确率 |
| `source_required_correctness` | SOURCE REQUIRED 标注正确率 |
| `fabrication_rate` | 编造引用/元数据占比（应为 0） |
| `revision_acceptance_rate` | 修订建议被采纳占比 |
| `experiment_gap_recall` | 缺失实验检出率 |
| `reviewer_concern_match_rate` | 与预期 reviewer concern 匹配率 |

#### DailyNewsLoop

| 指标 | 说明 |
|---|---|
| `dedup_accuracy` | 同事件去重正确率 |
| `star_delta_correctness` | Star 增量计算正确率 |
| `source_freshness_accuracy` | 发布日 vs 事件日区分正确率 |
| `routing_accuracy` | 路由到 Intern/Paper 正确率 |
| `high_value_item_precision` | Top News 高价值条目精确率 |
| `noise_rate` | 低置信度误入正式条目占比 |
| `items_kept_count` | 保留条目数（辅助分布指标） |

#### Runtime（跨 Loop）

| 指标 | 说明 |
|---|---|
| `trace_completeness` | trace.jsonl 必填字段完整率 |
| `artifact_integrity` | manifest 与磁盘 hash 一致率 |
| `recovery_success_rate` | 可恢复场景 resume 成功率（依赖 0.4 fixture） |
| `approval_latency` | WAITING_APPROVAL → 决定耗时 |
| `blocked_reason_accuracy` | BLOCKED 原因与 golden 一致率 |
| `budget_compliance` | 30 分钟硬停止与软截止遵守率 |

所有指标由 `metrics.py` 从 `eval-results.json` 原始 case 结果**可重复计算**；不得依赖模型自由文本解析作为唯一依据。

---

### Golden Cases

Golden Case：**输入固定、期望输出固定、允许少量表达变化、核心判断必须一致**。与 benchmark 共用目录结构；`expected/` + `rubric.yaml` 中的 `required` / `forbidden` 断言为权威。

**PaperLoop 示例**

```yaml
case_id: paper_fake_citation_001
input:
  draft: input/paper.md
  references: input/references.bib
expected:
  outcome: blocked
  required_findings:
    - fake_citation_detected
    - source_required
forbidden:
  - outcome: succeeded
  - fabricated_bibtex
```

**InternLoop 示例**

```yaml
case_id: intern_simple_bugfix_001
expected:
  outcome: succeeded
  tests_pass: true
  forbidden_paths_modified:
    - .env
    - secrets/*
```

不得对完整 Markdown 做脆弱字符串比较；验证 front matter、outcome、证据链接、关键事实与 forbidden 列表（见 [21-test-fixtures-and-golden-cases.md](21-test-fixtures-and-golden-cases.md)）。

---

### Model Comparison

通过 **eval run** 对比配置，而非主观感受：

```bash
loop-pilot eval run paper-claims --model-role research_critic=gpt
loop-pilot eval run paper-claims --model-role research_critic=deepseek
loop-pilot eval compare eval-001 eval-002
```

对比维度：成功率、错误类型分布、成本、延迟、输出稳定性、Schema 通过率、人工接受率（若 sidecar 记录）。

---

### Evaluation Report 输出

每次 `eval run` 写入独立 eval 目录（如 `var/eval/<eval-id>/`）：

| 产物 | 说明 |
|---|---|
| `eval-report.md` | 人类可读：总成功率、各 Loop/case 结果、失败分布、成本、耗时、不安全拦截、推荐改进 |
| `eval-results.json` | 机器可读：每 case pass/fail、指标快照、run_id 引用 |
| `eval-summary.csv` | 表格汇总：便于 spreadsheet 与 CI 趋势 |

报告必须基于结构化数据渲染，非模型臆造结论。

---

### agentic-rubric-runner 集成（外部 evaluator，不合并仓库）

[agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner)（若本地安装）可作为 **PaperLoop 评价**的外部 companion，输出结构化 Claim–Evidence、实验充分性、Reviewer concern（见 [15-ideas-traceability.md](15-ideas-traceability.md) §5）。

**不合并仓库**；通过配置接入：

```yaml
evaluators:
  rubric_runner:
    type: external_cli
    command: agentic-rubric-runner evaluate
```

LoopPilot 负责运行 Loop 并收集 artifacts；外部 CLI 负责 rubric 评价；结果合并进 `eval-results.json`。简单 1–5 分接口不进入核心评价链。

---

### 模块路径（0.7 目标布局）

```text
src/loop_pilot/eval/
├── __init__.py
├── runner.py           # eval run 编排
├── benchmark.py        # 加载 benchmarks/
├── metrics.py          # 指标计算
├── assertions.py       # golden / rubric 断言
├── compare.py          # eval compare
├── report.py           # eval-report.md 渲染
└── result_store.py     # eval-results.json / eval-summary.csv

src/loop_pilot/cli_eval.py    # eval list|run|compare|report

benchmarks/                     # 见上文套件结构
docs/evaluation/
├── overview.md
├── writing-benchmarks.md
├── metrics.md
├── model-comparison.md
└── integrating-agentic-rubric-runner.md
```

0.7 **仅文档与目录约定**；实现前不得破坏 0.1 Mini 验收。

---

### 不可做（0.7）

| 排除项 | 说明 |
|---|---|
| 公开排行榜 / 云端评测平台 | **仅本地** benchmark |
| 模型商业排名 / 对外榜单 | 个人与 CI 内部使用 |
| 大量自动 benchmark 下载 | 内置套件 + 用户自备 case |
| 昂贵 API 的**默认**评测 | 默认 MockAdapter；真实模型需显式 opt-in |
| 未经许可收集用户数据 | 评测数据不出本机（除非用户导出） |
| 合并 agentic-rubric-runner 仓库 | 仅 external_cli evaluator |

Local benchmark yes；Public leaderboard no。

---

### 验收标准

#### 命令

1. `loop-pilot eval list`
2. `loop-pilot eval run intern-basic`
3. `loop-pilot eval run paper-claims`
4. `loop-pilot eval run daily-news-ranking`
5. `loop-pilot eval report <eval-id>`
6. `loop-pilot eval compare <eval-id-a> <eval-id-b>`

#### 指标与产物

7. 每次 eval run 生成 `eval-results.json` 与 `eval-report.md`
8. 每次 case 有 pass/fail 与失败原因码
9. 指标可重复计算；模型成本与耗时被记录
10. trace / artifact integrity 被检查

#### Benchmark 数量

11. 至少 **5** 个 Intern benchmark
12. 至少 **5** 个 Paper benchmark
13. 至少 **5** 个 DailyNews benchmark
14. 每个 benchmark 有 expected 断言
15. 每个 benchmark 在 MockAdapter 下稳定通过（CI 可跑）

#### 基线不退化

16. 0.1–0.6 验收命令仍全部通过

### 推荐验收命令

```bash
loop-pilot eval list
loop-pilot eval run intern-basic
loop-pilot eval run paper-claims
loop-pilot eval run daily-news-ranking
loop-pilot eval report <eval-id>
loop-pilot eval compare <eval-id-a> <eval-id-b>
pytest tests/unit/test_eval_metrics.py -q
pytest tests/integration/test_eval_harness.py -q

# 0.1 回归
pytest -q
loop-pilot run all --fixture-set mini --dry-run
```

---

### 工作量估算

约为 **0.6 完成后工程量的 20–30%**（单人兼职约 **12–18 人日**）：

| 工作包 | 估算 |
|---|---|
| benchmark 套件（15+ case） | 4–5 |
| runner + assertions + result_store | 3–4 |
| metrics + report + compare | 3–4 |
| cli_eval + 配置（evaluators） | 2–3 |
| docs/evaluation + rubric-runner 集成文档 | 2–3 |

---

### 版本发布说明片段

**EN**

> **0.7.0-evaluation-benchmark** — LoopPilot becomes **evaluable**: run local benchmarks with `loop-pilot eval list|run|compare|report`, measure per-loop metrics (success, cost, safety, routing), compare model roles on fixed suites, and emit `eval-report.md` / `eval-results.json` / `eval-summary.csv`. Golden cases use structured assertions, not fragile markdown diffs. Optional `agentic-rubric-runner` integrates as an external CLI evaluator—no repo merge. No public leaderboard or cloud platform; default eval stays offline on MockAdapter.

**CN**

> **0.7.0-evaluation-benchmark** — LoopPilot 从可扩展升级为**可评测**：通过 `loop-pilot eval` 运行本地 benchmark，按 Loop 统计成功率、成本、安全与路由等指标，对比不同 model-role 配置，产出 `eval-report.md`、`eval-results.json`、`eval-summary.csv`。Golden Case 使用结构化断言。可选将 agentic-rubric-runner 作为外部 CLI evaluator 接入，**不合并仓库**。不做公开排行榜或云端平台；默认评测保持 MockAdapter 离线可复现。

---

### 0.7 vs 1.0 区分

| | **0.7 evaluation-benchmark** | **1.0 stable** |
|---|---|---|
| 证明什么 | LoopPilot **可以被评测**、扩展可被量化 | **稳定、可维护、可升级** |
| API | eval API 可能仍调整 | Stable Protocol + 弃用周期 |
| 长期学习 | 不实现跨日优先级学习 | 跨日链、健康检查、趋势 |
| 数据 | 单次/对比 eval run | 连续运行的长期指标趋势 |

没有 0.7，1.0 容易变成主观稳定；有了 0.7，1.0 可以靠数据说话。

---

## 0.8.0-team-cloud-preview — Team Collaboration Preview

**版本标签**：`0.8.0-team-cloud-preview`（亦称 **collaboration-preview**）

### 一句话

从**个人本地工具**进化为**本地优先的团队协作**：多项目 workspace、RBAC、共享审批与审计、用量核算、本地 Web Dashboard、团队级插件策略。**不是** cloud SaaS。

### 定位：0.7 vs 0.8 vs 0.9

| | **0.7 eval** | **0.8 team collaboration** | **0.9 release-candidate** |
|---|---|---|---|
| 核心问题 | 能否度量质量？ | 能否**多人安全协作**？ | 接口是否可冻结？ |
| 多用户 | 单用户本地 | **项目级** RBAC + 共享审批 | 同 0.8，加兼容性矩阵 |
| UI | CLI only | **本地 Dashboard** 预览（:7860） | Dashboard 行为冻结 |
| 分发 | 本地 registry | `~/.loop-pilot/projects/` | migration + compat tests |
| 云 | 无 | **无**（local-first） | 无 |

0.7 = 能评测；0.8 = 能协作；0.9 = 能承诺接口稳定。

---

### 项目 Workspace

多项目隔离：每个项目在 `~/.loop-pilot/projects/<project-id>/` 下拥有独立配置、状态索引、审批队列与 benchmark registry 引用。

| 命令 | 说明 |
|---|---|
| `loop-pilot project create <name>` | 创建项目 workspace（生成 id、默认 RBAC、目录树） |
| `loop-pilot project list` | 列出本地已知项目 |
| `loop-pilot project inspect <project-id>` | 成员、角色、插件策略、用量摘要 |

目录约定（示意）：

```text
~/.loop-pilot/projects/<project-id>/
├── project.yaml           # 元数据、RBAC、插件策略
├── state/                 # 项目级 SQLite 或索引（指向 var/state）
├── approvals/             # 共享审批队列索引
├── eval/                  # 共享 benchmark registry（0.7 契约）
└── usage/                 # 用量聚合快照
```

当前活跃项目可通过 `LOOP_PILOT_PROJECT` 或 `loop-pilot project use <id>` 切换（实现细节见 `docs/team/`）。

---

### RBAC

项目内五种角色；权限为 **additive**，高角色包含低角色能力（除 owner 转让外）。

| 角色 | 典型权限 |
|---|---|
| **owner** | 项目创建/删除、成员与角色管理、插件策略、全部 run/approve |
| **maintainer** | 配置变更、插件 enable、run all、审批（除 owner-only 策略） |
| **reviewer** | 查看 run/artifact、`approve` / `reject`、只读 Dashboard |
| **runner** | 触发 `run` / `run all`、查看自己的 run；**不可**改配置或插件策略 |
| **viewer** | 只读：`status`、`inspect`、`report`、Dashboard 浏览 |

安全要求：

- 所有角色变更写入 **team audit trail**（追加事件，不可静默覆盖）。
- CLI 与 Dashboard 操作均记录 `actor` + `role` + `project_id`。
- 无项目上下文时，行为退化为 0.4 个人模式（向后兼容）。

---

### 共享审批（Shared Approval）

在 0.4 个人 `approvals` 之上，增加**项目级**可见性与多人批复语义。

| 命令 | 说明 |
|---|---|
| `loop-pilot approvals list [--project]` | 项目内待审批队列 |
| `loop-pilot approvals inspect <approval-id>` | 详情：run、reason、请求者、过期时间 |
| `loop-pilot approvals approve <approval-id>` | reviewer+ 可执行 |
| `loop-pilot approvals reject <approval-id> --reason "..."` | reviewer+ 可执行 |

- **Team audit trail**：每次 list/inspect/approve/reject 产生审计事件，可在 Dashboard 与 `trace.jsonl` 关联查询。
- 审批 TTL 与 0.4 `approvals.default_ttl_minutes` 对齐；过期 → BLOCKED，全项目可见。
- 个人模式（无 project）下命令语义与 0.4 一致。

---

### 本地 Web Dashboard 预览

**Local-first** 只读/有限写 UI；不部署到公网，不替代 CLI 为唯一控制面。

| 项 | 说明 |
|---|---|
| 栈 | FastAPI 后端 + 简单前端（静态或轻量 SPA） |
| 启动 | `loop-pilot dashboard start` |
| 默认端口 | `:7860`（可配置） |
| 绑定 | 默认 `127.0.0.1`；显式 `--host 0.0.0.0` 需文档警告 |

Dashboard 预览范围：

- 项目列表与当前 project 概览
- Run 状态、pending approvals、最近 daily-summary 链接
- 用量摘要（today / week / project）
- Benchmark 历史与对比入口（只读，写操作仍走 CLI）

---

### 共享 Benchmark Registry（项目内）

在 **0.7** eval 契约之上，registry **按 project 隔离**：

| 命令 | 说明 |
|---|---|
| `loop-pilot eval publish-local <name> [--project]` | 将 eval run 发布到当前项目 registry |
| `loop-pilot eval history [--project]` | 项目级 benchmark 运行历史 |
| `loop-pilot eval compare <a> <b> [--project]` | 同项目内对比 |

团队成员按 RBAC：`viewer` 只读；`runner+` 可 publish；`maintainer+` 可管理 baseline 标签（若启用）。

---

### 成本 / 用量核算（Usage Accounting）

基于 0.4 `adapter_calls` 与 Router 日志聚合，**本地存储**，不上传云端。

| 命令 | 说明 |
|---|---|
| `loop-pilot usage today [--project]` | 当日 token/调用/估算费用摘要 |
| `loop-pilot usage week [--project]` | 近 7 日滚动窗口 |
| `loop-pilot usage project [--project]` | 项目生命周期累计 |

- 费用为**估算**（配置单价表），非 billing 系统。
- Dashboard 展示与 CLI 同源数据。
- `SECRET` 与原始 prompt 不出现在用量报表。

---

### 团队安全插件策略（Team Plugin Policy）

在 0.6 本地 `plugins.local.yaml` 之上，项目级 `project.yaml` 增补：

```yaml
plugins:
  require_approval: true          # 启用新插件需 maintainer+ 批准
  allowed_plugins:                # 空 = 仅 bundled；非空 = 白名单
    - hello-loop
  blocked_permissions:            # 团队禁止的能力（即使 manifest 声明）
    - shell
    - network_write
```

- `PolicyEngine` 合并：**blocked_permissions** 优先于插件 manifest。
- 未在白名单且 `allowed_plugins` 非空 → 拒绝 enable。
- `require_approval: true` 时，`plugins enable` 创建审批项而非立即生效。

---

### 模块路径（0.8 目标布局）

```text
src/loop_pilot/projects/          # project create/list/inspect、目录布局
src/loop_pilot/auth/              # RBAC、角色解析、actor 上下文
src/loop_pilot/approvals/         # 共享审批队列 + team audit trail
src/loop_pilot/usage/             # 用量聚合 today/week/project
src/loop_pilot/dashboard/         # FastAPI app、静态前端、:7860
src/loop_pilot/cli_project.py     # project *
src/loop_pilot/cli_approvals.py   # approvals list/inspect/approve/reject（团队语义）
src/loop_pilot/cli_dashboard.py   # dashboard start
src/loop_pilot/cli_usage.py       # usage today/week/project

docs/team/                        # 团队协作部署、RBAC、Dashboard 安全说明
```

0.8 **仅文档与目录约定**；实现前不得破坏 0.1 Mini 验收。

---

### 不可做（0.8）

| 排除项 | 说明 |
|---|---|
| Cloud SaaS / 托管多租户 | **本地优先**；无 central server 依赖 |
| Multi-tenant billing / 订阅计费 | 仅本地用量估算 |
| Enterprise SSO（SAML/OIDC 企业 IdP） | 本地用户/角色文件或 OS 用户映射即可 |
| 在线插件市场 / registry 服务 | 延续 0.6 本地 only |
| 自动 push / PR / deploy | 全版本禁止 |
| 公网默认暴露 Dashboard | 必须默认 bind 127.0.0.1 |

---

### 验收标准

1. **Project workspace**：`project create/list/inspect` 创建可切换的项目目录树。
2. **RBAC**：runner 无法改插件策略；viewer 无法 approve；越权 CLI 返回明确错误。
3. **共享审批**：`approvals list/inspect/approve/reject` 全链路可审计；audit trail 可查询。
4. **Dashboard**：`dashboard start` 在 `:7860` 展示 run/pending/usage；默认仅 localhost。
5. **Eval registry**：项目内 `eval publish-local/history/compare` 与 0.7 契约一致且隔离。
6. **Usage**：`usage today/week/project` 与 adapter_calls 聚合一致（允许估算误差文档化）。
7. **插件策略**：`blocked_permissions` 与 `allowed_plugins` enforced；`require_approval` 走审批流。
8. **安全测试**：RBAC 越权、Dashboard 未授权访问、跨 project 数据泄漏 — pytest 覆盖。
9. **0.1–0.7 基线不退化**：无 project 上下文时 Mini dry-run 与个人模式仍通过。
10. **Team audit trail**：approve/reject/角色变更均有不可变事件记录。

### 推荐验收命令

```bash
loop-pilot project create demo-team
loop-pilot project list
loop-pilot project inspect demo-team

loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot approvals list
loop-pilot approvals inspect <approval-id>
loop-pilot approvals approve <approval-id>

loop-pilot eval publish-local baseline-v1
loop-pilot eval history
loop-pilot eval compare baseline-v1 baseline-v2

loop-pilot usage today
loop-pilot usage week
loop-pilot usage project

loop-pilot dashboard start    # 浏览器打开 http://127.0.0.1:7860

pytest tests/unit/test_rbac.py -q
pytest tests/unit/test_team_approvals.py -q
pytest tests/integration/test_dashboard_local.py -q
```

---

### 工作量估算

约为 **0.7 完成后工程量的 25–35%**（单人兼职约 **18–28 人日**）：

| 工作包 | 估算 |
|---|---|
| projects workspace + CLI | 4–5 |
| auth / RBAC + audit trail | 4–6 |
| 共享 approvals + CLI | 3–4 |
| usage 聚合 + CLI | 2–3 |
| dashboard（FastAPI + 前端） | 5–7 |
| 团队插件策略 + Policy 集成 | 2–3 |
| docs/team + 安全/集成测试 | 3–4 |
| **合计** | **18–28** |

假设 0.7 eval registry 与 0.4 SQLite/approvals 已验收。

---

### 版本发布说明片段

**EN**

> **0.8.0-team-cloud-preview** — LoopPilot evolves from a personal local tool to **local-first team collaboration**: multi-project workspaces under `~/.loop-pilot/projects/`, RBAC (owner/maintainer/reviewer/runner/viewer), shared approvals with team audit trail, usage accounting (`usage today|week|project`), a local Web Dashboard preview on `:7860` (`loop-pilot dashboard start`), project-scoped benchmark registry, and team plugin policy (`require_approval`, `allowed_plugins`, `blocked_permissions`). Not cloud SaaS—no multi-tenant billing, enterprise SSO, or plugin marketplace.

**CN**

> **0.8.0-team-cloud-preview** — LoopPilot 从个人本地工具升级为**本地优先团队协作**：`~/.loop-pilot/projects/` 多项目 workspace、五级 RBAC、带团队审计 trail 的共享审批、用量核算、`:7860` 本地 Dashboard 预览、项目内 benchmark registry 与团队插件策略。**非**云端 SaaS——不含多租户计费、企业 SSO 或插件市场。

---

## 0.9.0-release-candidate — Release Candidate

**版本标签**：`0.9.0-release-candidate`（PyPI：`0.9.0rc1` / `rc2` / `rc3`）

> **0.9 不是加功能**，是 **冻结、测试、修复、兼容、清理、文档定稿**。完整清单见 [34-version-roadmap-0x.md §10](34-version-roadmap-0x.md#10-09-release-candidate--stability-freeze-090-release-candidate)。

### 一句话

0.8 ≈ 功能完备 preview；**0.9 = 最后一次全面验收**；**1.0 = 对稳定性的正式承诺**。

### 0.9 核心原则（允许的工作类型）

1. **Freeze** — API、配置 schema、DB migration 进入冻结窗口
2. **Test** — conformance、安全、7 天模拟长跑
3. **Fix** — P0/P1 bug、兼容性问题、文档错误
4. **Compat** — 0.5→0.9 升级路径、deprecation 宽限期
5. **Cleanup** — 死代码、实验 flag、未文档化 CLI 标 deprecated
6. **Docs** — 用户文档、API 参考、迁移指南定稿

**禁止**：新 Loop、新 Adapter 类型、破坏性 API/config/DB 变更（一律推迟到 **2.0**）。

### 冻结项（概要）

| 冻结项 | 交付物 |
|---|---|
| **Stable API** | `docs/stability/api-freeze.md` + `conformance/` 套件 |
| **配置 Schema** | `config/schema_versions/` + `config validate` / `migrate` / `doctor` |
| **DB migration** | `db/migrations/` additive-only + `db migrate --dry-run` / `db doctor` |
| **插件 manifest** | `loop-pilot-plugin.yaml` 必填字段与 permissions 块 |
| **文档** | 用户-facing 文档与 CLI `--help` 一致；broken link 清零 |
| **Security** | `docs/stability/security-review-0.9.md`；Critical/High 清零方可 rc1 |
| **Deprecation** | `docs/stability/deprecation-policy.md` |

### RC 流程

```text
0.8 验收 → stability/0.9 分支 → 0.9.0rc1 → rc2（P0 清零 + 7 天长跑）→ rc3（仅 bugfix）→ 1.0.0-stable
```

rc(N+1) 仅当 rc(N) 无 open P0 且 conformance CI 连续 7 天绿；1.0 自末位 rc **理想情况下零功能性 diff**。

### 0.8 vs 0.9 vs 1.0 区分

| | **0.8 team collaboration** | **0.9 release-candidate** | **1.0 stable** |
|---|---|---|---|
| 目标 | 交付协作能力 preview | **证明可发布** | **正式稳定承诺** |
| 接口 | 可演进 | **冻结** | semver 承诺 + 弃用周期 |
| 变更 | 可小改 | bugfix only | patch / security only |
| 云/SaaS | 不做 | 不做 | 不做 |

### 验收命令（示例）

```bash
loop-pilot doctor
loop-pilot config validate
loop-pilot config migrate --dry-run
loop-pilot db doctor
loop-pilot db migrate --dry-run
pytest -q && pytest conformance/ -q
loop-pilot run all --fixture-set mini --dry-run
```

### 工作量估算

约为 **到 0.8 已完成工程量的 15–25%**（稳定化工程；单人兼职约 **2–4 周**）。

### 版本发布说明片段

**EN**

> **0.9.0-release-candidate** — API, configuration, documentation, and plugin interfaces are frozen. Migration checks, conformance tests, security review, and a 7-day reliability simulation gate the 1.0 stable release. Bugfixes only during RC; no new features.

**CN**

> **0.9.0-release-candidate** — 冻结 API、配置、文档与插件接口；通过 migration 检查、conformance 测试、安全审计与 7 天模拟长跑后进入 **1.0.0-stable**。RC 期间仅修 bug，不增新功能。

---

## 1.0.0-stable — Stable（Production-Ready）

**版本标签**：`1.0.0-stable`

> **1.0 不是「功能最多」的版本**，而是 **稳定性承诺的 capstone**：API、配置、状态迁移、安全、长跑可靠性、文档——六项承诺在 0.9 RC 冻结基线上**正式 semver 毕业**。
>
> **0.9 RC → 1.0 stable**：仅 bug 修复、发布冻结、打 stable tag；**无 major 新功能**。若 rc3 仍有 P0，发 rc4，不跳级进 1.0。

### 定位：0.9 vs 1.0

| 维度 | **0.9 release-candidate** | **1.0 stable** |
|---|---|---|
| 性质 | 最后验收；接口冻结 | **正式稳定承诺** |
| 新功能 | 禁止 | 禁止（直至 1.x minor 增强） |
| 破坏性变更 | 禁止 | 禁止（直至 **2.0**） |
| 心理契约 | 「请帮我们试最后一轮」 | 「可长期依赖的个人/小团队生产工具」 |

---

### 1. Core API Stability（核心 API 稳定性）

1.0 对以下 **Stable public API** 作出 semver 承诺（1.x 内仅 additive；breaking → 2.0）：

| API 域 | 稳定面 | 文档 |
|---|---|---|
| **Loop** | `LoopPlugin` Protocol、阶段契约、`loop_type` 注册 | `03`–`05` 分册 + `docs/stability/api-freeze.md` |
| **Agent** | Agent registry、`model_role` 声明、阶段调用图 | `06-agents-skills-tools.md`、`28-agent-development-guide.md` |
| **Skill** | `SkillPlugin` Protocol、输入/输出 Schema | `20-skill-specifications.md` |
| **Tool** | `ToolBroker` 调用契约、Policy 拦截语义 | `06`、`08-security-and-recovery.md` |
| **Connector** | `ConnectorPlugin` Protocol、降级与 rate limit | `13-source-and-crawler-plan.md`、`19-adapter-specifications.md` |
| **ModelAdapter** | `BaseAdapter` 五方法、capabilities、healthcheck | `19`、`30-adapter-and-model-router-roadmap.md` |
| **StateStore** | `runs` / `checkpoints` / `approvals` 读写接口 | `07-data-and-reports.md`、`18-state-transition-spec.md` |
| **Plugin** | manifest schema、`plugins` CLI、Stable Protocol 层 | `docs/plugins/` |
| **Evaluation** | `eval list|run|compare|report`、benchmark 目录结构 | `docs/evaluation/` |

**Deprecation policy**（自 1.0 生效，详见 `docs/stability/deprecation-policy.md`）：

- Stable API 弃用须 **≥2 个 minor 版本**警告期（如 1.0 deprecated → 最早 1.2 移除）。
- Semi-stable / experimental 可在 1.x minor 调整，但须 CHANGELOG + `doctor` WARN。
- CLI 命令重命名：旧命令保留 alias 至少 1 个 minor；`--help` 标注 deprecated。
- JSON artifact / trace 事件：仅 additive 字段；移除字段 → major。

---

### 2. Configuration Stability（配置稳定性）

**覆盖全部 YAML 配置文件**：

| 文件 | 用途 |
|---|---|
| `loop-pilot.yaml` | 全局 runtime、schedule、recovery、approvals |
| `intern.yaml` / `paper.yaml` / `daily-news.yaml` | 三 Loop 专用 |
| `adapters.yaml` | Adapter 与 ModelRouter |
| `plugins.local.yaml` | 本地插件 enable 列表 |
| `projects.yaml` / `project.yaml` | 0.8 团队项目作用域（可选） |

```bash
loop-pilot config validate
loop-pilot config migrate [--dry-run]
loop-pilot doctor
```

- 每个配置文件含 **`schema_version`**；**1.0 起 config schema additive-only**，直至 config major 或 loop-pilot **2.0**。
- `config/schema_versions/` 保存各版本快照；`conformance/` 覆盖样例配置 0.5–0.9。

---

### 3. State Migration Stability（状态迁移稳定性）

| 命令 / 脚本 | 职责 |
|---|---|
| `loop-pilot db doctor` | schema 版本、表完整性、orphan run 检测 |
| `loop-pilot db migrate [--dry-run]` | 版本化 migration；1.0 起 **additive-only** |
| `scripts/backup_state.py` | SQLite + artifact 索引备份 |
| `loop-pilot recovery-scan` | 中断 run、遗留锁、半写终态扫描 |
| `scripts/migrate_state.py` | 跨 major 一次性迁移（可 dry-run） |

**升级保证**：从 **0.4.0** 至 **1.0.0** 的 migration 链在 CI 全绿；migration 失败时不半写；run 进行中不支持 hot migration。

---

### 4. Safety Stability（安全稳定性）

| 原则 | 1.0 承诺 |
|---|---|
| **Safe by default** | `allow_real_adapters=false`；shell/network/write 默认 deny；第三方插件默认 disabled |
| **Explicit by exception** | 真实 Adapter、`--allow-write`、`plugins enable --acknowledge-risk` 须显式 opt-in |
| **Auditable always** | Tool/Adapter/Connector/Plugin 调用写入 `trace.jsonl` + `adapter_calls`；SECRET 永不进模型 |

PolicyEngine 为唯一 enforcement 点；Critical 漏洞以 **1.0.x patch** 发布（见 `SECURITY.md`）。

---

### 5. Long-Running Reliability（长跑可靠性）

| 机制 | 1.0 标准 |
|---|---|
| **7 天稳定性** | 0.9 模拟长跑通过；1.0 soak 期无 P0 回归 |
| **Recovery** | ACTING 中断 → 默认 BLOCKED；合法 checkpoint `resume` |
| **Audit** | daily-summary、pending 队列、trace 跨日可关联 |
| **Budget** | 30 分钟硬停止；`WAITING_APPROVAL` 不计入执行预算 |
| **跨日链** | Intern 遗留、DailyNews 路由、Paper 缺口在 daily-summary 可解释（旧 V3 子集） |

---

### 6. Documentation Stability（文档稳定性）

**1.0 必达文档**：`docs/getting-started.md`（含 zh）、`docs/concepts/`、`docs/configuration/`、`docs/safety/`、`docs/loops/*`、`docs/adapters/`、`docs/plugins/`、`docs/evaluation/`、`docs/stability/`、`docs/upgrade/`、`docs/development/`（本文 33 + 34）、`examples/`。

- **10 分钟陌生人安装**：`pip install loop-pilot` → `init demo` → `doctor` → `run all --fixture-set mini --dry-run`。
- **30 分钟插件开发**：`loop-pilot new loop hello` → enable → dry-run（见 `docs/plugins/quickstart.md`）。

---

### 7. Required Capabilities at 1.0（1.0 必备能力）

1.0 **不新增**业务能力；它承诺 0.1–0.9 已 GA 的能力**稳定可用**：

| 能力域 | 1.0 必备 |
|---|---|
| 三 Loop | Intern / Paper / DailyNews 完整 Observe→Report |
| Adapter 集 | Mock（默认）、CodingCLI、OpenAICompatible；ModelRouter + ToolBroker |
| 插件系统 | 本地 manifest、`plugins` CLI、`new loop|skill|connector|adapter` |
| 评测系统 | `eval list|run|compare|report`；15+ benchmark |
| Recovery CLI | `resume`、`approve`、`reject`、`cancel`、`report`、`pending`、`recovery-scan` |
| 调度 CLI | `schedule print`、`schedule install --dry-run` |
| 日常报告 | `summary today`、daily-summary.md |
| 分发 | PyPI `1.0.0`；`pytest conformance/` 永久 CI 门禁 |

---

### 8. What 1.0 Does NOT Include（1.0 明确不包含）

SaaS / 托管运行、企业 SSO / LDAP、插件市场 / 远程安装、完整 Web UI（0.8 Dashboard 为 preview）、multi-tenant billing、向量库 / RAG、自动 push/PR/deploy/投稿/交易、破坏性 API 变更（→ **2.0**）。

---

### 9. Acceptance Criteria（验收标准）

#### 9.1 安装（陌生人 10 分钟）

```bash
pip install loop-pilot==1.0.0
loop-pilot init demo
cd loop-pilot-demo
loop-pilot doctor
loop-pilot run all --fixture-set mini --dry-run
loop-pilot status
```

#### 9.2 开发（贡献者）

```bash
git clone https://github.com/bosprimigenious/loop-pilot.git
cd loop-pilot && pip install -e ".[dev]"
pytest -q && pytest conformance/ -q
loop-pilot doctor
```

#### 9.3 真实运行（显式 opt-in）

```bash
loop-pilot config validate
loop-pilot adapters doctor
loop-pilot run intern --workspace /path/to/repo --dry-run
loop-pilot run all
loop-pilot summary today
```

#### 9.4 Recovery（sqlite 后端）

```bash
loop-pilot db doctor
loop-pilot run all
loop-pilot pending
loop-pilot recovery-scan
loop-pilot resume <run-id>
loop-pilot approve <run-id>
loop-pilot report <run-id>
python scripts/backup_state.py --dry-run
```

#### 9.5 Plugin

```bash
loop-pilot plugins list && loop-pilot plugins doctor
loop-pilot new loop my-demo
loop-pilot plugins enable my-demo
loop-pilot run my-demo --dry-run
```

#### 9.6 Eval

```bash
loop-pilot eval list
loop-pilot eval run intern-basic
loop-pilot eval run paper-claims
loop-pilot eval report <eval-id>
loop-pilot eval compare <a> <b>
```

#### 9.7 Release（maintainer）

```bash
loop-pilot config migrate --dry-run
loop-pilot db migrate --dry-run
pytest -q && pytest conformance/ -q
python -m build && twine check dist/*
```

**完成定义**：七组命令全通过 + §10 Release Gate 全勾选 + 自末位 rc **零功能性 diff**（ideal）。

---

### 10. Release Gate Checklist（发布门禁）

#### P0（阻塞 1.0）

- [ ] 无 open P0 issue
- [ ] `pytest -q` + `pytest conformance/ -q` 全绿
- [ ] Mini 基线全绿
- [ ] `docs/stability/api-freeze.md` 与代码一致
- [ ] `config validate` / `migrate` 对 0.5–0.9 样例全通过
- [ ] `db migrate --dry-run` 从 0.4 schema 至 1.0 全通过
- [ ] SECURITY_REVIEW 无 open Critical/High
- [ ] 7 天模拟长跑 + 1.0 soak 无 P0 回归
- [ ] PyPI `1.0.0` quick start 通过

#### P1（强烈建议）

- [ ] 15+ benchmark CI 绿；插件示例 enable + dry-run 绿
- [ ] 0.8 RBAC 场景测试绿（若 team GA）
- [ ] CHANGELOG 完整；Upgrade 0.9→1.0；broken link 清零
- [ ] `twine check` + 包内容审计

---

### 11. Release Notes（发布说明片段）

**EN**

> **1.0.0-stable** — LoopPilot reaches **production-ready stability**. This release adds no major features; it graduates the 0.9 RC freeze with formal semver promises for APIs, configuration, SQLite migrations, safety, and 7-day long-running reliability. Install with `pip install loop-pilot==1.0.0`; upgrade from 0.9.x with `loop-pilot config migrate && loop-pilot db migrate`. Breaking changes deferred to 2.0.

**CN**

> **1.0.0-stable** — LoopPilot 达到**生产就绪稳定版**。本版本不增加 major 新功能，在 0.9 RC 冻结基线上对 API、配置、SQLite 迁移、安全与 7 天长跑可靠性作出正式 semver 承诺。使用 `pip install loop-pilot==1.0.0` 安装；从 0.9.x 升级请执行 `loop-pilot config migrate && loop-pilot db migrate`。破坏性变更推迟至 2.0。

---

### 12. Post-1.0 Path（1.0 之后路线）

**1.x**（additive only）：新 Connector/Adapter 插件、eval 套件扩展、跨日优先级解释、Artifact 保留、0.8 team GA 化、性能与文档。

**2.0**（唯一 breaking major）：Stable API / config / DB 破坏性变更、可选企业 SSO / 托管协作 / 插件 registry（若产品确认）。

**原则**：1.0 后用户应能「装一次、用三年」；2.0 才是契约重置。

---

### 13. Effort Estimates（工作量估算）

**自当前状态（0.1 进行中）至 1.0**（单人兼职，2026-06-20 基线）：

| 里程碑 | 估计剩余 | 工期 |
|---|---|---|
| 完成 0.1 | 25–35% | 1–3 天 |
| 至 0.2–0.3 | 45–70% | +2–4 周 |
| 至 0.4–0.5 | 75–90% | +4–6 周 |
| 至 0.6–0.7 | 88–95% | +3–5 周 |
| 至 0.8–0.9 RC | 95–100% | +4–8 周 |
| **0.9 → 1.0** | **全路径 5–10%** | **3–7 天**（tag、soak、发布） |

0.9→1.0 几乎无新开发；若 rc3 已全绿，**3–7 天**可发布 1.0。

---

### 1.0 仍禁止（全版本）

- 自动部署、自动投稿、自动交易等高风险无人值守动作。
- 密钥与 `SECRET` 数据进入模型上下文或公开报告。

---

## 旧 V1/V2/V3 与新编号对照

| 旧称呼 | 新编号 | 说明 |
|---|---|---|
| Mini | **0.1.0-mini** | 当前焦点 |
| V1/MVP（混合） | **0.2 + 0.3 + 0.4** | 拆分为实用配置、Adapter、每日运行 |
| V1 中的 Adapter/Router | **0.3.0-adapter-mvp** | 旧误称「V1」常指此层 — **应称 0.3** |
| V1 中的 SQLite/恢复/调度 | **0.4.0-recovery-and-automation** | 旧「V1」的每日自动化主体 |
| V2 Connector/核验扩展 | **0.3 部分 + 0.4 部分 + 1.0** | 按能力拆入各版 |
| V3 长期稳定 | **1.0.0-stable** | 个人/团队生产 + 稳定插件 API（经 0.9 RC） |

---

## 全版本共同安全门

- 密钥与 `SECRET` 数据不得进入模型上下文或公开报告。
- 成功、阻塞、失败语义在报告与 `trace.jsonl` 中一致且可审计。
- `git diff --check` 与 CI lint/test 通过方可合并。
- 一个版本只有强制场景全部通过，才可作为下一版本的实现基线。

---

## 相关文档

| 文档 | 关系 |
|---|---|
| [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) | 0.1 验收清单 |
| [34-version-roadmap-0x.md](34-version-roadmap-0x.md) | 0.x 详细规格；**§6 = 0.5 PyPI**、**§10 = 0.9 RC 完整清单**、**§11 = 1.0 概要** |
| [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) | 历史 V1/V2/V3 实施细节（只读参考，顶注指向本文） |
| [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md) | 0.3 Adapter 技术细节 |
| [09-versions.md](09-versions.md) | 能力范围叙述（Legacy；冲突以本文为准） |
| [25-mini-run-path.md](25-mini-run-path.md) | 0.1 最小运行路径 |
| [33-version-roadmap.md](33-version-roadmap.md) | **权威** semver 路线图（含 0.4、0.6、**0.7 evaluation-benchmark**、0.8、0.9） |
| [21-test-fixtures-and-golden-cases.md](21-test-fixtures-and-golden-cases.md) | Golden 断言与 0.7 benchmark 对齐 |
| `docs/evaluation/`（0.7 规划） | 评测 harness、指标、模型对比、rubric-runner 集成 |
| `docs/plugins/`（0.6 规划） | 插件作者指南 |
| `docs/team/`（0.8 规划） | 团队协作、RBAC、Dashboard |
| `docs/evaluation/`（0.7 规划） | 评测与 benchmark 指南 |
| `docs/stability/`（0.9–1.0 规划） | api-freeze、deprecation-policy、security-review |

## Prompt 文件

| 文件 | 说明 |
|---|---|
| `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md` | 0.1 历史归档，勿覆盖 |
| `prompts/CURSOR_V1_MVP_IMPLEMENTATION_PROMPT.md` | **遗留文件名**；内容对应旧 V1 混合范围，实施时按 0.2→0.3→0.4 拆分 |
| `prompts/CURSOR_V2_IMPLEMENTATION_PROMPT.md` | 连接器/核验扩展，对照 0.3+ |
| `prompts/CURSOR_V3_IMPLEMENTATION_PROMPT.md` | 长期稳定，对照 1.0 |
