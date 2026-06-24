# 0.5 / 0.6 / 0.7 版本边界：真实 Agent 何时打通

> **Versioning update:** 后续 0.5 规划采用和 `agentic-rubric-runner`
> 一致的细粒度版本层级：公开发布如 `0.5.2`，内部切片如 `0.5.2.1`，
> 门控迭代如 `0.5.2.1.3`，证据运行如 `0.5.2.1.3.2`。权威编号见
> [61-0.5-version-alignment-with-agent-runner.md](61-0.5-version-alignment-with-agent-runner.md)。

## 核心结论

不要把 0.5 写成“三个真实 Agent 已打通”。

最准确的边界是：

```text
0.5 完成 = 三个真实 agent 可以安全接入
0.6 完成 = 三个真实 agent 真正打通
0.7 完成 = 三个真实 agent 可以进入 Morning OS 调度
```

也就是说：

```text
Current: 0.4.0b1 Truthful Runtime Baseline
Also present: 0.5-prep SafetyGate scaffolding
Next: 0.5 Personal Runtime Substrate
Then: 0.6 Real Connected Loops, but Controlled
Later: 0.7 Morning OS
```

## 为什么 0.5 不能直接等于真实 Agent 打通

0.5 是地基，不是派 Agent 去真实世界干活。

0.5 应该解决：

- personal SQLite profile；
- runtime path 隔离；
- secrets 不落盘；
- GitHub auth 配置方式；
- branch policy；
- PR policy；
- source verification contract；
- report / artifact 标准；
- recovery / resume 语义清楚；
- schedule / unattended 仍 fail-closed；
- `today list/show/done/defer`；
- 更好的 failure report。

这些完成后，LoopPilot 才具备“安全接真实世界”的能力。

但 0.5 本身不应该做：

- 自动读取 GitHub PR 并修复；
- 修改真实 paper repo；
- 读取服务器新数据并改论文；
- 真实联网抓新闻并聚簇核验；
- push 分支；
- open PR。

这些是 0.6。

## 0.4.0b1 当前真实状态

`0.4.0b1` 是 Truthful Runtime Baseline。

已经完成：

- 三个 fixture/demo Loop；
- MockAdapter；
- ToolBroker 基线；
- JSON + SQLite state；
- SQLite migrations 到 v4；
- review layer；
- patch review gate；
- `WAITING_APPROVAL`；
- approve / reject / cancel / defer；
- daily summary；
- schedule preview；
- terminal artifacts；
- failure artifact contract；
- truthful 0.4 aggregate gate。

当前自动化口径：

```text
ruff check .                  PASS
pytest -q                     254 passed
verify_0_4_acceptance.py      11/11 READY
verify_0_5_prep.py            prep PASS / ready NOT READY
```

## 0.4 还不完整的地方

0.4 已经可以称为 truthful runtime baseline，但还不是舒适的个人日用工具。

### 1. 默认配置仍是 JSON

默认 `config/loop-pilot.yaml` 仍是：

```yaml
runtime:
  state_backend: json
```

这意味着 0.4 的 SQLite 能力虽然实现了，但日用入口不是默认打开。

影响：

- `db` / `review` / `summary` / `run daily` 依赖 sqlite；
- 新用户会误以为默认配置就能完整跑 0.4；
- personal profile 尚未成型。

### 2. runtime path 没有真正隔离

`--config-dir /tmp/...` 不等于状态隔离。相对路径仍可能解析到 repo cwd 下的 `var/`。

影响：

- 测试、demo、个人日用可能串状态；
- 多 profile 不安全；
- 未来真实 GitHub / Paper / News 接入时风险扩大。

### 3. Today read model 不完整

现在 `today` 缺：

```bash
loop-pilot today list
loop-pilot today show <item_id>
loop-pilot today done <item_id>
loop-pilot today defer <item_id> --until YYYY-MM-DD
```

影响：

- 早晨 30 分钟入口不自然；
- 用户无法直接查看今日任务面板；
- `summary today` 和 `today` 命令面不闭环。

### 4. approve / resume 语义需要文档和 CLI help 收紧

当前行为是：

```text
approve -> direct finalize -> TERMINATED / SUCCEEDED
resume after approve -> cannot resume: already finalized
```

这是可以接受的，但 help 不能再暗示 approved runs 通常需要 resume。

