# 50 Personal Daily Loop — 0.5 Safe Autonomy 详细规格

> **版本标签**：`0.5.0-safe-autonomy`（与 [34-version-roadmap-0x.md](34-version-roadmap-0x.md) §7 Personal Beta 并行；本规格聚焦 **无人值守安全运行** 子线）  
> **上级路线图**：[40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) → 0.4-d 已交付 dry-run  
> **前置条件**：0.4-a/b/d 验收通过；0.4-c Review Layer 可 partial（summary Needs Review 节可空）  
> **安全基线**：[37-adapter-safety-policy.md](37-adapter-safety-policy.md)、`schemas/gate_result.schema.json`

---

## 1. 目标陈述

0.5 **Safe Autonomy** 让个人日用闭环从「手动 + dry-run 预览」升级为「可安装 OS 调度 + 后台 daemon + 分级无人值守」，且 **默认 fail-closed**：

1. **真实调度安装** — `schedule install --yes` 在 Windows Task Scheduler / cron / systemd 注册任务（可 `--uninstall`）
2. **Daemon 入口** — 长驻或单次 tick：`loop-pilot daemon run|status|stop`（0.5 最小：单次 tick + 文件锁，完整常驻可 0.5b）
3. **无人值守 daily** — `loop-pilot run daily --safe --level N` 替代仅 `--dry-run`
4. **SafetyGate 0–4** — 统一门禁评估，输出 `gate_result.json`（schema 已有），阻断越权自动化

**永不做（任何 level）**：auto approve、auto commit、auto push、绕过 ToolBroker/PolicyEngine。

---

## 2. 与 0.4-d 的增量

| 能力 | 0.4-d | 0.5 |
|------|-------|-----|
| `schedule print` / `install --dry-run` | ✅ | ✅ 保持 |
| `schedule install --yes` | ❌ `NotImplementedError` | ✅ 平台实现 |
| `run daily --dry-run` | ✅ | ✅ 等价 **Level 0** |
| `run daily`（真实 Loop） | ❌ | ✅ Level 1–4 受 SafetyGate 约束 |
| Daemon | ❌ | ✅ 最小 tick |
| 默认 schedule 命令 | `run daily --dry-run` | 配置化；默认仍为 `--safe --level 0` 直至用户提升 |

**现有代码状态（0.4-d 落地）**：

- `src/loop_pilot/scheduler/installer.py`：`preview_install()` 仅预览；`install_schedule(yes=True)` 显式 `NotImplementedError`
- `src/loop_pilot/cli_schedule.py`：`--yes` 且无 `--dry-run` 时调用 installer 并失败；默认路径写 `var/artifacts/schedule/schedule-preview.md`
- `src/loop_pilot/scheduler/profiles.py`：`DEFAULT_PROFILE.command = "loop-pilot run daily --dry-run"`

---

## 3. SafetyGate 等级（0–4）

`SafetyGate` 在每次 unattended run 开始前评估；结果写入 run artifact 目录下的 `gate_result.json`（见 schema）。

| Level | 名称 | 允许行为 | 禁止 |
|-------|------|----------|------|
| **0** | Observe | `db verify`、recovery-scan、today 预览、summary 刷新；**零** Adapter/Loop 执行 | 任何 real/mock adapter 调用 |
| **1** | Collect | Level 0 + 只读 Adapter（fetch/RSS/只读 CLI per policy） | 写 workspace、subprocess mutating |
| **2** | Mock execute | Level 1 + **mock** Loop 步骤（现有 dry-run adapter 路径） | `allow_real_adapters`、网络 mutating |
| **3** | Real guarded | Level 2 + real adapters **仅当** config + CLI 双确认；每 run 强制 `needs_review` 产物 | 自动 approve、git push |
| **4** | Real bounded | Level 3 + 预配置 loop 白名单与预算内自动 **继续**（仍每 step 写 trace）；human review 队列不自动清空 | auto merge、deploy、密钥外泄路径 |

