# 41 0.3 完成后 → 0.4 行动顺序

> **上级路线图**：[34-version-roadmap-0x.md](34-version-roadmap-0x.md)  
> **0.4 规格**：[40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)  
> **0.3 验收**：[36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)

---

## 1. 当前位置（2026-06-21）

```
[✅] 0.1 Mini-MVP
[✅] 0.2 Practical MVP（v0.2.0a1）
[🔄] 0.3 Adapter MVP（v0.3.0a1，分支 adapter-mvp-0.3）
[ ] 0.4 Personal Recovery & Daily Loop  ← 下一焦点
```

**0.3 状态**：自动化验收 PASS（109 tests）；默认 real adapter gate OK。待办：Cursor CLI 手动层、live API（可选，不阻塞 0.4-a）。

---

## 2. 0.3 收尾（进入 0.4 前）

| # | 任务 | 阻塞 0.4？ |
|---|------|------------|
| 1 | 记录 [logs/2026-06-21-0.3-acceptance-run.md](logs/2026-06-21-0.3-acceptance-run.md) 手动层结果 | 否 |
| 2 | 合并 `adapter-mvp-0.3` → `main`（若尚未） | 建议 |
| 3 | 打 tag `0.3.0a1` / 更新 CHANGELOG 条目 | 否 |
| 4 | Cursor CLI doctor 手动 PASS（有 PATH 的机器） | 否 |
| 5 | 0.1 + 0.2 回归全绿 | **是** |

**0.4 入口条件**：

- [ ] 0.3 自动化验收清单 §1–§7 全绿
- [ ] `allow_real_adapters=false` 默认仍生效
- [ ] 无 open P0 破坏 0.1 fixture

---

## 3. 0.4 实施顺序（四子阶段）

```text
Phase 1: 0.4-a 状态可靠（db + recovery）
    ↓
Phase 2: 0.4-b 任务入口（inbox / queue / today）
    ↓
Phase 3: 0.4-c 审阅（review / approve / reject / defer / cancel / resume）
    ↓
Phase 4: 0.4-d 总结与调度（summary / schedule dry-run / run all 集成）
```

### Phase 1 — 0.4-a（优先）

1. 扩展 SQLite schema + migration（`inbox_items` 等表可 Phase 2 再加，但 migration 框架 Phase 1 完成）
2. 实现 `loop-pilot db status|migrate|backup|verify`
3. 完善 `recovery-scan`；ACTING 中断 → BLOCKED
4. `pytest tests/unit/test_sqlite_state_store.py`
5. **门禁**：0.4-a 验收命令全绿 + 0.1 json 回归

### Phase 2 — 0.4-b

1. `src/loop_pilot/tasks/` inbox + queue 模块
2. CLI：`inbox add/list`、`queue list/promote`、`today`
3. DailyNews `candidate-actions` → SQLite inbox 双写
4. 单元测试 `test_inbox_queue.py`

### Phase 3 — 0.4-c

1. `review list`；与 `approvals` 表对齐
2. `defer` 新语义（相对旧 0.4 规格）
3. `resume` / `approve` / `reject` / `cancel` 与 SQLite 集成
4. 集成测试 `test_v1_recovery.py`

### Phase 4 — 0.4-d

1. `summary today` / `summary week`
2. `schedule print` / `install --dry-run`
3. `run all` 完成后自动 `summary today`（可配置）
4. 全量 0.4 验收矩阵 11 项

---

## 4. 0.4 完成后 → 0.5

| 顺序 | 版本 | 首项任务 |
|------|------|----------|
| 1 | **0.5 Personal Beta** | `loop-pilot init personal` |
| 2 | 0.6 | 跨日记忆 schema |
| 3 | 0.7 | 本地 plugins 目录约定 |
| 4 | 0.8 | getting-started 公开（可选） |

**不要**在 0.4 期间启动：PyPI release workflow、CONTRIBUTING 全套、团队 Dashboard。

---

## 5. 不要做的事

| 动作 | 原因 |
|------|------|
| 0.4 做 team / Dashboard | 归属 **1.1+** |
| 0.4 做 PyPI / init demo | 归属 **0.5 可选 / 0.8** |
| 0.4 做插件市场 | 归属 **0.7** 本地 only |
| 跳过 0.4-a 直接 inbox | 无可靠 state |
| 在 json 后端注册假成功 db 命令 | 违反 0.1 边界 |
| 把 0.3 称为「V1 完成」 | 0.4 才是日用 OS |

---

## 6. 相关文档

- [39-next-steps-0.3.md](39-next-steps-0.3.md) — 0.3 增强项（非阻塞）
- [34-version-roadmap-0x.md](34-version-roadmap-0x.md) — 完整路线图
- [logs/2026-06-21-personal-first-roadmap-pivot.md](logs/2026-06-21-personal-first-roadmap-pivot.md) — pivot 决策