### 5. blocked / failed report 仍太薄

阻塞路径有 artifacts，但 `report.md` 人读信息不足。

至少应包含：

- command；
- gate；
- blocked reason；
- 是否发生外部写入；
- artifact links；
- next action。

### 6. Daily run recovery 输出不够可解释

`run daily` 如果显示 recovery finding，必须列出具体 finding，否则用户会误以为状态不一致。

### 7. 0.4 仍然是 fixture/demo Loop

三个 Loop 都能跑，但都不是“真实外部世界 Agent”：

- InternLoop 还不读真实 GitHub PR/CI；
- PaperLoop 还不读真实服务器数据/论文 repo；
- DailyNewsLoop 还不读真实联网新闻。

这不是 0.4 的失败，而是 0.4 的边界。

## 0.5 完成后得到什么

0.5 = Personal Runtime Substrate。

目标不是自动修代码、自动改论文、自动抓新闻，而是把真实运行必须依赖的门、锁、身份、路径、证据、报告建好。

0.5 完成后应具备：

```text
safe local runtime
isolated personal profile
sqlite as personal backend
explicit source/auth config
branch/PR policy contract
secret redaction
failure report quality
daily task surface
schedule still fail-closed
read connector scaffolding
```

## 三个真实 Agent 的版本边界

### Real GitHub Intern Agent

```text
0.5.3.1  GitHub connector foundation，只读
0.6.0  Real InternLoop，可新分支、修代码、跑测试、开 draft PR
```

0.5.3.1 只负责安全读取：

- repo metadata；
- PR；
- issue；
- CI status；
- review comments；
- GitHub auth status。

0.6.0 才负责写：

- create branch；
- edit code；
- run tests；
- commit；
- push branch；
- open draft PR。

### Real Paper Agent

```text
0.5.2  Paper/data connector foundation，只读
0.6.1  Real PaperLoop，可读新数据、改论文、开 draft PR
```

0.5.2 只负责安全读取：

- paper repo；
- manuscript；
- claim list；
- experiment plan；
- server/data manifest；
- data checksum。

0.6.1 才负责写：

- update paper text；
- update figures/tables；
- update claim-evidence report；
- create branch；
- open draft PR。

### Real DailyNews Agent

```text
0.5.3  News connector foundation，只读 replay / live-small
0.6.2  Real DailyNewsLoop，真实联网、聚簇、核验、日报、候选导入
```

0.5.3 只负责安全读取：

- GitHub source；
- arXiv source；
- RSS source；
- finance / politics whitelist；
- source replay artifacts。

0.6.2 才负责：

- live source collection；
- event clustering；
- cross-source verification；
- unresolved signals；
- real daily-news-report；
- candidate-actions；
- explicit import to Inbox。

## 推荐版本路线

```text
0.4.0b1
Truthful Runtime Baseline
已经完成：状态、审计、review、SQLite、summary、fixture loops

0.5.2.3
Personal Runtime Substrate
目标：真实运行地基，不直接碰外部世界写操作

0.5.2.4.x
Web Evidence / Source Policy
目标：标清 replay/live/source_use/evaluator_required，不把 replay 误称 live

0.5.2.5.x
LoopPilot Evaluation Bridge
目标：evaluation_request.json -> evaluation_result.json -> pass/needs_review/blocked

0.5.3.x
Read Connector Prototypes
目标：只读 GitHub / Paper / News connector prototypes，仍不写外部世界

0.6.0
Real InternLoop
目标：新分支 -> 修代码 -> 测试 -> draft PR

0.6.1
Real PaperLoop
目标：新分支 -> 更新论文/图表 -> evidence report -> draft PR

0.6.2
Real DailyNewsLoop
目标：真实联网 -> 聚簇 -> 核验 -> daily report -> candidate import

0.7.0
Morning OS
目标：三条 loop 每天 30 分钟调度运行，但仍不自动 merge/approve
```

## 一句话

0.5 是“把门、锁、日志、身份、路径、证据系统建好”。

0.6 才是“真的派 Intern / Paper / DailyNews 去干活”。

所以项目文档里应该避免：

```text
0.5 完成 = 三个 agent 打通
```

应该统一写成：

```text
0.5 完成 = 三个真实 agent 可以安全接入
0.6 完成 = 三个真实 agent 真正打通
```