**配置示例**（`loop-pilot.yaml`）：

```yaml
runtime:
  state_backend: sqlite
  unattended:
    default_level: 0          # 新装默认 0
    max_level: 2              # 硬顶，防止误配 4
    require_cli_flag: true    # run daily 必须显式 --safe --level N
```

**CLI**：

```bash
loop-pilot run daily --safe --level 0    # 与 0.4 --dry-run 对齐
loop-pilot run daily --safe --level 2 --allow-real-adapters  # 3+ 才生效，且需 config
```

Gate 失败时：`gate=blocked`，run 标记 failed，daemon 记录 last_error，**不** retry 无限次。

---

## 4. CLI 命令清单（0.5）

### 4.1 Schedule

| 命令 | 说明 |
|------|------|
| `loop-pilot schedule print [--target]` | 不变 |
| `loop-pilot schedule install [--dry-run]` | 不变（默认 dry-run） |
| `loop-pilot schedule install --yes [--target]` | **0.5**：写入 OS scheduler；打印 task id / cron line |
| `loop-pilot schedule uninstall [--yes]` | 移除已安装条目 |
| `loop-pilot schedule status` | 显示是否已安装、下次运行时间（只读查询 OS） |

### 4.2 Daemon（最小）

| 命令 | 说明 |
|------|------|
| `loop-pilot daemon run [--once]` | 获取 `loop:daily` 锁，执行 profile 命令；`--once` 适合 Task Scheduler |
| `loop-pilot daemon status` | 锁、上次 run id、上次 gate、pid 文件 |
| `loop-pilot daemon stop` | 协作式停止（flag 文件） |

### 4.3 Run daily

| 命令 | 说明 |
|------|------|
| `loop-pilot run daily --dry-run` | 保留；映射 Level 0 |
| `loop-pilot run daily --safe --level N` | 0.5 主路径 |
| `loop-pilot run daily`（无 flag） | **拒绝**或等价 `--safe --level 0`（实现时二选一，文档推荐拒绝） |

---

## 5. 实现分步（建议 PR 顺序）

| Step | 内容 | 验收 |
|------|------|------|
| **1** | 本规格 + prompt；`SafetyGate` 模块骨架 + Level 0 单测 | 文档 PR |
| **2** | `run daily --safe --level 0/1` + gate_result 写入 | pytest + verify_0_5a |
| **3** | `schedule install --yes`（Windows 优先）+ uninstall + status | 集成测试 mock OS |
| **4** | `daemon run --once` + profile 指向 safe daily | verify_0_5b |
| **5** | Level 2–3 mock/real 与 Today 队列执行衔接 | 依赖 0.4-c 可选 |
| **6** | `init personal`、配置迁移（Personal Beta 其余项） | 34 §7 |

---

## 6. 测试与验收

- 新脚本：`scripts/verify_0_5_acceptance.py`（或 0.5a/0.5b 拆分）
- 必跑：`pytest -q` 全绿 + 0.4b/0.4d 不回退
- 手动：在 Windows 上 `schedule install --yes --dry-run` 与 `--yes` 对比；确认 `--yes` 创建任务后 `run daily --safe --level 0` 可手动触发

---

## 7. 非目标（0.5）

- Team / cloud / Dashboard（1.3+）
- Auto approve / PR / deploy
- 完整 0.4-c Review Agent（可 stub Needs Review）
- PyPI 发布（Personal Beta 可选，见 34 §7）

---

## 8. 参考

- [48-personal-daily-loop-0.4d-acceptance.md](48-personal-daily-loop-0.4d-acceptance.md) — out of scope 已标注 0.5+
- [49-daily-summary-engine-design.md](49-daily-summary-engine-design.md)
- `src/loop_pilot/scheduler/installer.py`、`cli_schedule.py`、`runtime/daily_run.py`
