# 34 版本路线图（个人优先 · 0.1 → 1.3）

> **战略口径（2026-06-21）**：LoopPilot = **个人开发助手 + 论文推进器 + 信息筛选器 + 每日任务 OS**。0.x 主线是「**一个人每天真的能用**」；1.x 主线是「**先个人稳定，再受控协作，最后团队 preview**」。
>
> **与 [33-version-roadmap.md](33-version-roadmap.md) 的关系**：33 为 semver 标签索引（含历史 0.6–0.8 插件/团队规格，**部分已后移**）；**本文是 0.x 个人优先路线的权威执行规格**；**1.x 完整规格** → [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md)。冲突时：0.x 阶段边界与 0.4 四子阶段以本文为准；1.x 以 42 为准；semver 命名以 33 标签为准并见 [§16 Legacy 映射](#16-legacy-映射)。
>
> **0.4 详细规格** → [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)  
> **0.3 完成后行动项** → [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md)  
> **1.x 详细规格** → [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md)  
> **规划决策日志** → [logs/2026-06-21-personal-first-roadmap-pivot.md](logs/2026-06-21-personal-first-roadmap-pivot.md)、[logs/2026-06-21-1x-roadmap-personal-stable.md](logs/2026-06-21-1x-roadmap-personal-stable.md)

---

## 1. 版本总览

| 版本 | 名称 | 核心 | 状态 |
|------|------|------|------|
| **0.1** | Mini-MVP | 三条 fixture dry-run，MockAdapter only | ✅ 已完成 |
| **0.2** | Practical MVP | 受控 demo workspace，报告链路 | ✅ 已验收 `v0.2.0a1` |
| **0.3** | Adapter MVP | Mock→Real Adapter 安全接入，ToolBroker | 🔄 进行中 `v0.3.0a1`（分支 `adapter-mvp-0.3`） |
| **0.4** | **Personal Recovery & Daily Loop** | SQLite、inbox/queue/today、review、summary、schedule dry-run | 📋 下一焦点 |
| **0.5** | **Personal Beta** | `init personal`、个人配置、稳定日用、**可选** PyPI（换机安装） | 规划 |
| **0.6** | Personal Memory & Evaluation | 长期记忆、周报、效率指标 | 规划 |
| **0.7** | Personal Extensions | 本地 connector/skill，**非**公共插件市场 | 规划 |
| **0.8** | Optional Public Beta | 公开文档/示例，仍以个人为核心 | 规划 |
| **0.9** | Release Candidate | 冻结、审计、7 天长跑 | 规划 |
| **1.0** | Personal Stable | 单人长期稳定 semver 承诺 | 规划 |
| **1.1** | Personal Intelligence | 记忆、规划、优先级（非团队） | 规划 |
| **1.2** | Controlled Collaboration | 文件包协作、handoff（非云端账号） | 规划 |
| **1.3** | Team / Cloud Preview | 团队/云 preview only | 后置规划 |

```text
0.1 ──► 0.2 ──► 0.3 ──► 0.4 Personal Daily Loop
                              │
                              ▼
                    0.5 Personal Beta（可选 PyPI）
                              │
                              ▼
              0.6 Memory ──► 0.7 Extensions ──► 0.8 Optional Public
                              │
                              ▼
                    0.9 RC ──► 1.0 Personal Stable
                              │
                              ▼
                    1.1 Personal Intelligence
                              │
                              ▼
                    1.2 Controlled Collaboration
                              │
                              ▼
                    1.3 Team / Cloud Preview（0.x 不做；非 1.0 后立刻大团队版）
```

**当前聚焦**：收尾 **0.3 Adapter MVP**（`0.3.0a1` 已发布，验收见 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) 与 [logs/2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md)），随后进入 **0.4 Personal Recovery & Daily Loop**。

---

## 2. 产品定位（个人优先）

LoopPilot 不是「先开源再找人用」的团队工具，而是：

| 角色 | 说明 |
|------|------|
| **个人开发助手** | InternLoop：有限任务、测试验证、可审计 diff |
| **论文推进器** | PaperLoop：缺口诊断、证据核验、SOURCE REQUIRED 不编造 |
| **信息筛选器** | DailyNewsLoop：高价值信号 → Inbox，不凑数 |
| **每日任务 OS** | inbox / queue / today / review / summary 串联一天 |

