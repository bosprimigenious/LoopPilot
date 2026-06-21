# 2026-06-21 中英文文档管理策略

日期：2026-06-21  
分支：`adapter-mvp-0.3`  
类型：文档架构决策（不涉及源码变更）

## 1. 背景

0.3 收尾与 0.4–1.x 个人优先路线图已定稿（[34-version-roadmap-0x.md](../34-version-roadmap-0x.md)、[42-1x-roadmap-personal-to-collaboration.md](../42-1x-roadmap-personal-to-collaboration.md)）。既有三层文档体系（[2026-06-21-doc-system-bilingual-upgrade.md](2026-06-21-doc-system-bilingual-upgrade.md)）解决了「入口分散」，但缺少：

- 0.3 / 0.4 / 1.x 的**中文认知页**与英文 spec 的一一对应
- **验收文档**写中文摘要还是英文清单的明确分工
- **维护者**何时更新 zh、何时更新 development 的操作规则

## 2. 决策

### 2.1 语言分工（不变）

- **中文** = 理解、规划、日常跑命令（`docs/zh/`、`README.md`、logs 决策）
- **英文** = AI/CI 接口契约、编号 spec、验收文件名（`docs/en-core.md`、`docs/development/`）
- **不整篇双语同步**

### 2.2 新增中文认知页（07–10）

| 文件 | 对应英文 |
|------|----------|
| `docs/zh/07-0.3-Adapter验收说明.md` | `36-adapter-mvp-0.3-acceptance.md` + 验收跑 log |
| `docs/zh/08-0.4-个人日用闭环.md` | `40-personal-daily-loop-0.4-spec.md` |
| `docs/zh/09-1.x-个人到协作.md` | `42-1x-roadmap-personal-to-collaboration.md` |
| `docs/zh/10-中英文文档管理.md` | 本文 + `development/README.md` 映射表 |

`docs/zh/03-版本路线图.md` 同步 0.3 tag、0.4 焦点、1.1–1.3 结构；**移除 emoji 状态标记**，改用文字。

### 2.3 验收双语策略

- **勾选与证据**以英文 `36`（及后续 `40` 验收段）为准
- 中文 `07` 负责：L1/L2/L3 分层、当前结论一句话、MANUAL 项、常用命令、下一步
- 验收跑记录仍在 `development/logs/`（可中文叙述 + 英文命令输出）

### 2.4 索引更新

- `docs/zh/README.md` — 07–10 链接
- `docs/README.md` — 双语高层索引
- `docs/development/README.md` — **中文认知层对应关系**表
- `DEVELOPMENT_PLAN.md` — 指向 `10-中英文文档管理.md`
- `docs/en-core.md` — 最小补充 0.4 / 42 指针（不扩写）

### 2.5 明确不做

- 不移动/重命名 `docs/development/` 编号文件
- 不将 `36`/`40`/`42` 全文翻译为中文
- 不在文档中使用 emoji
- 不改代码、CLI、config

## 3. 维护流程（今后）

1. **阶段边界变更** → 先 `development/34` 或 `42` + logs → 再 `docs/zh/03` 或 07–09
2. **验收状态变更** → 勾选 `36`（英文）→ 更新 `zh/07` 结论段 + 可选 logs
3. **新能力规格** → 英文编号 doc → 若影响日常理解，补 zh 摘要页或扩写 03/08
4. PR 合并前检查：`development/README.md` 映射表是否需要新行

## 4. 推荐阅读路径（本次交付后）

```text
理解 0.3 状态:
  docs/zh/07 → development/36 → logs/2026-06-21-0.3-acceptance-run

规划 0.4:
  docs/zh/08 → development/40 → development/41

理解 1.x:
  docs/zh/09 → development/42 → logs/2026-06-21-1x-roadmap-personal-stable

文档怎么写:
  docs/zh/10 → development/README.md（映射表）
```

## 5. 相关文档

- [docs/zh/10-中英文文档管理.md](../../zh/10-中英文文档管理.md) — 权威维护说明
- [2026-06-21-doc-system-bilingual-upgrade.md](2026-06-21-doc-system-bilingual-upgrade.md) — 三层体系初版
- [2026-06-21-personal-first-roadmap-pivot.md](2026-06-21-personal-first-roadmap-pivot.md) — 0.x pivot
- [2026-06-21-1x-roadmap-personal-stable.md](2026-06-21-1x-roadmap-personal-stable.md) — 1.x 四段式
