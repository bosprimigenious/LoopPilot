# 14 实现文件与脚本清单

本文回答“真正开始编码时必须写哪些文件、哪些脚本不是必需的”。核心运行能力必须实现为可测试模块，不应堆成几个不可维护的大脚本。

## 1. 必须实现的入口

| 文件 | 必须 | 职责 |
|---|---:|---|
| `src/loop_pilot/cli.py` | 是 | 所有用户命令的唯一入口 |
| `src/loop_pilot/app.py` | 是 | 装配配置、存储、Runtime、Loop 和适配器 |
| `src/loop_pilot/config.py` | 是 | 加载并校验 YAML 配置 |
| `src/loop_pilot/domain/models.py` | 是 | Run、Round、Task、Artifact 等领域对象 |
| `src/loop_pilot/domain/states.py` | 是 | 状态和合法转换 |
| `src/loop_pilot/domain/errors.py` | 是 | 稳定错误分类 |

不得另外维护 `run_daily.py`、`run_intern.py`、`run_paper.py` 三套业务入口；它们会造成配置和流程分叉。统一使用：

```bash
loop-pilot doctor
loop-pilot run daily-news
loop-pilot run intern
loop-pilot run paper
loop-pilot run all
loop-pilot status
loop-pilot inspect <run-id>
```

## 2. Runtime 必须模块

```text
src/loop_pilot/runtime/
├── orchestrator.py       # 驱动一次 Run
├── state_machine.py      # 状态转换
├── budgets.py            # 时间、轮次、调用、费用
├── locks.py              # Loop/工作区锁
└── finalizer.py          # 固化结果、释放资源
```

以上文件为 Mini 必需。V1 再增加 `checkpoints.py`、`recovery.py` 和 `approvals.py`。`orchestrator.py` 不得包含具体代码修改、论文写作或网页抓取逻辑。

## 3. Policy、存储与报告必须模块

```text
src/loop_pilot/policy/
├── engine.py
├── paths.py
├── commands.py
├── diffs.py
└── external_actions.py

src/loop_pilot/storage/
├── base.py
├── json_store.py
├── events.py
└── artifacts.py

src/loop_pilot/reporting/
├── renderer.py
├── evidence_links.py
├── daily_summary.py
└── templates.py
```

上述 storage 文件为 Mini 必需。V1 增加 `sqlite.py` 和 `migrations.py`。Mini 必须配套成功、部分完成、无任务、阻塞、失败和耗尽 Markdown 模板；审批请求模板从 V1 开始。

## 4. InternLoop 必须模块

```text
src/loop_pilot/loops/intern/
├── loop.py               # 阶段编排适配
├── observer.py           # 仓库、昨日任务、CI/测试状态
├── task_selector.py      # 单任务选择
├── planner.py            # 文件范围、动作、验证计划
├── workspace.py          # Git worktree 生命周期
├── worker.py             # 受控修改
├── test_runner.py        # test/lint/type/build
├── diagnoser.py          # 失败分类和根因证据
├── reflector.py          # 下一轮差异化计划
└── evaluator.py          # 汇总验证与 diff review
```

必须实现的 Tool：

- Git status/diff/log/worktree；
- 受控文件读取、搜索和写入；
- 带超时的命令执行；
- 测试结果捕获；
- diff 范围与敏感文件检查。

不是必需：自动 commit、push、PR、部署和多 Agent 并发。

## 5. PaperLoop 必须模块

```text
src/loop_pilot/loops/paper/
├── loop.py
├── state_reader.py
├── task_selector.py
├── gap_diagnoser.py
├── literature_query.py
├── citation_verifier.py
├── revision_planner.py
├── writer.py
├── structure_checker.py
├── claim_evidence_checker.py
├── experiment_checker.py
├── related_work_checker.py
├── consistency_checker.py
├── reviewer_simulator.py
├── reflector.py
└── evaluator.py
```

必须实现的 Tool：

- Markdown/LaTeX 章节读取和定位；
- BibTeX 读取、去重和 citation key 检查；
- DOI/arXiv 等稳定标识核验；
- claim 与实验表/图/来源映射；
- 数字和术语一致性检查；
- 论文工作副本与修订 diff。

不是必需：自动跑昂贵实验、自动投稿、自动生成不存在的 BibTeX、把 Reviewer verdict 当硬分数。

## 6. DailyNewsLoop 必须模块

```text
src/loop_pilot/loops/daily_news/
├── loop.py
├── fetcher.py
├── normalizer.py
├── deduplicator.py
├── date_verifier.py
├── source_verifier.py
├── ranker.py
├── router.py
└── snapshot_store.py
```

必须实现的 Connector：

- GitHub repository/release/issue/security 读取；
- 至少一个论文元数据源和一个 DOI 元数据源；
- RSS/Atom 通用读取；
- 官方公告页面读取；
- HTML fallback 及结构失效检测。

必须实现：增量游标、内容哈希、规范 URL、跨来源去重、GitHub Star 快照、条目上限、低置信度隔离。

不是必需：全网社交媒体抓取、情绪分析、自动交易判断和无限来源扩展。

## 7. Agent 与 Skill 必须文件

```text
agents/<agent-name>/
├── prompt.md
├── contract.yaml
└── examples/

skills/<skill-name>/
├── SKILL.md
├── schemas/
└── templates/
```

Mini 阶段可将 Prompt 和契约放在包内；V1 前必须拆出可测试契约。每个 Agent 必须有至少一个成功、一个拒绝和一个证据不足示例。

## 8. 必须的运维脚本

核心业务通过 CLI 运行；以下脚本只承担安装、维护和测试：

| 脚本 | 必须阶段 | 职责 |
|---|---|---|
| `scripts/bootstrap_local.py` | Mini | 创建本地目录和示例配置，不覆盖已有文件 |
| `scripts/install_scheduler.py` | V1 | 安装/打印 OS 调度配置，支持 dry-run |
| `scripts/run_regression.py` | V1 | 运行固定三 Loop 回归场景 |
| `scripts/backup_state.py` | V1 | 备份 SQLite、配置和未关闭检查点 |
| `scripts/migrate_state.py` | V1 | 显式执行并记录状态 Schema migration |
| `scripts/seed_demo_data.py` | Mini | 创建测试仓库、论文和新闻夹具，只用于测试 |

这些脚本必须幂等、支持 `--dry-run`（适用时）、失败返回非零退出码，并输出 Markdown 或明确日志。

## 9. 可选脚本

- `scripts/export_reports.py`：批量导出报告。
- `scripts/benchmark_models.py`：离线比较模型，不进入每日链。
- `scripts/cleanup_cache.py`：预览和清理可再生缓存。
- `scripts/rebuild_github_snapshots.py`：仅在快照修复时使用。
- `scripts/import_bibliography.py`：批量导入已有文献库。

可选脚本不能成为核心 Loop 成功所需的隐藏依赖。

## 10. 配置与模板必须文件

```text
config/
├── loop-pilot.yaml
├── intern.yaml
├── paper.yaml
├── daily_news.yaml
├── policies.yaml
├── sources.yaml
└── models.yaml

templates/
├── intern/
├── paper/
├── daily_news/
├── approvals/
└── daily_summary/
```

每份配置必须有 Schema、示例、默认值说明和错误测试。密钥只写环境变量名称，不写值。

## 11. 测试文件必须结构

```text
tests/
├── unit/
├── integration/
├── scenarios/
│   ├── intern/
│   ├── paper/
│   └── daily_news/
├── fault_injection/
└── fixtures/
```

任何必需模块没有对应测试和错误路径时，不算完成。