**0.x 成功标准**：维护者（你）每天 30 分钟 × 3 Loop + 任务 OS，**无需团队功能**也能闭环。

---

## 3. 0.1 Mini-MVP ✅

### 目标

证明受控闭环在离线 fixture 下成立：编排、状态机、Policy Gate、Artifact Manifest、JSONL trace、Markdown 报告。

### 验收

- 三条 Loop Observe→Report；`doctor`、`pytest -q`、fixture dry-run 全绿
- `allow_real_adapters: false` 默认；无假 `resume/approve` 命令

详见 [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md)。

---

## 4. 0.2 Practical MVP ✅

### 目标

在 `examples/*_demo` 等受控 workspace 验证业务逻辑；Mock + dry-run 为主。

### 验收

- `v0.2.0a1` 已验收（2026-06-21）
- Intern/Paper/DailyNews demo profile 全绿

详见 [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md)。

---

## 5. 0.3 Adapter MVP 🔄

> **0.3 ≠ 旧称 V1**；只解决 Mock→Real Adapter 与受控真实运行，**不含** SQLite 日用链、inbox CLI、团队功能。

### 当前状态（2026-06-21）

| 项 | 状态 |
|----|------|
| 包版本 | `0.3.0a1`（`pyproject.toml`） |
| 分支 | `adapter-mvp-0.3` |
| 自动化验收 | 109 tests PASS；adapters list/doctor；默认 gate 拦截 real adapter |
| 待手动 | Cursor CLI doctor（无 PATH）；live API / live-small 源 |

### 目标

严格安全限制下 Real Adapter 生效：Cursor CLI、OpenAI-compatible、ToolBroker、ModelRouter 门控。

### 验收命令（摘要）

```bash
loop-pilot adapters list
loop-pilot adapters doctor
loop-pilot run intern --workspace examples/intern_demo --adapter cursor_cli --dry-run
# expect: blocked（allow_real_adapters=false）
pytest -q
```

详见 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)、[37-adapter-safety-policy.md](37-adapter-safety-policy.md)、[38-toolbroker-design.md](38-toolbroker-design.md)。

### 0.3 明确不做

| 不做 | 归属 |
|------|------|
| SQLite / resume / inbox CLI | **0.4** |
| PyPI / `init demo` 对外 onboarding | **0.5**（Personal Beta，非急 public） |
| 团队 / Dashboard / 云同步 | **1.3**（1.2 仅文件包协作） |

---

## 6. 0.4 Personal Recovery & Daily Loop 📋

> **详细规格**：[40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)

### 6.1 定位

| | **0.3 Adapter MVP** | **0.4 Personal Daily Loop** |
|---|---|---|
| 核心问题 | 真实 Adapter 能否安全跑通？ | **我能否每天靠它管任务、审结果、看总结？** |
| 状态 | JSON 可接受 | **SQLite 生产路径** |
| 任务 OS | 无 CLI | **inbox / queue / today** |
| 审阅 | Markdown 侧车 | **review list + approve/reject/defer/cancel** |
| 总结 | 单次 run 报告 | **summary today/week + daily-summary.md** |
| 调度 | 无 | **schedule print / install --dry-run** |

### 6.2 四子阶段（必须按序）

| 子阶段 | 名称 | 交付 |
|--------|------|------|
| **0.4-a** | 状态可靠 | `db status` / `migrate` / `backup` / `verify`；`recovery-scan` |
| **0.4-b** | 个人任务入口 | `inbox add/list`；`queue list/promote`；`today` |
| **0.4-c** | 个人审阅 | `review list`；`approve` / `reject` / `defer` / `cancel` |
| **0.4-d** | 每日总结 | `summary today` / `summary week`；`schedule print` / `install --dry-run` |

```text
0.4-a 状态可靠 ──► 0.4-b 任务入口 ──► 0.4-c 审阅 ──► 0.4-d 总结与调度
```

### 6.3 0.4 验收标准（10 项摘要）

