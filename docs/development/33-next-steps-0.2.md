# 33 下一步行动：先完成 0.1，再进入 0.2

本文将原「V1 任务清单」重映射到 **0.2 / 0.3 / 0.4**，并明确**当前应聚焦 0.1 Mini-MVP 收尾**。

> 版本体系权威定义见 [34-version-roadmap-0x.md](34-version-roadmap-0x.md)。**0.3 ≠ V1**；不要现在冲 0.3。

## 1. 当前阶段与优先级

```
[已完成] 0.1 mini  ←── Phase A 验收通过（2026-06-21）
    ↓
[已完成] 0.2 practical-mvp  ←── v0.2.0a1 验收通过（2026-06-21）
    ↓
[下一步] 0.3 adapter-mvp  ←── 见 [39-next-steps-0.3.md](39-next-steps-0.3.md)
    ↓
[之后]   0.4 recovery-and-automation
    ↓
[远期]   0.5 public-beta
    ↓
[远期]   0.6 plugin-ecosystem
    ↓
[远期]   0.7 evaluation-benchmark
    ↓
[远期]   0.8 team-cloud-preview
    ↓
[远期]   0.9 release-candidate  （冻结 / 测试 / 文档定稿，不加功能）
    ↓
[目标]   1.0 stable               （正式稳定承诺）
```

**完整 0.1–1.0 路线图**见 [34-version-roadmap-0x.md](34-version-roadmap-0x.md) §1 总览表；**0.9 RC 完整规格**见同文档 §10。

**原则**：0.1/0.2 已全部验收；**0.3 在 `adapter-mvp-0.3` 分支启动**（0.2 tag 之后）；0.6–0.9 均为文档规划，**不得提前实现**。

## 2. 0.1 完成情况（2026-06-21）

对照 [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) 与 [logs/2026-06-20-mini-mvp-delivery.md](logs/2026-06-20-mini-mvp-delivery.md)：

| # | 任务 | 状态 | 验收 |
|---|------|------|------|
| 1 | PaperLoop SOURCE_REQUIRED → `partial` | ✅ | `run paper --fixture unsupported_claim` → partial |
| 2 | DailyNews 候选路由产物 | ✅ | intern/paper candidates + candidate-actions.json |
| 3 | `allow_real_adapters` 默认 false | ✅ | Router/Registry 阻止 cli/api |
| 4 | pyproject extras 清理 | ✅ | 无自引用 `all` |
| 5 | GitHub Actions CI | ✅ | ruff + pytest + doctor + dry-run |
| 6 | 异常 traceback Artifact | ✅ | error-traceback.txt + 脱敏 |
| 7 | README Mini-MVP 状态 | ✅ | 验收命令块 |
| 8 | 全量验证 | ✅ | 93 passed + CLI 全绿 |

**0.1 完成定义**：上述八项全部通过 + CI 绿 + 交付日志已归档。

## 3. 原「V1 任务」→ 0.x 重映射

以下条目摘自 32 文档「遗留 V1 任务」及 31 文档，按新体系拆分：

| 原 V1 任务 | 目标版本 | 说明 |
|------------|----------|------|
| CLI：`resume`, `approve`, `reject`, `cancel`, `report` | **0.4** | 依赖 SQLite + approval 协议 |
| SQLite recovery 与跨进程锁 | **0.4** | 非 0.3 范围 |
| `CodingCLIAdapter` / `APIModelAdapter` 真实接入 | **0.3** | Real Adapter MVP 核心 |
| ModelRouter 能力路由 | **0.3** | 与 Adapter 同步 |
| ToolBroker | **0.3** | Agent 不得绕过 |
| 真实 Intern/Paper workspace 配置与边界 | **0.2** | dry-run/report；0.3 再加 real adapter |
| DailyNews 在线源 / `--real-sources` | **0.3** | 0.2 用快照/fixture |
| worktree 生命周期、测试链 | **0.2**（逻辑）+ **0.3**（真实 CLI 驱动） | |
| PolicyEngine 生产化 | **0.2** 基础 + **0.3** 与 Adapter 联动 | |
| OS 调度安装 | **0.4** | `install_scheduler.py` |
| PyPI 发布 | **0.5** | |
| `run all` 真实每日链 | **0.4** | 需 recovery + scheduler |
| Inbox 双通道、候选过期 | **0.2**（结构）+ **0.3**（真实源填充） | |
| GitHub star 增量排名 | **0.3**（真实源）+ **1.0**（完善） | |

