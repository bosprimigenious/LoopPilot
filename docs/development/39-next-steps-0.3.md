# 39 下一步行动：0.3 Adapter MVP

> **路线图已 pivot 为个人优先（2026-06-21）**。0.4 权威规格 → [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)；行动顺序 → [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md)。

> **前置条件**：0.2 验收全绿并已打 tag `v0.2.0a1`。在此之前**不要**在 main 上合并 real adapter 默认行为。

## 1. 阶段定位

```
[已完成] 0.1 mini           ← v0.1.0-mini (2026-06-21)
[已完成] 0.2 practical-mvp  ← v0.2.0a1 (2026-06-21)
    ↓
[当前]   0.3 adapter-mvp    ← v0.3.0b1 ToolBroker polish · tag v0.3.0b1
    ↓
[之后]   0.4 Personal Recovery & Daily Loop
```

**0.3 核心口径**：

- 真实 Adapter **可控接入**；默认 `allow_real_adapters=false`
- 做：BaseAdapter、Registry、ModelRouter、ToolBroker、CodingCLI、APIModel、`adapters list/doctor`
- **不做**：SQLite recovery、approve CLI、Web UI、插件、PyPI

## 2. 开分支前检查清单

- [x] [35-practical-mvp-0.2-acceptance.md](35-practical-mvp-0.2-acceptance.md) 全部 PASS
- [x] Tag `v0.2.0a1` 已 push
- [x] 分支 `adapter-mvp-0.3` 已创建
- [x] 阅读 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)
- [x] 阅读 [37-adapter-safety-policy.md](37-adapter-safety-policy.md)
- [x] 阅读 [38-toolbroker-design.md](38-toolbroker-design.md)

## 3. Phase 1–8 开发拆分

### Phase 1 — BaseAdapter + MockAdapter 完整化

**目标**：统一协议，Mock 行为对齐 [19-adapter-specifications.md](19-adapter-specifications.md)。

| 任务 | 产出 |
|------|------|
| 提取 `BaseAdapter` 到 `adapters/base.py` | 五方法协议 |
| 扩展 `AdapterResult` | transcript, tool_calls, usage |
| MockAdapter 场景 | timeout, invalid_schema, rate_limit |
| 单元测试 | `test_v1_adapters.py` 扩展 |

**验收**：Mock 测试全绿；无行为变更于 0.2 dry-run 路径。

---

### Phase 2 — AdapterRegistry + allow_real_adapters 门控

**目标**：factory 在 `allow_real_adapters=false` 时拒绝 cli/api。

| 任务 | 产出 |
|------|------|
| `AdapterRegistry` 注册表 | mock, coding_cli, api_model |
| `adapters/factory.py` 门控 | 配置 + runtime 读取 |
| 扩展 `test_allow_real_adapters.py` | registry 级拒绝 |

**验收**：false 时 `CodingCLIAdapter` 不可实例化；true 时可构造（仍不自动调用）。

---

### Phase 3 — ModelRouter 能力路由

**目标**：从 role 映射升级为 capability + data class + budget 过滤。

| 任务 | 产出 |
|------|------|
| `config/models.yaml` → `model_roles` | 迁移 + 文档 |
| Router 过滤链 | require capabilities, data class |
| Fallback + trace | routing artifact |
| `test_model_router.py` | 全覆盖 |

**验收**：SECRET → BLOCKED；无候选时不静默 mock（除非显式 mock run）。

---

### Phase 4 — ToolBroker 最小实现

**目标**：见 [38-toolbroker-design.md](38-toolbroker-design.md)。

| 任务 | 产出 | 状态 |
|------|------|------|
| `runtime/tool_broker.py`（或 `tools/broker.py`） | File + Command | ✅ |
| Policy 钩子 | 每次调用前 evaluate | ✅ |
| dry-run 写跳过 | plan artifact | ✅ |
| 单元测试 | policy deny, dry-run | ✅ |
| Loop 集成（0.3.0b1） | Intern/Paper/DailyNews 经 broker | ✅ |

**验收**：Intern validation 命令经 Broker；直接 subprocess 被测试禁止。 — **PASS 0.3.0b1**

---

### Phase 5 — CodingCLIAdapter

**目标**：Cursor CLI 优先；argv 模板；worktree cwd。

| 任务 | 产出 |
|------|------|
| `adapters/coding_cli.py` 生产化 | timeout, cancel, artifacts |
| Git snapshot hooks | 经 ToolBroker |
| 配置示例 | `models.yaml` cursor 条目 |
| Gated 集成测试 | env + allow_real_adapters |

**验收**：mock 路径不变；gated 测试文档化运行方式。 — **PASS 0.3.0a1**

