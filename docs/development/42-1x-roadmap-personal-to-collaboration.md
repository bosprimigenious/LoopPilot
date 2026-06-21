# 42 1.x 路线图：Personal Stable → Controlled Collaboration

> **版本标签**：`1.0.0-personal-stable` → `1.3.0-team-cloud-preview`  
> **上级路线图**：[34-version-roadmap-0x.md](34-version-roadmap-0x.md)（0.x 权威；本文是 **1.x 权威**）  
> **前置条件**：0.9 Release Candidate 通过；0.4 日用链见 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)（1.0 验收的 0.x 基础）  
> **决策日志**：[logs/2026-06-21-1x-roadmap-personal-stable.md](logs/2026-06-21-1x-roadmap-personal-stable.md)

---

## 1. 战略口径

LoopPilot 在 **0.x** 阶段完成从原型到**个人可用系统**的演进。  
**1.x** 阶段不再追求快速堆功能，而是围绕**稳定性、长期个人使用、受控协作和可持续扩展**逐步推进。

### 1.1 核心原则

1. **1.0 之前**不承诺稳定接口。
2. **1.0 之后**配置、状态、Artifact、CLI 行为需要保持兼容（1.x additive-only；breaking → 2.0）。
3. **团队协作不应早于个人使用稳定性**——不建议跳过 1.0 / 1.1 直接做团队版。
4. **云端能力不应早于本地安全模型**。
5. **所有自动化能力**都必须可审计、可暂停、可恢复。

### 1.2 与 0.x 的衔接

| 0.x 阶段 | 1.x 承接 |
|----------|----------|
| 0.4 Personal Daily Loop | 1.0 稳定 CLI / inbox / queue / today / review / summary |
| 0.5 Personal Beta | 1.0 换机安装与配置迁移 |
| 0.6 Personal Memory & Evaluation | **1.1** 长期记忆、规划、优先级（0.6 为 1.1 前置） |
| 0.7 Personal Extensions | 1.0 本地扩展 GA；1.1+ 增强 |
| 0.8 Optional Public Beta | 1.0 文档与 PyPI 稳定承诺 |
| 0.9 Release Candidate | 1.0 接口冻结毕业 |
| 旧 **0.8 team-cloud**（[33-version-roadmap.md §0.8](33-version-roadmap.md)） | **deprecated** → 能力拆分至 **1.2**（受控协作）与 **1.3**（团队/云 preview） |

---

## 2. 总览

| 版本 | 名称 | 核心目标 | 状态 |
|------|------|----------|------|
| **1.0** | Personal Stable | 单人长期稳定使用，本地优先，接口冻结 | 规划 |
| **1.1** | Personal Intelligence | 强化个人记忆、跨 Loop 规划、长期任务推进 | 规划 |
| **1.2** | Controlled Collaboration | 受控协作：少量可信协作者、文件包 handoff | 规划 |
| **1.3** | Team / Cloud Preview | 团队工作区、云端同步、多人权限的 **preview only** | 后置规划 |

```text
0.9 RC ──► 1.0 Personal Stable
                │
                ▼
           1.1 Personal Intelligence
                │
                ▼
           1.2 Controlled Collaboration
                │
                ▼
           1.3 Team / Cloud Preview（preview only，非 GA 团队版）
```

**推进顺序**：先个人稳定 → 个人增强 → 受控协作 → 团队预览。  
**禁止**：1.0 后立刻做大团队版 / 完整 SaaS。

---

## 3. 1.0 Personal Stable

**版本标签**：`1.0.0-personal-stable`

### 3.1 定位

1.0 是 LoopPilot 的**第一个稳定版本**。它不追求团队化，也不追求复杂云端能力，而是证明 LoopPilot 已经可以作为**个人长期使用的 AI 工作循环系统**。

**1.0 的目标**：

- 一个人可以**连续使用 LoopPilot 30 天以上**
- 每天运行开发、论文、信息流任务
- 系统能**恢复、能总结、能审阅、能继续昨天的工作**
- 不会因为状态损坏、配置混乱、Adapter 失控而中断

