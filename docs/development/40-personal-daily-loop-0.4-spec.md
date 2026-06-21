# 40 Personal Daily Loop — 0.4 详细规格

> **版本标签**：`0.4.0-personal-daily-loop`  
> **上级路线图**：[34-version-roadmap-0x.md](34-version-roadmap-0x.md) §6；**1.0 验收** → [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) §3（0.4 命令 + 30 天日用 + semver 承诺）  
> **前置条件**：0.3 Adapter MVP 验收通过（`0.3.0a1` 自动化层 + 手动层文档化）  
> **受众**：维护者本人（单用户）；**不含**团队、Dashboard、云同步

---

## 1. 目标陈述

0.4 让 LoopPilot 成为**个人每日任务 OS**：

1. **状态可靠** — SQLite 可备份、可迁移、可恢复
2. **任务入口清晰** — Anything → Inbox → Queue → Today
3. **审阅可执行** — 一条命令看清待处理，approve/reject/defer/cancel
4. **总结可复盘** — 今日/本周摘要 + 调度预览（dry-run）

成功定义：**连续 5 个工作日**仅用 CLI 完成「收任务 → 跑 Loop → 审结果 → 看总结」，无手工改 SQLite。

---

## 2. 四子阶段

| 子阶段 | 焦点 | 退出条件 |
|--------|------|----------|
| **0.4-a** | 状态可靠 | db 四命令 + recovery-scan 全绿 |
| **0.4-b** | 任务入口 | inbox/queue/today 链路 + 测试 |
| **0.4-c** | 个人审阅 | review + 四动作 CLI + 审计 |
| **0.4-d** | 每日总结 | summary + schedule dry-run + run all 集成 |

**顺序不可跳过**；0.4-b 依赖 0.4-a 的 SQLite 与 migration。

---

## 3. CLI 命令清单

### 3.1 0.4-a — 状态可靠

| 命令 | 必须 | 说明 |
|------|------|------|
| `loop-pilot db status` | ✅ | 显示 backend、schema 版本、run 计数、锁状态 |
| `loop-pilot db migrate [--dry-run]` | ✅ | 执行或预览 migration；可重复 |
| `loop-pilot db backup [--dry-run] [--dest PATH]` | ✅ | 备份 SQLite + 索引；包装 `scripts/backup_state.py` |
| `loop-pilot db verify` | ✅ | 表完整性、orphan run、manifest 一致性 |
| `loop-pilot recovery-scan` | ✅ | 扫描中断/stale run；输出建议动作 |
| `loop-pilot doctor` | ✅ | 扩展：sqlite 可写、lock_dir、recovery 配置 |

**配置要求**（启用 0.4 模式）：

