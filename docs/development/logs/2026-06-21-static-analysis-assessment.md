# 2026-06-21 静态分析与版本状态评估

日期：2026-06-21  
分支：`main`（静态分析基线）  
包版本：`0.2.0a1`（`pyproject.toml`）

## 1. 评估结论（摘要）

| 版本 | 代号 | 状态 | 说明 |
|------|------|------|------|
| **0.1** | mini | **基本完成** | Phase A 清单已通过；待本地/CI 最终确认后可打 tag `0.1.0-mini` |
| **0.2** | practical-mvp | **0.2.0a1 候选 / 代码就绪，验收待定** | demo workspace CLI 与产物链路已实现；需正式 acceptance run + CI 绿 |
| **0.3** | adapter-mvp | **未开始** | 仅路线图（CursorCLIAdapter、ToolBroker、`adapters list/doctor` 等） |
| **0.4+** | recovery / beta / … | **未开始** | 仅规划；仓库内 SQLite/recovery WIP 归属 0.4，非当前验收范围 |

**当前主线口径**：`main` 位于 **0.2.0a1 / Practical MVP Candidate**，不是 pre-0.1，也不是 0.3。

## 2. 0.1 完成证据

- `pyproject.toml`：`version = "0.2.0a1"`，`loop-pilot` CLI entry point
- `runtime.allow_real_adapters: false` 默认生效（`config/loop-pilot.yaml`）
- workspace allowlist：`workspaces.intern_demo` / `workspaces.paper_demo`
- CI：`.github/workflows/ci.yml` 覆盖 mini + 0.2 demo dry-run
- PaperLoop：`SOURCE_REQUIRED` → `partial` / NEEDS_HUMAN
- DailyNews：`paper-candidates.md`、`candidate-actions.json`
- pyproject extras 已修复（无自引用 `all = ["loop-pilot[dev]"]`）

详见 [32-mini-mvp-acceptance.md](../32-mini-mvp-acceptance.md)、[logs/2026-06-20-mini-mvp-delivery.md](2026-06-20-mini-mvp-delivery.md)。

## 3. 0.2 候选证据

- README 将 **0.2 practical-mvp** 标为当前阶段
- CLI：`--workspace`、`--source-profile`、`--profile demo`
- 验收文档：[35-practical-mvp-0.2-acceptance.md](../35-practical-mvp-0.2-acceptance.md)
- CI 运行 demo workspace dry-run
- PaperLoop 产出 `review-required.md`、`next-actions.md`
- DailyNews 双通道候选（intern + paper）
- 集成测试：`tests/integration/test_practical_mvp.py`

## 4. 0.3+ 未开始（仅文档）

以下能力**不在**当前已验收范围，不得标称为已实现：

- `CursorCLIAdapter` / `CodingCLIAdapter` 每日主链
- `ToolBroker` 生产路径
- `loop-pilot approve` / `reject` CLI（0.4）
- SQLite recovery / `resume` 生产语义（0.4）
- PyPI / `init demo`（0.5）

路线图见 [34-version-roadmap-0x.md](../34-version-roadmap-0x.md) §4–§6、[30-adapter-and-model-router-roadmap.md](../30-adapter-and-model-router-roadmap.md)。

## 5. 本地验收复跑（2026-06-21）

自仓库根目录执行 [35-practical-mvp-0.2-acceptance.md](../35-practical-mvp-0.2-acceptance.md) 命令：

```bash
python -m pip install -e ".[dev]"
pytest -q
loop-pilot doctor
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot run paper --workspace examples/paper_demo --dry-run
loop-pilot run daily-news --source-profile demo --dry-run
loop-pilot run all --profile demo --dry-run
```

### 结果

| 命令 | 结果 | 预期 | 状态 |
|------|------|------|------|
| `pip install -e ".[dev]"` | 成功 | — | 通过 |
| `pytest -q` | **91 passed** in ~25s | 全绿 | 通过 |
| `loop-pilot doctor` | Doctor: OK | OK | 通过 |
| `run intern … intern_demo` | **succeeded** | succeeded | 通过 |
| `run paper … paper_demo` | **partial**（Claim requires additional source） | partial | 通过 |
| `run daily-news … demo` | **succeeded**（Processed 2 items） | succeeded | 通过 |
| `run all --profile demo` | daily_news/intern succeeded, paper partial | 同上 | 通过 |

### 未确认项

- **GitHub CI 绿**：静态分析未能从 GitHub 确认 main 上 CI 最新状态；需维护者查看 Actions 或 push 后复验。
- **正式 0.2 sign-off**：本地复跑通过 ≠ 里程碑验收完成； checklist 仍以「候选 / pending acceptance」口径记录。

## 6. 建议下一步

1. 确认 GitHub Actions `ci.yml` 在 `main` 上为绿。
2. 在 [35-practical-mvp-0.2-acceptance.md](../35-practical-mvp-0.2-acceptance.md) 勾选全部 checklist 后，将 0.2 标为 **accepted**（非 candidate）。
3. 可选：打 tag `0.1.0-mini`（若尚未打）与预发布 tag `0.2.0a1`。
4. **不要**提前启动 0.3 Real Adapter 接入；入口条件为 0.2 正式验收通过。

## 7. 相关文档

- [33-version-roadmap.md](../33-version-roadmap.md) — 权威 semver 边界
- [34-version-roadmap-0x.md](../34-version-roadmap-0x.md) — 0.x 详细规格
- [33-next-steps-0.2.md](../33-next-steps-0.2.md) — 当前行动项
- [35-practical-mvp-0.2-acceptance.md](../35-practical-mvp-0.2-acceptance.md) — 0.2 验收清单