## 4. 0.2 Practical MVP 预备任务清单

0.1 完成后按此顺序启动（**仍不使用 Real Adapter**）：

### 4.1 配置与 workspace

- [ ] `config/loop-pilot.yaml` 支持 `intern.workspace`、`paper.workspace`、`allowed_paths`、`forbidden_paths`
- [ ] Intern validation 命令数组（pytest 等）可配置
- [ ] Paper `main_document`、`bibliography`、`modifiable_sections` 配置
- [ ] CLI：`--workspace` 覆盖配置；`--dry-run` 默认 true

### 4.2 InternLoop（0.2）

- [ ] 真实仓库 observe：读测试失败、昨日 next action
- [ ] worktree 创建/清理；用户未提交改动检测
- [ ] 测试链执行（模型输出仍可用 MockAdapter）
- [ ] diff review：越界路径 → BLOCKED
- [ ] `--allow-write` 显式开启有限写入

### 4.3 PaperLoop（0.2）

- [ ] 真实论文副本读取与修订 diff（Mock 驱动 writing）
- [ ] 引用 key / BibTeX / claim-evidence 检查
- [ ] SOURCE REQUIRED 语义与 0.1 fixture 一致

### 4.4 DailyNewsLoop（0.2）

- [ ] 离线快照 / fixture 扩展为「真实路径快照」
- [ ] Inbox 写入：intern-candidates、paper-candidates
- [ ] 去重、置信度门槛

### 4.5 测试与文档

- [ ] `tests/unit/test_v1_workspaces.py` 或等价 0.2 workspace 测试
- [ ] 更新 32 → 新建 0.2 验收记录（待 0.2 完成时）
- [ ] README 指向 0.2 验收命令

### 4.6 0.2 验收命令（目标）

```bash
loop-pilot doctor
loop-pilot run intern --workspace /path/to/repo --dry-run
loop-pilot run paper --workspace /path/to/paper --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --dry-run
pytest -q
```

## 5. 0.3 / 0.4 预告（勿提前实施）

### 0.3 入口条件

- 0.2 全部验收通过
- BaseAdapter 协议设计评审（见 30、34 文档）
- `allow_real_adapters` 门控与 CLI 双重确认就绪

### 0.3 首批任务（届时执行）

1. MockAdapter 完整化 + AdapterRegistry
2. ModelRouter 能力路由
3. ToolBroker 最小实现
4. CodingCLIAdapter（Cursor CLI）
5. OpenAICompatibleAdapter
6. `adapters list` / `adapters doctor`
7. Intern/Paper/DailyNews 受控真实 run

