# 规划日志：1.x 路线图（Personal Stable → Controlled Collaboration）

**日期**：2026-06-21  
**决策类型**：1.x 阶段边界 — 个人稳定优先，团队/云后置至 1.3 preview  
**状态**：已采纳（文档 only）

---

## 背景

2026-06-21 个人优先 pivot 已将 Team/Cloud **移出 0.x**，但 34 文档仍使用笼统的 **「1.1+ Team / Cloud Preview」**，未区分：

- 个人智能增强（记忆、规划、优先级）
- 受控协作（文件包、handoff，无云端账号）
- 团队/云 preview（RBAC、sync、Dashboard）

用户明确：**1.0 后不要立刻做大团队版**；应先 30 天个人稳定，再逐步走向多人协作。

## 决策

### 1. 1.x 四段式（取代「1.1+」笼统表述）

| 版本 | 名称 | 要点 |
|------|------|------|
| **1.0** | Personal Stable | 接口冻结；30 天日用；个人 semver 承诺 |
| **1.1** | Personal Intelligence | 记忆、规划、优先级；**非团队** |
| **1.2** | Controlled Collaboration | 文件包协作、handoff；**非云端账号** |
| **1.3** | Team / Cloud Preview | RBAC、sync、Dashboard；**preview only** |

### 2. 与旧规划映射

| 旧规划 | 新归属 | 说明 |
|--------|--------|------|
| 0.8 team-cloud（[33 §0.8](../33-version-roadmap.md)） | **deprecated @ 0.8** | 拆分：协作 → **1.2**；团队/云 → **1.3** |
| 0.8 Optional Public Beta（34 现行） | **0.8 保留** | 公开文档；与 1.3 无关 |
| 1.1+ Team / Cloud（34 旧 §12） | **supersede** | 细化为 1.1–1.3 |
| 0.6 Personal Memory | **0.6 + 1.1** | 0.6 基础记忆；1.1 智能增强 |

### 3. 核心原则（写入 42）

1. 1.0 之前不承诺稳定接口
2. 1.0 之后 CLI/配置/状态/Artifact additive-only
3. 团队协作不早于个人稳定（不可跳过 1.0/1.1）
4. 云端不早于本地安全模型
5. 自动化可审计、可暂停、可恢复

### 4. Team/Cloud 明确在 1.3

- **不在 0.8**（0.8 = Optional Public Beta，个人叙事）
- **不在 1.0 / 1.1**（个人 only）
- **1.2** 仅文件包协作，无云端账号
- **1.3** 才含 team workspace、cloud sync prototype、Dashboard preview

## 产出文档

| 文件 | 动作 |
|------|------|
| `42-1x-roadmap-personal-to-collaboration.md` | **新建** — 1.0–1.3 完整规格 |
| `34-version-roadmap-0x.md` | 增加 §1.x 总览；更新 §12；diagram 延伸 1.1–1.3 |
| `docs/zh/03-版本路线图.md` | 中文同步 1.x 总览 |
| `docs/development/README.md` | 索引 42 + 决策日志 |
| `README.md` | 路线图表一行 1.x |
| `40-personal-daily-loop-0.4-spec.md` | cross-ref → 1.0 验收 |
| 本文 | 新建 |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 33 旧 §0.8 与 42 冲突 | 33 顶注 + 42 §1.2 映射表；0.8 team 标 deprecated |
| 1.0 与 0.9/33 §1.0 重复 | 42 为 1.x 权威；34 摘要 + cross-ref |
| 过早做 1.3 团队 | 42 §7 门禁：1.0 需 30 天日用 |

## 下一步

1. 完成 0.3 → 0.4 日用链（1.0 前置）
2. 0.9 RC 冻结后发布 1.0 Personal Stable
3. 维护者 30 天日用日志作为 1.0 发布证据