### 3.2 核心能力

1.0 必须完成：

| 域 | 能力 |
|----|------|
| CLI | 稳定命令面（见 §3.3） |
| 配置 | 稳定 `loop-pilot.yaml` 与 Loop 专用配置；`schema_version` |
| 状态 | 稳定 SQLite StateStore；migration additive-only |
| 产物 | 稳定 Artifact Manifest |
| Adapter | 稳定 Adapter 协议；默认 gate |
| 工具 | 稳定 ToolBroker 策略 |
| 任务 OS | 稳定 Inbox / Queue / Today / Review / Summary |
| 恢复 | 稳定 `resume` / `cancel` / `approve` / `reject` / `defer` |
| 调度 | 稳定个人调度配置 |
| 报告 | 稳定 `summary today` / `summary week` |
| 备份 | 稳定本地备份与恢复 |
| 安全 | 稳定安全默认值 |

### 3.3 主要命令

```bash
loop-pilot doctor
loop-pilot today
loop-pilot inbox add "..."
loop-pilot inbox list
loop-pilot queue list          # 与 today 配合；见 0.4 规格
loop-pilot run all --profile personal --dry-run
loop-pilot review list
loop-pilot approve <run-id>
loop-pilot reject <run-id> --reason "..."
loop-pilot defer <run-id> --until tomorrow
loop-pilot resume <run-id>
loop-pilot summary today
loop-pilot summary week
loop-pilot recovery-scan
loop-pilot db backup
loop-pilot db verify
```

> **Cross-ref**：上述 inbox/queue/today/review/summary 命令的 0.x 实现规格见 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)；1.0 验收在此基础上增加 **30 天日用**与 **semver 稳定承诺**。

### 3.4 验收标准

1.0 可以发布的条件：

1. 0.1–0.9 所有核心回归命令通过
2. **连续 30 天**个人使用不出现不可恢复状态损坏
3. SQLite 状态可备份、可验证、可迁移
4. 所有真实 Adapter 调用都有 trace
5. 所有写入都经过 ToolBroker
6. API key、token、隐私内容不会进入公开 Artifact
7. `today` 能准确展示当前任务状态
8. `summary today` 和 `summary week` 能形成可读报告
9. `resume` 不会重复危险动作
10. ACTING 阶段失败默认进入人工审阅
11. 文档说明当前稳定承诺和不稳定边界

**验收命令（摘要）**：

```bash
pytest -q && pytest conformance/ -q
loop-pilot doctor
loop-pilot today
loop-pilot summary today
loop-pilot summary week
loop-pilot recovery-scan
loop-pilot db backup --dry-run
loop-pilot db verify
loop-pilot run all --profile personal --dry-run
```

### 3.5 明确不做

| 排除项 | 说明 |
|--------|------|
| 团队成员系统 | **1.2+** |
| 组织空间 | **1.3 preview** |
| 云端同步 | **1.3 preview** |
| 多人权限 / 复杂 RBAC | **1.3 preview** |
| Web Dashboard | **1.3 preview** |
| 插件市场 | 非 1.x 急项 |
| 公共 SaaS | 永不（local-first） |
| 多用户计费 | 永不 |

**1.0 的核心是个人稳定，而不是团队平台。**

---

## 4. 1.1 Personal Intelligence

**版本标签**：`1.1.0-personal-intelligence`

### 4.1 定位

1.1 在 1.0 稳定基础上增强**个人智能**能力。目标不是增加更多 Adapter，而是让 LoopPilot 更懂你的长期目标、项目脉络和任务优先级。

**1.1 的目标**：

- LoopPilot 不只是每天跑任务
- 还能够**记住长期目标、项目状态、任务历史**
- 并**主动建议**下一步最值得推进的工作

> **与 0.6 关系**：0.6 Personal Memory & Evaluation 提供基础跨日记忆与周报；1.1 在此基础上增加规划、优先级与主动建议。

### 4.2 核心能力