```yaml
runtime:
  state_backend: sqlite          # 0.4 生产；0.1 默认 json 不变
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

**0.4-a 验收命令**：

```bash
loop-pilot db status
loop-pilot db migrate --dry-run
loop-pilot db migrate
loop-pilot db verify
loop-pilot db backup --dry-run
loop-pilot recovery-scan
loop-pilot doctor
pytest tests/unit/test_db_ops.py tests/unit/test_recovery_scan.py -q
```

**0.4-a acceptance (delivered):** See [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) for checklist, expected outputs, and delivery log [logs/2026-06-21-0.4a-delivery.md](logs/2026-06-21-0.4a-delivery.md). Chinese guide: [../zh/11-0.4a-SQLite与恢复扫描.md](../zh/11-0.4a-SQLite与恢复扫描.md).

---

### 3.2 0.4-b — 个人任务入口

| 命令 | 必须 | 说明 |
|------|------|------|
| `loop-pilot inbox add <text> [--source manual\|daily-news\|...]` | ✅ | 写入个人 Inbox（SQLite `inbox_items`） |
| `loop-pilot inbox list [--status open\|all]` | ✅ | 列出 Inbox；默认 open |
| `loop-pilot inbox archive <id>` | 可选 | 归档不再处理的条目 |
| `loop-pilot queue list` | ✅ | 已 promote、待执行的队列 |
| `loop-pilot queue promote <inbox-id> [--priority N]` | ✅ | Inbox → Queue |
| `loop-pilot queue demote <id>` | 可选 | Queue → Inbox |
| `loop-pilot today` | ✅ | 渲染今日焦点：queue 前几项 + 进行中 run + 待 review 数 |
| `loop-pilot today add <inbox-id>` | 可选 | 快捷：inbox → today 队列（等同 promote + 标记 today） |

**数据语义**：

- **Inbox**：未承诺执行的一切输入（手动、DailyNews 路由、Loop next-actions）
- **Queue**：已承诺、未分配 Run 的任务
- **Today**：当日焦点子集（Queue 的子集或视图；实现二选一，文档与 schema 一致）

DailyNews 路由：现有 `candidate-actions.json` 在 0.4-b 写入 SQLite `inbox_items`，保留 artifact 双写（兼容 0.3）。

**0.4-b 验收命令**：

```bash
loop-pilot inbox add "fix login test" --source manual --loop intern --priority 2
loop-pilot inbox list
loop-pilot queue promote <inbox-id> --loop intern
loop-pilot queue list
loop-pilot today add-queue <queue-id>
loop-pilot today
loop-pilot inbox import-daily-news --from var/artifacts/daily-news/<run-id>/candidate-actions.json --dry-run
loop-pilot inbox import-daily-news --from var/artifacts/daily-news/<run-id>/candidate-actions.json
pytest tests/unit/test_inbox_store.py tests/unit/test_queue_store.py tests/unit/test_today_service.py tests/unit/test_daily_news_importer.py -q
pytest tests/integration/test_inbox_cli.py tests/integration/test_queue_cli.py tests/integration/test_today_cli.py tests/integration/test_daily_news_to_inbox.py -q
```

> DailyNews 路由：**不**自动写入 Inbox；使用 `inbox import-daily-news`（见 [logs/2026-06-21-0.4b-acceptance-run.md](logs/2026-06-21-0.4b-acceptance-run.md)）。

---

### 3.3 0.4-c — 个人审阅

| 命令 | 必须 | 说明 |
|------|------|------|
| `loop-pilot review list` | ✅ | 待审：WAITING_APPROVAL runs + 可选 diff 摘要链接 |
| `loop-pilot approve <run-id> [--note "..."]` | ✅ | 允许继续或标记接受 |
| `loop-pilot reject <run-id> --reason "..."` | ✅ | 终止为 BLOCKED；reason 必填（可配置） |
| `loop-pilot defer <run-id> [--until YYYY-MM-DD]` | ✅ | 推迟；回到 queue/inbox |
| `loop-pilot cancel <run-id> [--reason]` | ✅ | 用户取消；释放锁 |
| `loop-pilot review show <review-id>` | ✅ | 审阅详情 + suggestion 路径 + resume  eligibility |
| `loop-pilot request-revision <run-id> --reason "..."` | ✅ | 打回修改；状态 `needs_revision` |
| `loop-pilot resume <run-id>` | ✅ | 从合法 checkpoint 恢复；**仅** explicit approve 之后 |
| `loop-pilot review batch --file PATH [--dry-run]` | 推荐 | 批量决策；无 auto-approve 失败项 |
| `loop-pilot report <run-id>` | ✅ | 摘要 + 是否可 resume |
| `loop-pilot pending` | 可选 | `review list --status pending_review` 别名 |

**defer 语义**：Run 或 Inbox 条目标记 `deferred_until`；`today` 默认隐藏，到期自动 resurfaced。

**0.4-c 验收命令**：

```bash
loop-pilot run intern --workspace examples/intern_demo --dry-run
loop-pilot review list
loop-pilot review show --run-id <run-id>
loop-pilot approve <run-id> [--note "..."]
loop-pilot reject <run-id> --reason "needs more tests"
loop-pilot defer <run-id> --until 2026-06-25
loop-pilot cancel <run-id>
loop-pilot request-revision <run-id> --reason "expand tests"
loop-pilot resume <run-id>    # 仅 explicit approve 之后
loop-pilot review batch --file decisions.json --dry-run
python scripts/verify_0_4c_acceptance.py
pytest tests/integration/test_review_cli.py tests/integration/test_v1_recovery.py -q
```

**0.4-c acceptance (planned):** See [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) for checklist, schema, ReviewAgent contract, and 8 must-haves. Architecture: [46-review-layer-design.md](46-review-layer-design.md). Chinese guide: [../zh/12-0.4c-审阅与决策层.md](../zh/12-0.4c-审阅与决策层.md). Spec log: [logs/2026-06-21-0.4c-spec-and-prompt.md](logs/2026-06-21-0.4c-spec-and-prompt.md).

**Core principle:** AI suggests only (`review_suggestion.json`); human makes final decision. No auto-approve, no bypass review queue.

---

### 3.4 0.4-d — 每日总结与调度

| 命令 | 必须 | 说明 |
|------|------|------|
| `loop-pilot summary today` | ✅ | 生成/刷新 `var/artifacts/daily/<date>/daily-summary.md` |
| `loop-pilot summary week` | ✅ | 近 7 日 rollup Markdown（个人周报雏形） |
| `loop-pilot schedule print` | ✅ | 打印 cron/systemd/Task Scheduler 配置（不写系统） |
| `loop-pilot schedule install --dry-run` | ✅ | 预览安装命令 |
| `loop-pilot schedule install --yes` | 后期 | 实际注册 OS 任务（单一入口） |
| `loop-pilot run all` | ✅ | 与 summary today 集成；DailyNews→Intern→Paper |

**daily-summary.md 七段**（与 [33-version-roadmap.md §0.4](33-version-roadmap.md) 对齐）：

1. 今日最重要结论（≤3 条）
2. InternLoop 摘要
3. PaperLoop 摘要
4. DailyNews 摘要
5. 等待人工（review list 链接）
6. 明日优先（来自 queue/inbox）
7. 元数据（run_ids、耗时、adapter 费用摘要）

**0.4-d 验收命令**：

```bash
loop-pilot run all --profile demo
loop-pilot summary today
loop-pilot summary week
loop-pilot schedule print
loop-pilot schedule install --dry-run
python scripts/install_scheduler.py --dry-run