---

### Phase 6 — APIModelAdapter

**目标**：OpenAI-compatible；structured output；脱敏。

| 任务 | 产出 |
|------|------|
| `adapters/api_model.py` 生产化 | retry, schema repair |
| Paper roles 接线 | research/writing/evaluation |
| Usage/cost 记录 | trace |

**验收**：Paper mock 路径不变；real 测试 gated。 — **PASS 0.3.0a1**

---

### Phase 7 — Loop 真实接入

**目标**：三条 Loop 各至少一个受控 real run 文档化。

| Loop | 关键工作 |
|------|----------|
| Intern | worktree + CLI + diff review + `--allow-write` |
| Paper | claim-evidence + SOURCE REQUIRED 保持 |
| DailyNews | `--real-sources` + connector 经 HttpTool |

**验收**：36 文档 Loop checklist 勾选；0.2 回归命令仍 PASS（默认配置）。 — **PASS 0.3.0b1**（ToolBroker + mock controlled runs）

---

### Phase 8 — CLI + 集成测试 + 文档

**目标**：对外可验证 0.3。

| 任务 | 产出 |
|------|------|
| `loop-pilot adapters list` | |
| `loop-pilot adapters doctor` | |
| CLI flags | `--allow-real-adapters`, `--real-sources` |
| 更新 36 验收记录 | 命令输出摘要 |
| pyproject `0.3.0a1` | 待验收后 tag |

**验收**：36 文档「Definition of done」全部满足；`pytest -q` 绿。 — **PASS 0.3.0a1 / 0.3.0b1**

## 4. 依赖关系

```text
Phase 1 ──► Phase 2 ──► Phase 3
                │
Phase 4 ────────┴──► Phase 5 ──► Phase 7
                └──► Phase 6 ──► Phase 7
                              └──► Phase 8
```

Phase 4 可与 Phase 2–3 并行（不同文件），但 Phase 7 前必须完成 4–6。

## 5. 不要做的事（0.3）

| 动作 | 原因 |
|------|------|
| 默认 `allow_real_adapters=true` | 违反安全策略 |
| 在 main 未验收前 merge real 默认 | 破坏 0.2 保证 |
| 跳过 ToolBroker 接 CLI | 无法审计 |
| 实现 `resume`/`approve` | 归属 0.4 |
| SQLite 生产切换 | 归属 0.4 |
| PyPI / init | 归属 0.5（Personal Beta，可选） |
| 称 0.3 为 "V1" | 命名混淆 |

## 6. 建议 PR 切分

| PR | 内容 |
|----|------|
| PR-1 | Phase 1–2 + 测试 |
| PR-2 | Phase 3 Router |
| PR-3 | Phase 4 ToolBroker |
| PR-4 | Phase 5–6 Adapters |
| PR-5 | Phase 7 Loop + Phase 8 CLI |
| PR-6 | 36 验收记录 + version bump + tag `v0.3.0a1` |

## 7. 0.3 之后：0.4 Personal Recovery & Daily Loop

四子阶段：**0.4-a** db/recovery → **0.4-b** inbox/queue/today → **0.4-c** review/approve/reject/defer → **0.4-d** summary/schedule dry-run

详见 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md) 与 [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md)。

## 8. 0.5 Personal Beta（非急 public）

- `loop-pilot init personal`、个人配置迁移
- **可选** PyPI（换机安装）；公开 onboarding 见 **0.8 Optional Public Beta**

> 旧「0.5 Public Beta / PyPI」规格见 [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md)（部分口径已 supersede）。

## 9. 0.3 后续增强（可选，非阻塞）

- httpx 注入 APIModelAdapter 重试策略
- Cursor CLI golden case（真实 worktree，非 CI）
- DailyNews live crawler（非 fixture 路径）

## 10. 验收与回归

- 保持 0.1 fixture 与 0.2 demo profile 全绿
- 新 adapter 启用前运行 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) 清单
- 自动化：`python scripts/verify_0_3_acceptance.py`

## 11. 相关文档

- [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) — 验收清单
- [37-adapter-safety-policy.md](37-adapter-safety-policy.md) — 安全策略
- [38-toolbroker-design.md](38-toolbroker-design.md) — ToolBroker 设计
- [34-version-roadmap-0x.md §5](34-version-roadmap-0x.md#5-03-adapter-mvp-)
- [42-1x-roadmap-personal-to-collaboration.md](42-1x-roadmap-personal-to-collaboration.md) — 1.x 路线
- [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)
- [33-next-steps-0.2.md](33-next-steps-0.2.md) — 0.2 已完成项
