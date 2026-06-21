# 2026-06-21 文档体系三层升级

日期：2026-06-21  
分支：`adapter-mvp-0.3`  
类型：文档架构决策（不涉及源码变更）

## 1. 背景

LoopPilot 在 0.3 阶段文档数量增长（00–39 编号规格 + 验收清单 + 日志）。原有 README 以英文为主、development 索引信息密度高，**新读者难以在 30 秒内理解系统**；同时 AI 实施需要稳定的英文接口规格。

## 2. 决策

采用 **三层文档架构**，不整篇双语同步：

| 层 | 语言 | 位置 | 职责 |
|----|------|------|------|
| Layer 1 认知层 | 中文 | `README.md`、`docs/zh/` | 人读：理解、跑命令、看进度 |
| Layer 2 执行层 | 英文 | `docs/en-core.md`、`docs/development/*`、`src/` | AI/CI：契约、验收 |
| Layer 3 提示词层 | 中+英 | `prompts/` | 中文目标 + English constraints |

**核心原则：** 中文 = 认知层；英文 = 接口层。Think in Chinese, interfaces in English.

## 3. 交付物

### 新建

- `docs/en-core.md` — 英文最小规格（overview / adapter / loop / state machine / safety）
- `docs/zh/README.md` 及 `00`–`05` 共 6 篇中文认知文档
- `prompts/CURSOR_0.3_ADAPTER_MVP_PROMPT.md` — 0.3 双语实施提示词
- 本日志

### 修改

- `README.md` — 中文主入口 + `English spec: see docs/en-core.md`
- `docs/development/README.md` — 三层说明 + 更新 0.2/0.3 状态
- `DEVELOPMENT_PLAN.md` — 指向 zh 索引
- `prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md` — 增加双语头部说明
- 遗留 V1/V2/V3 prompts — 增加 `_legacy` 说明与文档体系指向

### 明确不做

- 不删除任何 `docs/development/*.md`
- 不全文翻译编号规格
- 不改 CLI、config schema、源码

## 4. 推荐阅读路径

```text
README.md（30 秒）
    → docs/zh/00-快速开始.md（跑通）
    → docs/zh/01-系统是什么.md（理解）
    → docs/en-core.md 或 docs/development/（实施/深入）
```

## 5. 后续（Phase 2+，非本次）

- `docs/getting-started/` 完整入门树
- 按需增补 `docs/zh/` 专题（如 DailyNews 运维）
- 验收 doc 摘要中文版（仍链回英文 checklist）

## 6. 相关链接

- [docs/zh/05-文档体系说明.md](../zh/05-文档体系说明.md)
- [docs/en-core.md](../en-core.md)