| 能力 | 说明 |
|------|------|
| 长期个人记忆 | 项目目标、blocked 原因、偏好、高价值源 |
| 项目状态摘要 | 按 project 聚合进展 |
| 跨 Loop 任务规划 | DailyNews → Paper → Intern 链路 |
| 任务优先级排序 | 多因素排序（见 §4.4） |
| 失败模式分析 | 常见失败与重复 blocked |
| 每周趋势报告 | `summary week` 扩展为趋势而非流水账 |
| 个人目标追踪 | 长期 OKR / 目标条目 |
| 项目级上下文索引 | 本地索引，非向量库依赖 |
| 重复任务识别 | 去重与合并建议 |
| 低价值任务过滤 | Inbox 噪声抑制 |

### 4.3 建议模块

```text
src/loop_pilot/memory/
src/loop_pilot/planning/
src/loop_pilot/prioritization/
src/loop_pilot/metrics/
```

### 4.4 主要命令

```bash
loop-pilot memory status
loop-pilot memory rebuild
loop-pilot project status
loop-pilot project summarize <project-id>
loop-pilot plan today
loop-pilot plan week
loop-pilot metrics week
loop-pilot metrics month
loop-pilot suggest next
```

### 4.5 关键能力说明

#### 个人记忆

记录：

- 项目目标、最近任务、blocked 原因、已完成工作
- 常见失败、常用 workspace、常用 Adapter
- 个人偏好、高价值信息源

#### 跨 Loop 规划（示例）

```text
DailyNewsLoop 发现相关 benchmark
  → 写入 paper_queue
  → PaperLoop 生成阅读任务
  → InternLoop 生成实现实验任务
  → Summary 汇总进展
```

#### 个人优先级

排序依据：

- 当前项目重要性、截止时间
- 最近失败次数、预计完成成本
- 对论文/项目推进价值
- 是否可由 Adapter 自动完成、是否需要人工决策

### 4.6 验收标准

1. `loop-pilot suggest next` 能给出合理的下一步任务
2. `loop-pilot plan today` 能从 inbox、queue、recent runs 中生成今日计划
3. `loop-pilot project status` 能总结指定项目状态
4. `summary week` 能展示**趋势**，而不只是流水账
5. 系统能识别重复任务和长期 blocked 任务
6. 个人记忆可重建，不依赖单一不可恢复文件
7. 记忆系统不会泄露 secrets
8. **1.0 的稳定命令全部保持兼容**

### 4.7 明确不做

| 排除项 | 说明 |
|--------|------|
| 多人共享记忆 | **1.2+** |
| 团队知识库 | **1.3** |
| 云端同步 | **1.3** |
| Web Dashboard | **1.3 preview** |
| 复杂向量数据库依赖 | 非 1.1 必达 |
| 公开插件市场 | 非急项 |

**1.1 仍然是个人系统。**

---

## 5. 1.2 Controlled Collaboration

**版本标签**：`1.2.0-controlled-collaboration`

### 5.1 定位

1.2 开始支持**有限协作**，但不是完整团队版。它只面向**少量可信协作者**——例如你和一两个朋友、同学、项目合作者之间的共享审阅和任务交接。

**1.2 的目标**：

- 在不破坏**本地优先**和**个人控制权**的前提下
- 允许少量协作者查看报告、提出 review、接收任务或贡献反馈

> **与旧 0.8 team-cloud 差异**：旧 0.8 含 RBAC、Dashboard、多项目 workspace；1.2 **仅**文件包协作 + handoff，**无**云端账号。完整团队能力见 **1.3**。

### 5.2 核心能力

| 能力 | 说明 |
|------|------|
| 共享报告导出 | redacted 协作包 |
| 只读协作包 | Markdown + manifest + 脱敏 trace |
| Review comment 导入 | 外部 review 合并 |
| 任务交接记录 | handoff create/accept |
| Collaborator profile | 本地协作者目录 |
| 手动同步机制 | 文件交换，非实时 |
| 协作审计日志 | 导入/导出/ handoff 事件 |
| 外部反馈合并 | 人工确认后写入 |

