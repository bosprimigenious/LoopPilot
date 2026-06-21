# 43 Personal Daily Loop — 0.4-a 验收清单

> **版本标签**：`0.4.0a1`  
> **上级规格**：[40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.1  
> **分支**：`personal-daily-loop-0.4-a`

---

## 1. 范围

0.4-a 交付**状态可靠**能力：

| 命令 | 说明 |
|------|------|
| `loop-pilot db status` | backend、schema 版本、run 计数、锁文件 |
| `loop-pilot db migrate [--dry-run]` | 幂等 migration |
| `loop-pilot db backup [--dry-run] [--dest PATH]` | 时间戳备份，不覆盖旧备份 |
| `loop-pilot db verify` | 表完整性、orphan checkpoint、半写终态 |
| `loop-pilot recovery-scan` | stale/interrupted/WAITING_APPROVAL/ACTING/FAILED/stale lock |
| `loop-pilot doctor` | json 模式提示；sqlite 模式检查可写性与 schema |

**明确不在 0.4-a**：inbox/queue/today (0.4-b)、review/approve/defer (0.4-c)、summary/schedule (0.4-d)。

---

## 2. 配置

默认 `config/loop-pilot.yaml` 保持 `state_backend: json`（0.1 回归不变）。

0.4-a 验收使用 SQLite 配置（已提交 fixture）：

```bash
--config-dir tests/fixtures/acceptance_0_4a/config
```

或本机 `config.local/`（不入库）覆盖：

```yaml
runtime:
  state_backend: sqlite
  sqlite_path: var/state/loop_pilot.db
  lock_dir: var/locks
```

---

## 3. 验收命令

```bash
CFG=tests/fixtures/acceptance_0_4a/config

loop-pilot --config-dir $CFG db status
loop-pilot --config-dir $CFG db migrate --dry-run
loop-pilot --config-dir $CFG db migrate
loop-pilot --config-dir $CFG db verify
loop-pilot --config-dir $CFG db backup --dry-run
loop-pilot --config-dir $CFG recovery-scan
loop-pilot --config-dir $CFG doctor

# 0.1 回归（json 默认）
loop-pilot doctor
pytest tests/unit/test_db_ops.py tests/unit/test_recovery_scan.py -q
pytest -q
```

---

## 4. 验收矩阵

| # | 项 | 结果 |
|---|-----|------|
| 1 | `db migrate` 可重复；第二次无 pending | PASS |
| 2 | `db verify` 无 error | PASS |
| 3 | backup 时间戳目录；冲突时 `-NNN` 后缀 | PASS |
| 4 | `recovery-scan` 识别 ACTING → `manual_review_required` | PASS |
| 5 | ACTING 中断不 auto-resume | PASS（单元测试 + scan 逻辑） |
| 6 | `state_backend=json` 时 doctor 提示 sqlite | PASS |
| 7 | json 后端 `db migrate` 拒绝 | PASS |
| 8 | 全量 pytest 不退化 | PASS |

---

## 5. 模块清单

| 模块 | 路径 |
|------|------|
| migrations v1 | `src/loop_pilot/storage/migrations.py` |
| db ops | `src/loop_pilot/storage/db_ops.py` |
| recovery scan | `src/loop_pilot/runtime/recovery_scan.py` |
| db CLI | `src/loop_pilot/cli_db.py` |
| 测试 | `tests/unit/test_db_ops.py`, `tests/unit/test_recovery_scan.py` |

Schema v1 表：`runs`, `checkpoints`, `reviews`, `artifact_manifests`, `events`, `run_locks`, `schema_migrations`。

---

## 6. 2026-06-21 验收输出摘要

```text
db status          → backend sqlite, schema_version 1, run_count 0
db migrate --dry-run → No pending migrations
db migrate         → Database schema up to date
db verify          → Verify: OK
db backup --dry-run → Would back up db/state/config to var/backups/<timestamp>/
recovery-scan      → Recovery scan: OK (no issues)
doctor (sqlite)    → Doctor: OK
doctor (json)      → Doctor: OK + Warning: state_backend=json
pytest -q          → 141 passed
```

---

## 7. 下一步

0.4-b：inbox / queue / today CLI 与 SQLite `inbox_items` 表。见 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) §3.2。
