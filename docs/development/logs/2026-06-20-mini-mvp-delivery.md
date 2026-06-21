# 2026-06-20 Mini-MVP（0.1）交付报告

日期：2026-06-21（验收复跑）  
分支：`feat/mini-mvp-0.1`  
里程碑：`0.1.0-mini` / Mini-MVP Phase A

## 1. 八项任务完成情况

| # | 任务 | 状态 | 证据 |
|---|------|------|------|
| 1 | PaperLoop SOURCE_REQUIRED → `partial` | 通过 | `unsupported_claim` → `partial`；报告含 Source Required |
| 2 | DailyNews 候选路由 | 通过 | `intern-candidates.md`、`paper-candidates.md`、`candidate-actions.json` |
| 3 | `runtime.allow_real_adapters` 默认 false | 通过 | `config/loop-pilot.yaml`；`test_allow_real_adapters.py` |
| 4 | pyproject extras 清理 | 通过 | 移除 `all = ["loop-pilot[dev]"]` 自引用 |
| 5 | GitHub Actions CI | 通过 | `.github/workflows/ci.yml` |
| 6 | 异常 traceback Artifact | 通过 | `error-traceback.txt` + trace 错误事件；`test_error_artifacts.py` |
| 7 | README Mini-MVP 状态 | 通过 | 验收命令块、0.x 路线图、边界说明 |
| 8 | 全量验证 | 通过 | 见 §3 |

## 2. 主要修改文件

### 运行时与 Loop

- `src/loop_pilot/loops/paper/loop.py` — SOURCE_REQUIRED 语义、outcome 解析
- `src/loop_pilot/loops/daily_news/loop.py` — 双通道候选、JSON 路由表
- `src/loop_pilot/loops/intern/loop.py` — factory 路由、worktree 辅助
- `src/loop_pilot/runtime/orchestrator.py` — 失败 artifact、run_all 隔离
- `src/loop_pilot/cli.py` — Mini 命令面；V1 命令需 `state_backend=sqlite`
- `src/loop_pilot/models/router.py` — `model_roles` + `allow_real_adapters` 守卫
- `src/loop_pilot/adapters/{registry,factory,mock_adapter}.py` — Mock 默认、真实 Adapter 门控

### 0.4 预备模块（未纳入 Mini 验收）

- `src/loop_pilot/storage/sqlite.py`、`migrations.py`
- `src/loop_pilot/runtime/{recovery,checkpoints,approvals}.py`
- `src/loop_pilot/adapters/{api_model,coding_cli,base}.py`
- `scripts/{migrate_state,backup_state,install_scheduler,run_regression}.py`

### 配置、CI、模板

- `config/loop-pilot.yaml`、`config/models.yaml`
- `.github/workflows/ci.yml`
- `templates/daily_news/daily-news-report.md`
- `pyproject.toml`

### 测试（新增/扩展）

- `tests/unit/test_allow_real_adapters.py`
- `tests/unit/test_error_artifacts.py`
- `tests/scenarios/daily_news/test_github_star_snapshots.py`
- `tests/scenarios/paper/test_unsupported_claim.py`
- `tests/integration/test_v1_{cli,recovery}.py`（SQLite 场景，默认 JSON 不影响 Mini）

## 3. 验证结果（2026-06-21 复跑）

```text
ruff check .                    →  All checks passed
pytest -q                       →  93 passed in ~35s
loop-pilot doctor               →  Doctor: OK
run intern ... --dry-run        →  succeeded
run paper ... --dry-run         →  partial (Claim requires additional source)
run daily-news ... --dry-run    →  succeeded (Processed 4 items from day2)
run all --fixture-set mini      →  daily_news/intern succeeded, paper partial
loop-pilot status               →  列出最近 TERMINATED run
```

## 4. Mini 边界说明

- 默认 `state_backend: json` — 无 SQLite 恢复链
- 默认 `allow_real_adapters: false` — 仅 MockAdapter
- V1 CLI（`resume`/`approve`/…）在代码中存在，但 **JSON 配置下调用即失败**；Mini 验收不依赖这些命令
- 不接真实 Cursor CLI / API / 在线爬虫

## 5. 结论

**Mini-MVP Phase A 验收通过。** 可打 tag `0.1.0-mini` 并进入 0.2 Practical MVP 规划。

## 6. 相关文档

- [32-mini-mvp-acceptance.md](../32-mini-mvp-acceptance.md)
- [33-next-steps-0.2.md](../33-next-steps-0.2.md)
- [DELIVERY.md](../../../DELIVERY.md)