### 5.3 建议模块

```text
src/loop_pilot/share/
src/loop_pilot/collaboration/
src/loop_pilot/handoff/
```

### 5.4 主要命令

```bash
loop-pilot share export <run-id>
loop-pilot share export-summary --week
loop-pilot review import comments.md
loop-pilot collaborator add <name>
loop-pilot collaborator list
loop-pilot handoff create <task-id>
loop-pilot handoff accept <handoff-id>
loop-pilot audit collaboration
```

### 5.5 协作方式（文件包，非云端）

1.2 **不直接做云端账号**。采用文件包方式：

```text
share/
├── run-report.md
├── artifact-manifest.json
├── review-template.md
├── redacted-trace.jsonl
└── handoff.md
```

协作者可以看 Markdown、填写 review，再由你**手动导入**。

### 5.6 安全原则

| 原则 | 说明 |
|------|------|
| 默认脱敏 | 只导出 redacted artifact |
| 密钥隔离 | 不导出 API key、`.env`、私有路径 |
| Transcript | 不导出完整 Adapter transcript，除非显式 `--include-transcript` |
| 人工确认 | 所有导入的 review 都需要人工确认 |
| 无远程执行 | 协作者**不能**直接触发本机 Adapter |

### 5.7 验收标准

1. `share export` 能生成可读协作包
2. 协作包**默认脱敏**
3. `review import` 能导入外部评论
4. `handoff` 能记录任务交接状态
5. 协作日志可审计
6. 协作者不能绕过本地 ToolBroker
7. 协作功能**不影响**个人单机使用
8. **1.0 和 1.1 核心命令保持兼容**

### 5.8 明确不做

| 排除项 | 说明 |
|--------|------|
| 云端账号 | **1.3 preview** |
| Web 多人登录 | **1.3** |
| 实时协作 | 非 1.2 |
| 团队权限系统 / 复杂 RBAC | **1.3** |
| 在线审批流 | **1.3** |
| SaaS 部署 | 永不 |
| 多租户隔离 | **1.3 preview** |

**1.2 是受控协作，不是团队平台。**

---

## 6. 1.3 Team / Cloud Preview

**版本标签**：`1.3.0-team-cloud-preview`

### 6.1 定位

1.3 才开始探索真正的团队和云端能力。但 1.3 仍然只是 **preview**，不是稳定团队版。

**1.3 的目标**：

- 在 1.0 个人稳定与 1.2 受控协作已经成熟的基础上
- 探索团队工作区、云端同步、多人权限和共享任务队列

> **历史规格**：旧 [33-version-roadmap.md §0.8](33-version-roadmap.md) team-cloud 详细命令（`project create`、RBAC、Dashboard `:7860` 等）作为 **1.3 设计参考**，标注 **deprecated @ 0.8**。

### 6.2 核心能力（preview scope）

| 能力 | 说明 |
|------|------|
| Team workspace | 项目列表、共享队列、共享报告 |
| Cloud sync prototype | 仅 metadata / 脱敏 artifact |
| User role | owner / maintainer / reviewer / viewer（最小集） |
| Shared queue / review | 团队可见队列与审阅 |
| Team summary | 团队周报 |
| Remote artifact store | 脱敏产物远程索引（preview） |
| Team audit log | 成员操作审计 |
| Basic dashboard | 本地 `:7860` preview |
| Multi-device sync | dry-run 默认 |

### 6.3 Team Workspace 概念

团队空间包含：

- 项目列表、共享队列、共享报告
- 成员角色、审阅记录、团队 summary、审计日志

#### 最小角色（不要一开始做复杂 RBAC）

| 角色 | 能力摘要 |
|------|----------|
| **owner** | 项目创建、成员管理、全部 run/approve |
| **maintainer** | 配置、run all、审批 |
| **reviewer** | 查看 artifact、`approve` / `reject` |
| **viewer** | 只读 |

### 6.4 云端同步（preview only）

**同步对象**（限制）：

- run metadata、summary、redacted artifact
- review decision、queue item、handoff item