# 0.1 回归（json 后端）
loop-pilot run all --fixture-set mini --dry-run
pytest -q
```

---

## 4. SQLite 表（0.4 目标）

在 [33-version-roadmap.md §0.4](33-version-roadmap.md) 既有表基础上，**0.4-b 增补**：

| 表 | 用途 |
|----|------|
| **inbox_items** | `id`, `title`, `body`, `source`, `status`, `created_at`, `expires_at` |
| **queue_items** | `id`, `inbox_id` FK, `priority`, `status`, `promoted_at` |
| **today_items** | `id`, `queue_id` FK, `date`, `status`（若 today 为实体表；否则为 queue 视图字段） |

既有：`runs`, `checkpoints`, `approvals`, `events`, `artifacts`, `schema_migrations`。

---

## 5. 模块清单

| 模块 | 路径 | 子阶段 |
|------|------|--------|
| SQLite store | `src/loop_pilot/storage/sqlite.py` | 0.4-a |
| migrations | `src/loop_pilot/storage/migrations.py` | 0.4-a |
| inbox/queue | `src/loop_pilot/tasks/`（新建） | 0.4-b |
| approvals | `src/loop_pilot/runtime/approvals.py` | 0.4-c |
| recovery | `src/loop_pilot/runtime/recovery.py` | 0.4-a/c |
| daily_summary | `src/loop_pilot/reporting/daily_summary.py` | 0.4-d |
| schedule CLI | `src/loop_pilot/cli_schedule.py` | 0.4-d |
| db CLI | `src/loop_pilot/cli_db.py` | 0.4-a |

---

## 6. 验收矩阵（0.4 完成定义）

| # | 项 | 子阶段 |
|---|-----|--------|
| 1 | `db migrate` 可重复；`db verify` 无 error | a |
| 2 | 强制中断 run 无半写终态 | a |
| 3 | `recovery-scan` 识别 stale/interrupted | a |
| 4 | inbox add → queue promote → today 可追踪 | b |
| 5 | DailyNews 候选进入 inbox（SQLite） | b |
| 6 | `review list` 与 WAITING_APPROVAL 一致 | c |
| 7 | approve/reject/defer/cancel 可审计 | c |
| 8 | `resume` 不绕过 Policy；不重复 artifact | c |
| 9 | `summary today` 七段结构完整 | d |
| 10 | `schedule install --dry-run` 不写系统 | d |
| 11 | `state_backend=json` 时 0.1 全绿 | 全阶段 |

---

## 7. 明确不做（0.4 边界）

| 排除项 | 归属 | 说明 |
|--------|------|------|
| 团队 / 多用户 / RBAC | **1.3 preview** | 无 `project create` |
| Web Dashboard | **1.3 preview** | CLI only |
| 云同步 / 远程 state | **1.3 preview** | 本地 SQLite |
| 文件包协作 / handoff | **1.2** | 见 [42-1x-roadmap](42-1x-roadmap-personal-to-collaboration.md) §5 |
| 插件市场 / 远程安装 | **0.7** | 0.4 不做 plugins CLI |
| PyPI / `init demo` | **0.5 / 0.8** | 0.4 用 editable install |
| 公开 onboarding 文档 | **0.8** | |
| 向量库 / RAG | 非 0.x 急项 | |
| 自动 push / PR / deploy | 永不 | |

---

## 8. 与旧「0.4 recovery-and-automation」差异

| 项 | 旧规格 | 本规格（个人 daily loop） |
|----|--------|---------------------------|
| 任务 OS | 无 inbox CLI | **inbox / queue / today** |
| 审阅 | approve/reject/cancel | + **review list**、**defer** |
| 总结 | summary today | + **summary week** |
| db CLI | migrate/backup 脚本 | 统一 **`db status/migrate/backup/verify`** |
| 团队 | 无（旧 0.8 紧跟） | 团队 **1.3 preview**；协作 **1.2** |

---

## 9. 相关文档

- [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md) — **0.4-c 验收清单（planned）**
- [46-review-layer-design.md](46-review-layer-design.md) — **0.4-c Review Layer 架构**
- [44-personal-daily-loop-0.4b-acceptance.md](44-personal-daily-loop-0.4b-acceptance.md) — **0.4-b 验收清单**
- [43-personal-daily-loop-0.4a-acceptance.md](43-personal-daily-loop-0.4a-acceptance.md) — **0.4-a 验收清单**
- [logs/2026-06-21-0.4a-delivery.md](logs/2026-06-21-0.4a-delivery.md) — 0.4-a 交付记录
- [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md) — 实施顺序
- [08-security-and-recovery.md](08-security-and-recovery.md) — recovery 规则
- [18-state-transition-spec.md](18-state-transition-spec.md) — 状态机
- [23-human-review-protocol.md](23-human-review-protocol.md) — 审阅协议
- [07-data-and-reports.md](07-data-and-reports.md) — 产物契约
- [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) — 1.0 验收（基于本文 0.4 能力）
