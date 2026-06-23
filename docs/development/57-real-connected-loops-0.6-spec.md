# 0.6 Real Connected Loops Spec

## 版本定位

`0.6` 不等于全自动无人值守。

`0.6 = Real Connected Loops, but Controlled`

三个 Loop 都要真正接外部世界，但仍然遵守：

- 默认 `dry-run`；
- 只在新分支修改；
- 不直接修改 `main`；
- 不自动 merge；
- 不自动 approve；
- 所有外部动作必须有 `RunRecord`、artifact、trace、tool results、report。

## 0.5 与 0.6 边界

### 0.5：真实运行地基

0.5 不做真实自动开发/论文修改/联网新闻成稿，而是把真实运行的控制底座接牢：

- personal SQLite profile；
- runtime path 隔离；
- GitHub token / connector 配置；
- secrets 不落盘；
- run / artifact / report 标准化；
- recovery / resume 语义清楚；
- branch policy；
- PR policy；
- source verification contract；
- daily schedule 仍 fail-closed。

### 0.6：真实外部世界 Loop

0.6 才做：

- Real InternLoop；
- Real PaperLoop；
- Real DailyNewsLoop。

但 0.6 仍然是 controlled，不是 autonomous。

## 共用控制层

三个 Loop 必须共用同一套安全与审计控制层：

```text
Connector
  ↓
Policy Gate
  ↓
RunRecord
  ↓
Branch / Artifact / Evidence
  ↓
Human Review
  ↓
PR / Report
```

领域逻辑可以不同，但外部动作必须一致：

- 读外部系统：connector；
- 写本地/远端：tool broker；
- 开分支/发 PR：branch policy + PR policy；
- 决策：policy gate；
- 证据：artifact manifest；
- 用户批准：human review。

## 0.6.0 Real InternLoop

### 目标

InternLoop 能读取指定 GitHub 仓库、PR、issue、CI、review comment 和新代码更新，在新分支上修复问题并发 draft PR。

### 输入

- GitHub repo；
- base branch；
- issue / PR / CI failure / review thread；
- 用户明确任务；
- 可选本地工作区；
- 测试命令配置。

### 必须能力

- 连接用户 GitHub 账号；
- 读取指定 repo；
- 读取 PR / issue / CI failure / review comment；
- 拉取最新 base branch；
- 创建新分支；
- 修改代码；
- 跑测试；
- 记录报错、调试信息、尝试路径；
- 生成 `development-report.md`；
- commit；
- push branch；
- open draft PR。

### 强约束

```text
Never modify main directly.
Never push to main.
Never merge PR.
Every code change must happen on a new branch.
Every run must produce report + trace + tool-results.
```

### PR body 必须包含

- 问题；
- 修改；
- 测试；
- 风险；
- 未解决点；
- artifact 链接。

### 终态

```text
SUCCEEDED:
  draft PR opened, tests passed, report written.

PARTIAL:
  branch exists, some fix attempted, tests still failing or incomplete.

BLOCKED:
  auth missing, branch policy denied, CI unavailable, test environment unavailable, unclear user intent.
```

## 0.6.1 Real PaperLoop

### 目标

PaperLoop 能根据用户现有观点、论文草稿、claim list、实验计划和服务器/数据目录的新结果，更新论文并发 draft PR。

### 输入

- paper repo；
- LaTeX / Markdown / Overleaf mirror；
- claim list；
- experiment plan；
- server data manifest；
- figure/table generation scripts；
- bibliography。

### 必须能力

- 连接 paper repo；
- 拉取最新论文代码 / LaTeX / Markdown；
- 读取观点文件、claim list、实验计划；
- 读取服务器或数据目录的新数据；
- 对照论文 claim；
- 判断：
  - 哪个 claim 被支持；
  - 哪个 claim 需要降级；
  - 哪个实验缺失；
  - 哪个图表需要更新；
- 修改论文草稿；
- 更新表格/图表引用；
- 写 `paper-development-report.md`；
- 新建分支；
- commit；
- push；
- open draft PR。

### 强约束

```text
Never fabricate citation.
Never invent result.
New data must be linked to source path / checksum / timestamp.
Every claim change must cite evidence.
Every paper edit must be in branch + PR.
```

### Evidence gate

每个 claim 变化必须记录：

```text
claim_id
old_text
new_text
evidence_path
evidence_checksum
data_timestamp
support_level: supports | weakens | unresolved
```

## 0.6.2 Real DailyNewsLoop

### 目标

DailyNewsLoop 不再只跑 fixture，而是真实联网读取 GitHub、论文、政治财经新闻，聚簇、核验、过滤噪音和假信息，然后生成日报和候选任务。

### 必须能力

- `GitHubLiveConnector`；
- arXiv / paper metadata connector；
- RSS / official source connector；
- finance / politics source whitelist；
- source tier；
- event clustering；
- cross-source verification；
- `unresolved-signals.md`；
- `daily-news-report.md`；
- `candidate-actions.json`；
- 显式 import 到 Inbox。

### 强约束

```text
C-tier source cannot enter final report alone.
Single-source political/finance news goes to unresolved.
GitHub trending cannot claim star delta without previous snapshot.
No automatic Intern/Paper task creation without human import/approval.
```

### 聚簇层

DailyNews 必须加 cluster layer。详见 [56-dailynews-clustering-layer-plan.md](56-dailynews-clustering-layer-plan.md)。

## 版本拆分建议

```text
0.5.0  Personal runtime substrate
       SQLite profile, path isolation, reports, branch policy, GitHub auth config

0.5.1  GitHub connector foundation
       read repo/PR/CI/issues, no code writing yet

0.5.2  Paper/data connector foundation
       read paper repo, server data manifest, no paper writing yet

0.5.3  News connector foundation
       live GitHub/arXiv/RSS source replay, unresolved-signals

0.6.0  Real InternLoop
       branch -> patch -> tests -> PR -> report

0.6.1  Real PaperLoop
       data -> claim check -> paper branch -> PR -> report

0.6.2  Real DailyNewsLoop
       live source -> verification -> report -> candidate import

0.7.0  Morning OS
       scheduled 30-min runs, still no auto-merge / no auto-approve
```

## 0.6 不得声明 READY 的条件

任一条件不满足时，0.6 必须显示 `NOT READY`：

- 不能证明 main 不会被直接修改；
- 不能证明 push target 不是 protected branch；
- 不能证明 secrets 不落盘；
- 不能生成完整 report；
- 不能回放 tool-results；
- 不能解释失败路径；
- 不能区分事实、推断和未核验信号；
- 不能产生 draft PR 或明确 blocked reason。

