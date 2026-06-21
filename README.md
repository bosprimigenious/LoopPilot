# LoopPilot

> Loop Engineering 生态的运行时层 — 受控 AI 工作闭环，可审计产物，默认安全。

**30 秒理解：** 每天三条约 30 分钟的 Loop（开发 / 论文 / 高价值资讯），由统一 Runtime 编排；默认 MockAdapter + dry-run，真实模型需显式开启。

English spec: see [docs/en-core.md](docs/en-core.md)

## 三条循环

| Loop | 做什么 |
|------|--------|
| **InternLoop** | 解决一个真实开发问题，测试验证后出报告 |
| **PaperLoop** | 推进一个论文缺口，证据可查后出报告 |
| **DailyNewsLoop** | 从离线快照筛少量高价值信号，写入 Inbox |

## 当前版本（0.x · 个人优先）

> LoopPilot = **个人开发助手 + 论文推进器 + 信息筛选器 + 每日任务 OS** — 0.x 让**一个人每天真的能用**；1.x：**1.0 稳定 → 1.1 智能 → 1.2 协作 → 1.3 团队 preview**。

| 版本 | 状态 |
|------|------|
| **0.1** Mini-MVP | ✅ 已完成 — fixture dry-run |
| **0.2** Practical MVP | ✅ 已验收 `v0.2.0a1` — demo workspace |
| **0.3** Adapter MVP | 🔄 进行中 `v0.3.0a1` — Mock→Real Adapter |
| **0.4** Personal Daily Loop | 📋 下一 — inbox/queue/today、review、summary |
| 0.5–0.9 | 个人 Beta → RC |
| **1.x** | 1.0 个人稳定 → 1.1 智能 → 1.2 受控协作 → 1.3 团队 preview |

详情：[docs/zh/03-版本路线图.md](docs/zh/03-版本路线图.md) · [docs/development/34-version-roadmap-0x.md](docs/development/34-version-roadmap-0x.md)

## 快速开始

```bash
pip install -e ".[dev]"
python scripts/bootstrap_local.py   # 可选，首次
loop-pilot doctor
pytest -q
```

跑 demo workspace（0.2）：

```bash
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
```

跑 fixture 回归（0.1）：

```bash
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
```

0.3 Adapter 探测（默认被拦截）：

```bash
loop-pilot adapters list
loop-pilot adapters doctor
loop-pilot run intern --workspace examples/intern_demo --adapter cursor_cli --dry-run
# expect: blocked（allow_real_adapters=false）
```

## 命名规范

| 用途 | 名称 |
|------|------|
| 产品 / 项目 | `LoopPilot` |
| CLI / PyPI | `loop-pilot` |
| Python 包 | `loop_pilot` |

不使用未分隔的小写 `looppilot`。

## 文档入口

| 读什么 | 去哪 |
|--------|------|
| 日常中文理解 | [docs/zh/README.md](docs/zh/README.md) |
| 英文接口规格（AI/CI） | [docs/en-core.md](docs/en-core.md) |
| 开发文档索引 | [docs/development/README.md](docs/development/README.md) |
| 0.x 版本路线图 | [docs/development/34-version-roadmap-0x.md](docs/development/34-version-roadmap-0x.md) |
| 0.2 验收 | [docs/development/35-practical-mvp-0.2-acceptance.md](docs/development/35-practical-mvp-0.2-acceptance.md) |
| 0.3 验收清单 | [docs/development/36-adapter-mvp-0.3-acceptance.md](docs/development/36-adapter-mvp-0.3-acceptance.md) |
| 0.3 安全 / ToolBroker | [37-adapter-safety-policy.md](docs/development/37-adapter-safety-policy.md) · [38-toolbroker-design.md](docs/development/38-toolbroker-design.md) |
| 开发计划 | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) |

## 安全

接入 Adapter、Tool 或凭据前，请阅读 [SECURITY.md](SECURITY.md) 与 [docs/development/37-adapter-safety-policy.md](docs/development/37-adapter-safety-policy.md)。

评估 LoopPilot 输出质量可使用外部工具 [agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner)。