1. SQLite 事务：中断无半写终态；migration 可重复
2. ACTING 中断 → 默认 BLOCKED；`recovery-scan` 可见
3. `resume` 合法 checkpoint 可恢复，不重复 artifact
4. inbox → queue → today 链路可审计
5. approve/reject/defer/cancel 写入 SQLite，trace 可审计
6. `run all` 每日链：单 Loop 失败不抹掉其他结果
7. `summary today` 产出 daily-summary.md（七段结构）
8. `schedule print` / `install --dry-run` 不写系统任务
9. `state_backend=json` 时 0.1 基线不退化
10. 锁与 stale run 可识别

### 6.4 0.4 明确不做

| 排除项 | 说明 |
|--------|------|
| 团队 / 多用户 / RBAC | **1.3** |
| Web Dashboard | **1.3 preview** |
| 云同步 / SaaS | **1.3 preview** |
| 文件包协作 / handoff | **1.2** |
| 插件市场 / 远程安装 | **0.7** 仅本地扩展；市场永不急 |
| PyPI onboarding / `init demo` 陌生人路径 | **0.5** 可选；**0.8** 公开文档 |
| 自动 push / PR / deploy | 全版本禁止 |

### 6.5 工作量估算

| 子阶段 | 人日（单人兼职） |
|--------|------------------|
| 0.4-a | 5–8 |
| 0.4-b | 4–6 |
| 0.4-c | 4–5 |
| 0.4-d | 4–6 |
| 集成测试 | 4–6 |
| **合计** | **21–31**（假设 0.3 已验收） |

---

## 7. 0.5 Personal Beta

> **口径变更（2026-06-21）**：0.5 从「Public Beta / 急 PyPI」调整为 **Personal Beta**——先保证**个人换机可装、配置可迁移、日用稳定**；PyPI 为**可选**，非 0.x 阻塞项。旧 Public Beta 规格见 [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md)（**已 supersede 部分口径**）。

### 目标

- `loop-pilot init personal`：生成个人目录骨架与 `loop-pilot.yaml`
- 个人配置模板：workspace、adapter 占位、schedule 关闭默认
- 连续 **7 天**个人日用无 P0（0.4 能力打包）
- **可选**：PyPI `0.5.0b1` 供换机 `pip install`（非必须对外推广）

### 与旧 0.5 Public Beta 对比

| 维度 | 旧 Public Beta（2026-06-20） | 新 Personal Beta |
|------|------------------------------|------------------|
| 首要受众 | 外部陌生人 10 分钟跑通 | **维护者本人**换机/备份恢复 |
| PyPI | 必须 | **可选** |
| CONTRIBUTING / CoC | 必须全套 | 0.8 Optional Public 再补 |
| `init demo` | 陌生人 demo | `init personal` 个人骨架 |
| 阻塞 0.6 | 是 | 否（日用稳定即可进 0.6） |

---

## 8. 0.6 Personal Memory & Evaluation

### 目标

- 跨日记忆：昨日 next action、审批决定、Inbox 遗留关联
- 周报：`summary week` 扩展为结构化周报
- 效率指标：任务完成率、Loop 耗时、Adapter 费用摘要（本地）

### 不做

- 公开 benchmark 排行榜
- 团队共享 eval registry（**1.3**）

旧 0.7 evaluation-benchmark 部分能力并入此处（个人 scope）；详见 33 文档历史 §0.7 作参考。

---

## 9. 0.7 Personal Extensions

### 目标

- 本地 connector / skill 注册（**非**公共插件市场）
- `loop-pilot plugins list`（本地目录 only）
- 个人 manifest + Policy 权限声明

### 不做

- 在线插件市场 / `plugins install <url>`
- 团队插件策略（**1.3**）

旧 0.6 plugin-ecosystem 规格缩小为个人本地扩展；完整框架可参考 [33-version-roadmap.md §0.6](33-version-roadmap.md)（历史）。

---

## 10. 0.8 Optional Public Beta

### 目标

- 公开 getting-started、示例、CHANGELOG（仍以**个人用户**叙事）
- **可选** PyPI 稳定 beta
- CONTRIBUTING / SECURITY 对外协作文件

### 不做

- 团队 onboarding
- Dashboard / 多项目 workspace

