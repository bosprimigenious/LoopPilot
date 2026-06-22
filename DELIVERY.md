# Mini-MVP 实施与验证日志

> **历史交付记录，不代表当前分支通过回归。** 截至 2026-06-21，0.4.0b1 正在稳定化，Full 0.4 为 **NOT READY**；当前状态与补救门禁见 [docs/development/50-0.4-stabilization-and-truthful-acceptance.md](docs/development/50-0.4-stabilization-and-truthful-acceptance.md)。

日期：2026-06-21

## 实施摘要

按 8 项任务完成 Mini-MVP 可验收改造：Paper SOURCE_REQUIRED outcome、DailyNews 候选路由、Adapter 安全开关、pyproject extras、CI workflow、失败 traceback artifact、README 与验收文档。

## 修改文件清单

### 核心代码

| 文件 | 变更 |
|---|---|
| `src/loop_pilot/loops/paper/loop.py` | `_run_checks` / `_resolve_outcome`，SOURCE_REQUIRED → PARTIAL |
| `src/loop_pilot/loops/daily_news/loop.py` | intern/paper 候选、`candidate-actions.json` |
| `src/loop_pilot/adapters/registry.py` | **新增** 真实 Adapter 守卫 |
| `src/loop_pilot/adapters/factory.py` | `allow_real_adapters=false` 时强制 MockAdapter |
| `src/loop_pilot/models/router.py` | 集成 `allow_real_adapters` |
| `src/loop_pilot/runtime/orchestrator.py` | 失败 traceback artifact、trace 错误事件 |
| `src/loop_pilot/config.py` | 默认 json backend、`allow_real_adapters: false` |
| `src/loop_pilot/cli.py` | Mini CLI 面（无 resume/approve/reject/cancel/report） |
| `src/loop_pilot/app.py` | ModelRouter 注入 Orchestrator |

### 配置与构建

- `config/loop-pilot.yaml`
- `pyproject.toml`
- `.github/workflows/ci.yml`

### 模板与 fixture

- `templates/daily_news/daily-news-report.md`
- `tests/fixtures/daily_news/github_star_snapshots/input/paper_signal.json`

### 测试

- `tests/scenarios/paper/test_unsupported_claim.py`
- `tests/scenarios/daily_news/test_github_star_snapshots.py`
- `tests/unit/test_allow_real_adapters.py`
- `tests/unit/test_error_artifacts.py`
- `tests/integration/test_deferred_cli.py`
- `tests/integration/test_run_all.py`

### 文档

- `README.md`
- `docs/development/32-mini-mvp-acceptance.md`
- `docs/development/logs/2026-06-20-mini-mvp-delivery.md`

## 验证记录

| 命令 | 结果 |
|---|---|
| `python -m pip install -e ".[dev]"` | 成功 |
| `ruff check .` | All checks passed |
| `pytest -q` | **93 passed** |
| `loop-pilot doctor` | Doctor: OK |
| `run intern --dry-run` | succeeded |
| `run paper --dry-run` | **partial**（SOURCE REQUIRED） |
| `run daily-news --dry-run` | succeeded（4 items，含 paper 候选） |
| `run all --dry-run` | daily_news/intern succeeded，paper partial |
| `status` | 正常列出最近 run |

## 结论

**Mini-MVP 已达到验收标准。**
