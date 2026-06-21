# 13 输出接口：人看 Markdown，机器看 JSON

**一句话：人看 Markdown，机器看 JSON。**

英文权威规格：[development/47-output-interface-spec.md](../development/47-output-interface-spec.md)

---

## 为什么分两层

| 谁 | 读什么 | 用途 |
|----|--------|------|
| **你（人）** | `.md` 报告 | 快速理解结论、做审阅决定 |
| **CI / 验收脚本 / 外部评测** | `.json` / `.jsonl` | 结构化判断 pass / needs_review / blocked |

不要把 Markdown 当状态真相来源；也不要只用 JSON 代替可读报告。

---

## 每次 run 有哪些文件

目录（规范路径）：

```text
var/artifacts/<loop>/<run-id>/
├── artifact-manifest.json      # 本 run 全部产物索引（机器）
├── run_meta.json               # run 身份、配置快照、终态（机器）
├── loop_trace.jsonl            # 阶段/轮次事件流（机器）
├── tool-results.json           # ToolBroker 审计（有工具调用时）
├── adapter-call-trace.jsonl    # Adapter 调用记录（有 Adapter 时）
├── gate_result.json            # 门禁/评测结果（审阅 run 必填，0.4-c）
├── report.md                   # 主报告（人读）
├── review_required.md          # 审阅入口（人读，0.4-c 重点）
├── next_actions.md             # 后续行动（人读）
└── review_suggestion.json      # 审阅建议结构化版（机器，可选）
```

**每日汇总（0.4-d，不是单次 run）：** `var/artifacts/daily/<日期>/daily-summary.md`

各 Loop 还可能有专有文件（如 `patch.diff`、`candidate-actions.json`），一律登记在 `artifact-manifest.json` 里。

---

## 0.4-c 重点：`review_required.md`

0.4-c 个人审阅层把 **`review_required.md` 作为日常审阅入口**：

- `loop-pilot review list` 列出的 run，必须同时有 `review_required.md` 和 `gate_result.json`
- 人先打开 `review_required.md`：推荐动作、理由、勾选清单
- 机器用 `gate_result.json` / `review_suggestion.json` 做自动化判断

与 0.4-b 的区别：0.4-b 只管 inbox/queue/today；0.4-c 才强制审阅产物与 `approve` / `reject` / `defer` CLI。

详见 [12-0.4c-审阅与决策层.md](12-0.4c-审阅与决策层.md)、[08-0.4-个人日用闭环.md](08-0.4-个人日用闭环.md)。

---

## 示例片段

### `report.md`（简化）

```markdown
---
schema_version: "1.0"
run_id: "2026-06-21T120000+0800-intern-001"
loop_type: intern
terminal_state: PARTIAL
generated_at: "2026-06-21T12:25:00+08:00"
artifact_manifest: artifact-manifest.json
---

# Intern Development Report

## Objective
Fix failing login test in examples/intern_demo.

## Outcome
PARTIAL — patch applied; scope review required.

## Evidence
- tool-results.json
- patch.diff

## Verification
- pytest tests/test_login.py: pass
- full suite: not run
```

### `review_required.md`（简化）

```markdown
# Review Required

Run: `2026-06-21T120000+0800-intern-001`
Loop: intern
Outcome: partial

## Recommended action

**reject**

Patch modified files outside allowed_paths.

## Checklist

- [ ] Confirm intended file scope
- [ ] Re-run with narrowed objective
```

---

## 与 agentic-rubric-runner 的关系

| 组件 | 职责 |
|------|------|
| **LoopPilot** | 跑 Loop、写报告与 trace、生成 manifest |
| **[agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner)** | 评分、审计、无人值守 gate |

集成约定：

- 外部评测输出**规范化**为 run 目录下的 `gate_result.json`
- `gate` 取值：`pass` | `needs_review` | `blocked`
- 需要人审时，可同时写 `review_suggestion.json`，与 `review_required.md` 内容一致、格式不同

LoopPilot 负责「跑」；agentic-rubric-runner 负责「判」。两者通过 JSON 产物对接，不合并仓库。

---

## 相关文档

- 英文规格：[47-output-interface-spec.md](../development/47-output-interface-spec.md)
- 数据契约：[17-data-contracts.md](../development/17-data-contracts.md)
- 报告策略：[07-data-and-reports.md](../development/07-data-and-reports.md)
- 0.4-c 审阅：[12-0.4c-审阅与决策层.md](12-0.4c-审阅与决策层.md)
- 决策记录：[logs/2026-06-21-output-interface-md-json.md](../development/logs/2026-06-21-output-interface-md-json.md)