旧「0.5 必做 PyPI」能力**移至此阶段可选**；不阻塞 0.4–0.7 个人主线。

---

## 11. 0.9 Release Candidate · 1.0 Personal Stable

### 0.9

- API / 配置 / DB migration **冻结**
- conformance 测试、安全审计、7 天模拟长跑
- **仅 bugfix**，不加功能

### 1.0

- **Personal Stable**：单人长期 semver 承诺
- 必备：0.4 日用链 + 0.3 Adapter + 0.6 记忆 + 0.7 本地扩展（GA）
- **不含**团队能力（团队见 **1.3 preview**；受控协作见 **1.2**）

详见 [logs/2026-06-20-0.9-release-candidate-spec.md](logs/2026-06-20-0.9-release-candidate-spec.md)（团队相关条目见 **1.2/1.3** 注记）。

---

## 12. 1.x 总览（Personal Stable → Controlled Collaboration）

> **2026-06-21 决策**：1.x 不再使用笼统「1.1+ Team / Cloud」；细化为四段式。**完整规格** → [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md)。

| 版本 | 名称 | 核心 | 与旧规划 |
|------|------|------|----------|
| **1.0** | Personal Stable | 接口冻结；30 天日用；个人 semver | 原 33 §1.0；**不含**团队 |
| **1.1** | Personal Intelligence | 记忆、规划、优先级、主动建议 | 承接 0.6；**非团队** |
| **1.2** | Controlled Collaboration | 文件包 export/import、handoff | 旧 0.8 协作子集；**无**云端账号 |
| **1.3** | Team / Cloud Preview | RBAC、sync、Dashboard preview | 旧 **0.8 team-cloud** → **deprecated**，迁此 |

**推进顺序**：1.0 个人稳定 → 1.1 个人智能 → 1.2 受控协作 → 1.3 团队/云 preview。  
**禁止**：1.0 后立刻做大团队版 / 完整 SaaS。

```text
0.9 RC ──► 1.0 ──► 1.1 ──► 1.2 ──► 1.3
           稳定    智能    文件包    team preview
```

### 12.1 Legacy：旧 0.8 team-cloud → 1.2 / 1.3

| 能力 | 原规划（33 §0.8，**deprecated @ 0.8**） | 新归属 |
|------|----------------------------------------|--------|
| 多项目 workspace | 0.8 team-cloud | **1.3** |
| RBAC / 共享审批 | 0.8 | **1.3** |
| 本地 Dashboard :7860 | 0.8 | **1.3 preview** |
| 团队插件策略 | 0.8 | **1.3** |
| 文件包报告 export | — | **1.2** |
| handoff / 协作者 profile | — | **1.2** |
| Cloud SaaS | 永不（local-first 原则不变） | — |

历史规格仍可读：[33-version-roadmap.md §0.8](33-version-roadmap.md)（标注 **legacy / 1.2–1.3 候选**）。

---

## 13. 完成度与短板分析（2026-06-21）

| 里程碑 | 完成度（估） | 主要短板 |
|--------|-------------|----------|
| **0.1** | 100% | — |
| **0.2** | 100% | — |
| **0.3** | ~85% | Cursor CLI 手动验收；live API/源；DailyNews live-small |
| **0.4** | ~15%（WIP 骨架） | 无 inbox/queue/today CLI；SQLite schema 不完整；无 summary week |
| **0.5** | 0% | 无 `init personal`；无个人配置迁移 story |
| **0.6–0.8** | 文档 only | 记忆/扩展/公开文档均未实现 |
| **1.0** | 0% | 依赖 0.4–0.9 链 |

**关键路径**：0.3 收尾（手动层）→ **0.4-a** SQLite 可靠 → **0.4-b** 任务 OS → 0.4-c/d → 0.5 个人 beta。

**最大风险**：

1. 0.4 范围膨胀（团队功能回流）——用 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) 锁定不做项
2. 过早 PyPI/开源分散精力——PyPI 降为 0.5 可选 / 0.8 公开
3. 0.3 未验收即接 schedule 主链——必须先完成 0.4-a

---

## 14. 阶段推进规则