详见 [34-version-roadmap-0x.md §4](34-version-roadmap-0x.md#4-03-real-adapter-mvp030-adapter-mvp)。

### 0.4 入口条件

- 0.3 全部验收通过
- SQLite schema 与 migration 设计评审

0.4 任务：StateStore SQLite、checkpoint/recovery、approval CLI、scheduler、每日真实链。

## 7. 0.5 Public Beta 预览 checklist（远期，勿提前实施）

> 完整规格见 [34-version-roadmap-0x.md §6](34-version-roadmap-0x.md#6-05-public-beta--pypi050-public-beta)。**当前仍聚焦 0.1→0.2**；0.5 在 0.4 验收通过后再启动。

### 7.1 入口条件

- [ ] 0.4 全部验收通过（SQLite recovery、scheduler、approval 稳定）
- [ ] Mini / 0.2 / 0.3 测试基线不退化
- [ ] 维护者本人已连续多日使用 0.4 每日链

### 7.2 PyPI 与安装

- [ ] `pip install loop-pilot` 可用（PyPI `0.5.0b1`）
- [ ] `loop-pilot init demo` 生成 `loop-pilot-demo/`
- [ ] 5–10 分钟 quick start 文档与验收命令对齐

### 7.3 CI / Release

- [ ] `ci.yml` + `release.yml`（build、twine check、PyPI Trusted Publisher、GitHub Release）
- [ ] 包内容审计：无 outputs/memory/.env

### 7.4 文档与示例

- [ ] 开源 README（EN + `docs/zh/`）
- [ ] `docs/getting-started.md`、`concepts.md`、`configuration.md`、`safety.md`、`adapters.md`、`loops/*.md`
- [ ] `examples/`：intern_demo、paper_demo、daily_news_demo、full_demo
- [ ] CONTRIBUTING、SECURITY、CODE_OF_CONDUCT、LICENSE、CHANGELOG

### 7.5 0.5 验收命令（目标）

```bash
pip install loop-pilot
loop-pilot init demo
cd loop-pilot-demo && loop-pilot doctor && loop-pilot run all --fixture-set mini --dry-run
git clone ... && pip install -e ".[dev]" && pytest -q
python -m build && twine check dist/*
```

### 7.6 明确不做

商业化、云服务、多用户、Web UI、插件市场、企业权限、自动 PR/deploy。

## 10. 0.6–0.9 远期预览（勿提前实施）

> 完整规格见 [34-version-roadmap-0x.md](34-version-roadmap-0x.md) §7–§10。**0.9 决策日志**见 [logs/2026-06-20-0.9-release-candidate-spec.md](logs/2026-06-20-0.9-release-candidate-spec.md)。

| 版本 | 名称 | 一句话 |
|------|------|--------|
| 0.6 | plugin-ecosystem | 本地插件、自定义 Loop/Skill/Connector |
| 0.7 | evaluation-benchmark | benchmark、模型对比、Eval report |
| 0.8 | team-cloud-preview | 项目工作区、角色权限、Dashboard preview |
| 0.9 | release-candidate | API/配置/DB 冻结、安全审计、7 天长跑、文档定稿 |
| 1.0 | stable | 0.9 RC 通过后的正式 semver 稳定承诺 |

**0.9 入口条件**：0.8 验收通过；到 0.8 ≈95%+，到 0.9 还差 **15–25% 稳定化工程**（非新功能）。

---

## 11. 不要做的事（跨阶段）

| 动作 | 原因 |
|------|------|
| 现在实现 0.3 Real Adapter | 0.1/0.2 未稳 |
| 把 0.3 称为 "V1" | 命名混淆；0.3 是 V1-alpha 前置 |
| 在 Mini 注册 `resume` 等假命令 | 违反 Mini 边界 |
| 默认 `allow_real_adapters: true` | 安全风险 |
| 跳过 PolicyEngine 接真实 CLI | 必须先 ToolBroker + allowlist |
| 现在发布 PyPI / 写 init 命令 | 归属 **0.5**；0.4 未完成前不做 |
| 现在做 0.6–0.9 功能 | 归属对应版本；当前仅文档规划 |
| 在 0.9 前引入破坏性 API 变更 | 推迟至 2.0；0.9 为 freeze 窗口 |
| 覆盖 `CURSOR_MINI_IMPLEMENTATION_PROMPT.md` | 历史提示词保留 |

## 12. 相关文档

- [34-version-roadmap-0x.md](34-version-roadmap-0x.md) — **0.1→1.0 完整路线图**（§6 = 0.5 规格，§10 = **0.9 RC 规格**）
- [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md) — 0.5 规划决策日志
- [logs/2026-06-20-0.9-release-candidate-spec.md](logs/2026-06-20-0.9-release-candidate-spec.md) — **0.9 RC 规划决策日志**
- [32-mini-mvp-acceptance.md](32-mini-mvp-acceptance.md) — 0.1 验收
- [31-v1-v2-v3-implementation-roadmap.md](31-v1-v2-v3-implementation-roadmap.md) — Legacy 任务细节
- [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md) — 0.3 技术规格
- [logs/2026-06-20-version-roadmap-0x.md](logs/2026-06-20-version-roadmap-0x.md) — 本次规划决策日志
