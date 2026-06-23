# Main CLI 功能完善计划（2026-06-23）

## 目标

把 LoopPilot 从“验收脚本绿、fixture 能跑”推进到“个人每天可以稳定使用的 CLI”。重点不是继续堆 0.5 功能，而是补足真实使用时的入口、状态可见性和恢复解释。

## 目标使用流

每天早上 30 分钟：

```bash
loop-pilot doctor
loop-pilot run daily --dry-run
loop-pilot today list
loop-pilot review list
loop-pilot summary today
```

对于产生 patch 的开发任务：

```bash
loop-pilot run intern --workspace <project> --dry-run
loop-pilot review show <run_id>
loop-pilot report <run_id>
loop-pilot approve <run_id> --note "checked"
loop-pilot inspect <run_id>
```

对于 paper loop：

```bash
loop-pilot run paper --workspace <paper_dir> --review-only
loop-pilot report <run_id>
loop-pilot summary today
```

对于 daily news：

```bash
loop-pilot import-daily-news <snapshot.json>
loop-pilot run daily-news --source-profile personal --dry-run
loop-pilot inbox list
loop-pilot today add <item_id>
```

## V0.4.x：真实日用打磨

### 1. Personal SQLite profile

新增：

```text
config/profiles/personal-sqlite.yaml
config/profiles/smoke-sqlite.yaml
```

必要能力：

- 状态路径可显式隔离；
- `doctor` 显示当前 profile 与 runtime root；
- `db status` 显示绝对 sqlite path；
- README 给出 3 分钟初始化路径。

验收：

```bash
loop-pilot --config-dir config/profiles/personal-sqlite doctor
loop-pilot --config-dir config/profiles/personal-sqlite db status
```

### 2. Today read model

补齐命令：

```bash
loop-pilot today list
loop-pilot today show <item_id>
loop-pilot today done <item_id>
loop-pilot today defer <item_id> --until YYYY-MM-DD
```

核心原则：

- Today 是用户当天工作面板；
- Inbox 是候选池；
- Queue 是计划队列；
- Summary 是日报视图。

验收：

- `today list` 与 `summary today` Today 区域一致；
- 空状态不报错；
- 已完成/延期任务不会继续显示为今日待做。

### 3. Review gate UX

当前 review gate 基本可用，但要把语义做硬：

```text
WAITING_APPROVAL + needs_review -> approve -> TERMINATED/succeeded
WAITING_APPROVAL + needs_review -> reject -> TERMINATED/blocked
WAITING_APPROVAL + needs_review -> cancel -> TERMINATED/cancelled
```

当前版本建议采用 approve-finalizes 模式，不再暗示 approve 后需要 resume。

需要修改：

- `resume` help 文案；
- review docs；
- README quickstart；
- `review show` 输出中加入下一步建议。

### 4. Report quality

报告要从“机器验收 artifacts”升级为“人能快速读懂”。

每个 terminal report 至少包含：

- run id / loop type / phase / outcome；
- 用户命令；
- 关键判断；
- 失败或阻塞原因；
- 产物目录；
- 下一步。

特别是 blocked report，不能只写 `Outcome: blocked`。

### 5. Daily run explanation

`run daily --dry-run` 是用户最常看的命令，输出必须高度可信。

建议输出结构：

```text
Daily run (dry-run): YYYY-MM-DD
  profile: personal-sqlite
  db verify: OK
  recovery: OK / N finding(s) with details
  today: N item(s)
  inbox: N new candidate(s)
  review: N pending
  summary: path
```

如果 recovery 有 finding，必须列出具体条目或写进 summary。

## V0.5-prep：安全自治前置

当前 `verify_0_5_prep.py` 正确输出：

```text
0.5-prep: PASS
0.5-ready: NOT READY
```

这条线是对的。不要急着把 0.5-ready 改绿。

下一步只做三件事：

1. 保持 schedule install 默认 blocked；
2. 明确 safety levels；
3. 给真实 adapter 接入前加 dry-run audit。

真实无人值守必须等：

- personal sqlite profile 稳定；
- today/review/summary 体验稳定；
- failure report 足够可读；
- recovery finding 完全可解释；
- live connector 有隔离测试。

## V0.6-preview：Real Connected Loops

0.6 不是全自动无人值守，而是 `Real Connected Loops, but Controlled`。Intern、Paper、DailyNews 都可以连接真实外部世界，但所有写动作必须走新分支、draft PR、RunRecord、artifact、human review。详见：

- [57-real-connected-loops-0.6-spec.md](57-real-connected-loops-0.6-spec.md)
- [58-github-identity-branch-pr-skill-model.md](58-github-identity-branch-pr-skill-model.md)
- [56-dailynews-clustering-layer-plan.md](56-dailynews-clustering-layer-plan.md)
- [59-version-boundary-0.5-0.6-real-agents.md](59-version-boundary-0.5-0.6-real-agents.md)
- [60-0.5-development-plan-and-0.4-gap-audit.md](60-0.5-development-plan-and-0.4-gap-audit.md)

版本口径必须统一：

```text
0.5 完成 = 三个真实 agent 可以安全接入
0.6 完成 = 三个真实 agent 真正打通
```

## 暂不做

以下内容不应在当前阶段推进：

- 自动修改真实工作仓库；
- 自动联网抓新闻并创建任务；
- 自动 approve/reject；
- 自动 schedule install；
- PyPI 正式发布；
- 宣称 0.5 ready。

## 推荐下一轮 Cursor 任务

```text
You are improving LoopPilot main CLI usability after 0.4 READY.

Do not add new autonomy.
Do not weaken tests.
Do not change 0.5-ready to READY.

Implement:
1. explicit runtime path resolution and config/profile isolation;
2. personal-sqlite and smoke-sqlite config examples;
3. today list/show/done/defer commands;
4. clarify approve-finalizes vs resume semantics;
5. richer blocked/failure report.md;
6. daily run recovery finding details.

Required verification:
ruff check .
pytest -q
python scripts/verify_0_3_acceptance.py
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
manual CLI smoke with isolated config.
```
