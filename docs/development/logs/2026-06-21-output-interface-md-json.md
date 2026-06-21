# 2026-06-21 决策：输出接口 — 人看 MD，机器看 JSON

## 背景

LoopPilot 每次 run 产生多种产物；此前命名与分层分散在 README、`07-data-and-reports.md`、各 Loop 实现中（如 `trace.jsonl` vs `loop_trace.jsonl`、`review-required.md` vs `review_required.md`）。0.4-c 审阅层需要统一契约，以便 CI、验收脚本与 agentic-rubric-runner 对接。

## 决策

1. **双轨输出**：人读 Markdown（`.md`），机器读 JSON / JSONL。
2. **规范路径**：`var/artifacts/<loop>/<run-id>/`，索引文件为 `artifact-manifest.json`。
3. **0.4-c 强制产物**：进入 `review list` 的 run 必须有 `review_required.md` + `gate_result.json`。
4. **manifest 扩展**：每条 artifact 增加 `human_readable: true|false`。
5. **外部评测**：agentic-rubric-runner 输出规范化为 `gate_result.json`，不合并仓库。
6. **遗留别名**：实现层可仍写 `trace.jsonl`、`review-required.md`；新 writer 用规范名；读者兼容两者直至迁移完成。

## 文档落点

| 文档 | 角色 |
|------|------|
| [47-output-interface-spec.md](../47-output-interface-spec.md) | 英文权威规格 |
| [13-输出接口-人看MD机器看JSON.md](../../zh/13-输出接口-人看MD机器看JSON.md) | 中文认知 |
| [45-personal-daily-loop-0.4c-acceptance.md](../45-personal-daily-loop-0.4c-acceptance.md) | 0.4-c 验收引用 |
| [46-review-layer-design.md](../46-review-layer-design.md) | 审阅层设计 |
| [schemas/gate_result.schema.json](../../../schemas/gate_result.schema.json) | 最小 JSON Schema |

## 未决（后续 PR）

- 代码 writer 统一文件名（underscore 规范名）
- `artifact-manifest.json` schema 正式加入 `human_readable` 字段
- 0.4-c 验收脚本 `verify_0_4c_acceptance.py`

## 相关

- [07-data-and-reports.md](../07-data-and-reports.md)
- [17-data-contracts.md](../17-data-contracts.md)
- [40-personal-daily-loop-0.4-spec.md](../40-personal-daily-loop-0.4-spec.md)
