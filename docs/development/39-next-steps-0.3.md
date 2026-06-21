# 39 0.3 之后下一步

0.3 **Adapter MVP** 已完成 Mock→Real 可控接入骨架。后续按 [34-version-roadmap-0x.md](34-version-roadmap-0x.md)：

## 0.4 recovery-and-automation

- SQLite state backend 与 recovery/resume
- `approve` / `reject` / `cancel` CLI
- 调度与 checkpoint 自动化

## 0.5 public-beta

- PyPI 发布、`loop-pilot init` demo
- 开源 onboarding 与 SECURITY 审计

## 0.3 后续增强（可选，非阻塞）

- httpx 注入 APIModelAdapter 重试策略
- Cursor CLI golden case（真实 worktree，非 CI）
- DailyNews live crawler（非 fixture 路径）

## 验收与回归

- 保持 0.1 fixture 与 0.2 demo profile 全绿
- 新 adapter 启用前运行 [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) 清单