1. **顺序推进**：0.1 → … → 0.9 → **1.0 → 1.1 → 1.2 → 1.3**；Team/Cloud **仅在 1.3 preview**
2. **测试门禁**：每阶段强制场景全绿才进下一阶段
3. **文档先行**：先改本文 + 40/41，再改代码
4. **Mini 基线不退化**：每阶段后 0.1 fixture 仍 PASS
5. **个人日用验收**：0.4 起每阶段需「维护者自用 1 天」记录（可写 logs）

---

## 15. 相关文档

| 文档 | 关系 |
|------|------|
| [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) | 0.1 验收记录 |
| [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md) | 0.2 验收记录（2026-06-21） |
| [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) | **0.3 验收清单** |
| [37-adapter-safety-policy.md](37-adapter-safety-policy.md) | 0.3 Adapter 安全策略 |
| [38-toolbroker-design.md](38-toolbroker-design.md) | 0.3 ToolBroker 设计 |
| [39-next-steps-0.3.md](39-next-steps-0.3.md) | **0.3 开发 Phase 1–8** |
| [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) | **0.4 权威规格** |
| [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) | 0.3→0.4 行动顺序 |
| [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) | **1.x 权威规格**（1.0–1.3） |
| [33-version-roadmap.md](33-version-roadmap.md) | semver 索引（含历史 0.6–0.8 详细规格） |
| [33-next-steps-0.2.md](33-next-steps-0.2.md) | 0.2 行动项（已完成） |
| [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) | Legacy V1/V2/V3 任务分解 |
| [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md) | 0.3 Adapter/Router 技术细节 |
| [25-mini-run-path.md](25-mini-run-path.md) | 0.1→0.3 最小路径 |
| [09-versions.md](09-versions.md) | Legacy 能力描述；冲突以本文为准 |
| [logs/2026-06-21-personal-first-roadmap-pivot.md](logs/2026-06-21-personal-first-roadmap-pivot.md) | 0.x pivot 决策 |
| [logs/2026-06-21-1x-roadmap-personal-stable.md](logs/2026-06-21-1x-roadmap-personal-stable.md) | 1.x 决策 |
| [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md) | 0.5 规划决策日志 |

## 16. Legacy 映射

### 16.1 旧版本名 → 新 0.x（个人优先）

| 旧称呼 | 新编号 | 说明 |
|--------|--------|------|
| Mini | **0.1** | 已完成 |
| V1 真实 workspace | **0.2** + **0.3** | 配置 vs Adapter |
| V1 SQLite/recovery/scheduler | **0.4** | Personal Daily Loop |
| V1 PyPI / 开源 README | **0.5 可选** + **0.8 公开** | 不再急 public beta |
| V2 Connector/核验 | **0.3** + **0.6** + **1.0** | 拆分 |
| V3 长期稳定 | **1.0 Personal Stable** | |
| 0.8 team-cloud（旧） | **1.2 + 1.3** | **移出 0.x**；team 细节 → 1.3 |
| 1.1+ Team / Cloud（旧 34 §12） | **1.1–1.3 四段式** | 见 [42-1x-roadmap](42-1x-roadmap-personal-to-collaboration.md) |
| 0.6 plugin-ecosystem（旧） | **0.7 Personal Extensions** | 缩小为本地 |
| 0.7 evaluation（旧） | **0.6 Memory & Evaluation** | 个人 scope |

### 16.2 2026-06-20 → 2026-06-21 路线图差异（摘要）

| 项 | 旧（2026-06-20） | 新（2026-06-21 个人优先） |
|----|------------------|---------------------------|
| 0.4 名称 | Recovery & Automation | **Personal Recovery & Daily Loop**（+ inbox/queue/today） |
| 0.5 | Public Beta（必 PyPI） | **Personal Beta**（PyPI 可选） |
| 0.6 | Plugin ecosystem | **Personal Memory & Evaluation** |
| 0.7 | Evaluation benchmark | **Personal Extensions** |
| 0.8 | Team-cloud preview | **Optional Public Beta** |
| Team/Dashboard | 0.8 必达 | **1.3 preview** 后置 |
| 1.x 结构 | 1.1+ 笼统 | **1.0→1.1→1.2→1.3** 四段式 |
| 0.x 目标 | 工具型开源/团队 | **一个人每天真的能用** |
