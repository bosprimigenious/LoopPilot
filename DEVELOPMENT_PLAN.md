# LoopPilot 开发计划

LoopPilot 的详细开发计划已拆分为多个 Markdown 分册。

## 从哪里开始

| 目的 | 入口 |
|------|------|
| **日常理解（中文）** | [docs/zh/README.md](docs/zh/README.md) |
| **英文接口规格** | [docs/en-core.md](docs/en-core.md) |
| **完整开发索引** | [docs/development/README.md](docs/development/README.md) |
| **文档三层说明** | [docs/zh/05-文档体系说明.md](docs/zh/05-文档体系说明.md) |
| **中英文文档管理（权威）** | [docs/zh/10-中英文文档管理.md](docs/zh/10-中英文文档管理.md) |

## 系统构成

- `InternLoop`：每天约 30 分钟处理一个真实开发问题。
- `PaperLoop`：每天约 30 分钟推进一个关键论文缺口。
- `DailyNewsLoop`：每天约 30 分钟筛选少量高价值 GitHub、研究、政治和财经信息。

## 当前版本焦点

- **0.1** Mini-MVP 已完成
- **0.2** Practical MVP 已验收（`v0.2.0a1`）
- **0.3** Adapter MVP — safety alpha `v0.3.0a1`；中文验收说明 [docs/zh/07-0.3-Adapter验收说明.md](docs/zh/07-0.3-Adapter验收说明.md)；英文 [36-adapter-mvp-0.3-acceptance.md](docs/development/36-adapter-mvp-0.3-acceptance.md)
- **0.4.0b1** 稳定化进行中：0.4-d summary/schedule 实现存在，但 Full 0.4 因全量回归失败、0.4-c 未完成、migration v3 冲突和失败审计缺口而 **NOT READY**。
- 当前修复规格：[0.4 Stabilization and Truthful Acceptance](docs/development/50-0.4-stabilization-and-truthful-acceptance.md)
- Cursor 执行提示词：[CURSOR_0.4_STABILIZATION_PROMPT.md](prompts/CURSOR_0.4_STABILIZATION_PROMPT.md)

## 关键文档（英文规格）

- [总体架构](docs/development/01-architecture.md)
- [统一运行机制](docs/development/02-runtime-mechanism.md)
- [InternLoop](docs/development/03-intern-loop.md)
- [PaperLoop](docs/development/04-paper-loop.md)
- [DailyNewsLoop](docs/development/05-daily-news-loop.md)
- [Adapter 规范](docs/development/19-adapter-specifications.md)
- [0.3 验收](docs/development/36-adapter-mvp-0.3-acceptance.md)
- [测试与验收](docs/development/10-testing-and-acceptance.md)

原始探索内容保留在 [ideas.md](ideas.md)，不作为最终架构依据。
