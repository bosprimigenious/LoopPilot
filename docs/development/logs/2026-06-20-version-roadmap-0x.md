# 规划日志：0.x 版本体系确立

**日期**：2026-06-20  
**决策类型**：版本命名与路线图  
**状态**：已采纳

## 背景

LoopPilot 此前使用 Mini / V1 / V2 / V3 作为阶段称呼。V1 范围过大（含 SQLite、Real Adapter、scheduler、真实 workspace），导致：

- 「V1」与「Real Adapter MVP」概念混淆
- 难以判断当前应聚焦 Mini 收尾还是 Adapter 接入
- 完成度估计缺乏统一口径

## 决策

1. **采用 0.x 版本体系** 作为对外阶段命名：
   - 0.1 Mini-MVP
   - 0.2 Practical MVP
   - 0.3 Real Adapter MVP（0.3.0-adapter-mvp）
   - 0.4 Daily Automation / Recovery
   - 0.5 Public Beta / PyPI
   - 1.0 Stable personal production

2. **明确 0.3 ≠ V1**。0.3 是旧 V1-alpha 的前置，只覆盖 Mock→Real Adapter；SQLite/recovery/scheduler 归属 0.4。

3. **当前聚焦**：先完成 0.1（Mini-MVP，还差约 25–35%），再进入 0.2。**不要现在冲 0.3**。

4. **保留 Legacy 文档**：`09-versions.md`、`31-v1-v2-v3-implementation-roadmap.md` 不删除，在 `34-version-roadmap-0x.md` 中提供映射表。

5. **0.3 范围锁定**（写入 34 文档）：
   - 做：CursorCLIAdapter、OpenAICompatibleAdapter、ModelRouter、ToolBroker、受控真实 Loop
   - 不做：auto push/PR/deploy、SQLite recovery、复杂 approval、Web UI、PyPI、定时任务、向量库

## 产出文档

| 文件 | 动作 |
|------|------|
| `docs/development/34-version-roadmap-0x.md` | 新建 |
| `docs/development/33-next-steps-0.2.md` | 新建 |
| `docs/development/README.md` | 更新索引 |
| `README.md` | 轻量引用 0.x 体系 |

## 完成度与时间估计（记录基线）

| 里程碑 | 剩余 | 工期 |
|--------|------|------|
| 0.1 | 25–35% | 1–3 天 |
| 0.2 | 45–55%（自当前） | 5–10 天 |
| 0.3 | 60–70%（自当前）；0.2→0.3 +25–30% | 1–2 周 |

## 后续行动

- [ ] 0.1 八项任务全部验收（见 32、33 文档）
- [ ] 0.2 workspace 配置与测试（33 §4）
- [ ] 0.3 待 0.2 完成后按 34 §4 实施
- [ ] 考虑在 0.1 完成后更新 32 文档为「已完成」状态

## 参考

- 用户提供的版本表与 0.3 详细规格（2026-06-20 会话）
- 现有 `31-v1-v2-v3-implementation-roadmap.md` 任务分解
