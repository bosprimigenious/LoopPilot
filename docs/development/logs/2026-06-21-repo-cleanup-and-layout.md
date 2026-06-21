# 2026-06-21 仓库清理与目录说明

日期：2026-06-21  
分支：`adapter-mvp-0.3`  
类型：仓库卫生 + 文档（不涉及 Python 源码逻辑）

## 1. 背景

本地开发产生大量未跟踪生成物（`__pycache__`、`.pytest_cache`、`var/artifacts/` run 输出、`*.egg-info`）。`.gitignore` 已覆盖多数模式，但缺少文档化的目录说明，且 `var/` 占位未纳入版本控制。

## 2. 已清理的本地垃圾

以下均为**生成物**，已从工作区删除（不影响源码与 `var/` 内用户 run 数据）：

| 类型 | 数量 / 说明 |
|------|-------------|
| `__pycache__/` | 15 个目录（`src/loop_pilot/` 及 `tests/` 下） |
| `.pytest_cache/` | 根目录 1 个 |
| `.ruff_cache/` | 根目录 1 个 |
| `src/loop_pilot.egg-info/` | pip editable 安装产物 1 个 |

**未删除：** `var/` 下约 9000+ 文件（本地 run 状态与 artifacts）。这些应被 git 忽略，保留供本地调试。

## 3. `.gitignore` 变更

- 将 `/var/` 改为 `/var/*` + `!/var/.gitkeep`，以便跟踪占位文件而忽略运行时内容。
- 其余 Python / pytest / secret 规则已存在，未重复添加。

## 4. 新增 / 修改文档

| 文件 | 动作 |
|------|------|
| `var/.gitkeep` | 新建 — 说明 var 由 bootstrap 创建 |
| `docs/README.md` | 新建 — 文档根索引 |
| `docs/zh/06-仓库目录说明.md` | 新建 — 中文目录说明 |
| `docs/zh/README.md` | 更新 — 链接到 06 |
| 本日志 | 新建 |

## 5. 目录重构建议

### 已实施（低风险）

- 文档化顶层布局（`06-仓库目录说明.md`）
- `docs/README.md` 统一入口
- `var/.gitkeep` + gitignore 微调

### 刻意未实施（高风险 / 需单独评审）

- 移动 `src/loop_pilot/` 包结构
- 重命名 `docs/development/00–39` 编号文件
- 调整 `config/*.yaml` 或 Python import
- 删除或合并 `ideas.md`、`DELIVERY.md`、development spec

## 6. 验收

清理后 `git status` 不应出现 `__pycache__`、`.pytest_cache`、`var/artifacts` 等待跟踪项（在 `.gitignore` 生效前提下）。

## 7. 相关

- [docs/zh/06-仓库目录说明.md](../../zh/06-仓库目录说明.md)
- [docs/zh/05-文档体系说明.md](../../zh/05-文档体系说明.md)
