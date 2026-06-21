# 39 0.3 之后下一步

> **路线图已 pivot 为个人优先（2026-06-21）**。0.4 权威规格 → [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)；行动顺序 → [41-next-steps-after-0.3.md](41-next-steps-after-0.3.md)。

0.3 **Adapter MVP**（`0.3.0a1`）Mock→Real 可控接入骨架已就绪。后续按 [34-version-roadmap-0x.md](34-version-roadmap-0x.md)：

## 0.4 Personal Recovery & Daily Loop

四子阶段：**0.4-a** db/recovery → **0.4-b** inbox/queue/today → **0.4-c** review/approve/reject/defer → **0.4-d** summary/schedule dry-run

详见 [40-personal-daily-loop-0.4-spec.md](40-personal-daily-loop-0.4-spec.md)。

## 0.5 Personal Beta（非急 public）

- `loop-pilot init personal`、个人配置迁移
- **可选** PyPI（换机安装）；公开 onboarding 见 **0.8**

> 旧「0.5 Public Beta / PyPI」规格见 [logs/2026-06-20-0.5-public-beta-spec.md](logs/2026-06-20-0.5-public-beta-spec.md)（部分口径已 supersede）。

## 0.3 后续增强（可选，非阻塞）

- httpx 注入 APIModelAdapter 重试策略
- Cursor CLI golden case（真实 worktree，非 CI）
- DailyNews live crawler（非 fixture 路径）

## 验收与回归

- 保持 0.1 fixture 与 0.2 demo profile 全绿
- 新 adapter 启用前运行 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) 清单