**不应同步**：

- API key、`.env`、原始私有代码
- 未脱敏 Adapter transcript、本地绝对路径、大型 raw artifact

### 6.5 主要命令

```bash
loop-pilot team init
loop-pilot team status
loop-pilot team member list
loop-pilot team queue list
loop-pilot team sync --dry-run
loop-pilot team summary week
loop-pilot cloud doctor
```

### 6.6 建议模块

```text
src/loop_pilot/team/
src/loop_pilot/cloud/
src/loop_pilot/dashboard/          # :7860 preview
docs/team/                         # 部署与 RBAC 说明（自旧 0.8 迁移）
```

### 6.7 验收标准（preview 发布门槛）

1. **单人模式**不受团队功能影响
2. team 功能**默认关闭**
3. cloud sync **默认 dry-run**
4. 所有同步数据**默认脱敏**
5. 成员权限不会绕过本地安全策略
6. `team queue list` 能展示共享任务
7. `team summary week` 能生成团队周报
8. audit log 能记录成员操作
9. **1.0–1.2 命令全部兼容**

### 6.8 明确不做

| 排除项 | 说明 |
|--------|------|
| 正式 SaaS | preview only |
| 公开云服务 | local-first 不变 |
| 企业级权限 / SSO | → 2.0 候选 |
| 计费系统 | 永不 |
| 多租户生产隔离 | preview 不承诺 |
| 完整 Web 平台 | CLI 仍为控制面 |
| 大规模团队管理 | 非 1.3 目标 |

**1.3 只是团队和云端方向的技术预览。**

---

## 7. 1.x 总体路线与推进规则

### 7.1 推进顺序

```text
1.0 个人稳定 → 1.1 个人智能 → 1.2 受控协作 → 1.3 团队/云端预览
```

**不建议**跳过 1.0 和 1.1 直接做团队版。

**原因**：如果一个人都不能稳定每天使用，团队版只会放大复杂度。

### 7.2 阶段门禁

| 规则 | 说明 |
|------|------|
| 顺序推进 | 1.0 → 1.1 → 1.2 → 1.3；不可跳级 |
| 兼容门禁 | 每 minor 版本 1.0 基线命令全绿 |
| 个人日用 | 1.0 需 30 天日志；1.1+ 需维护者自用记录 |
| 文档先行 | 先改本文 + 34，再改代码 |
| Mini 不退化 | 每阶段后 0.1 fixture 仍 PASS |

### 7.3 与 2.0 边界

- **1.x**：additive only；个人 → 受控协作 → team preview
- **2.0**：破坏性 API / config / DB 变更；可选企业 SSO、托管协作、插件 registry（若产品确认）

---

## 8. 术语表（中英）

| 中文 | English | 版本 |
|------|---------|------|
| 个人稳定版 | Personal Stable | 1.0 |
| 个人智能 / 个人增强 | Personal Intelligence | 1.1 |
| 受控协作 | Controlled Collaboration | 1.2 |
| 团队/云端预览 | Team / Cloud Preview | 1.3 |
| 文件包协作 | File-pack collaboration | 1.2 |
| 任务交接 | Handoff | 1.2 |
| 接口冻结 | API freeze | 0.9 → 1.0 |
| 本地优先 | Local-first | 全版本 |

---

## 9. 相关文档

| 文档 | 关系 |
|------|------|
| [34-version-roadmap-0x.md](34-version-roadmap-0x.md) | 0.x + §1.x 总览 |
| [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) | 1.0 验收的 0.4 基础 |
| [33-version-roadmap.md](33-version-roadmap.md) | semver 索引；§0.8 team-cloud **deprecated → 1.2/1.3** |
| [logs/2026-06-21-personal-first-roadmap-pivot.md](logs/2026-06-21-personal-first-roadmap-pivot.md) | 0.x 个人优先 pivot |
| [logs/2026-06-21-1x-roadmap-personal-stable.md](logs/2026-06-21-1x-roadmap-personal-stable.md) | 1.x 决策日志 |
