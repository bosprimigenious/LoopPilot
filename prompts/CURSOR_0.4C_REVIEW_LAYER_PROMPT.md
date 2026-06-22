# Cursor Prompt: 0.4-c Review Layer

> **Priority 1 — BLOCKER for 0.5:** Do not start [0.5 Safe Autonomy](CURSOR_0.5_SAFE_AUTONOMY_PROMPT.md) until this layer passes `python scripts/verify_0_4c_acceptance.py` and [Truthful 0.4](../docs/development/50-0.4-stabilization-and-truthful-acceptance.md) Milestone A is green. See [logs/2026-06-21-truthful-0.4-acceptance.md](../docs/development/logs/2026-06-21-truthful-0.4-acceptance.md).

## 目标（中文）

实现 0.4-c 个人审阅层：`review list`、`approve`、`reject`、`defer`、`cancel`、`resume`，并确保每次进入审阅队列的 run 产出规范 artifacts。

## Output Interface（English — mandatory）

Follow **[docs/development/47-output-interface-spec.md](../docs/development/47-output-interface-spec.md)** for all run outputs.

### Mandatory artifacts (review-queue runs)

| File | Layer | Required |
|------|-------|----------|
| `review_required.md` | Human | Yes |
| `gate_result.json` | Machine | Yes |
| `artifact-manifest.json` | Machine | Yes — list all artifacts with `human_readable` |
| `report.md` | Human | Yes |
| `loop_trace.jsonl` | Machine | Yes |
| `run_meta.json` | Machine | Yes |
| `review_suggestion.json` | Machine | When `gate` is `needs_review` or `blocked` |

### Rules

- Humans read Markdown; CI and acceptance assert JSON/manifest only.
- Do not parse Markdown for review state or gate verdict.
- External evaluator (agentic-rubric-runner) normalizes to `gate_result.json`.
- Canonical path: `var/artifacts/<loop>/<run-id>/`.
- Legacy names (`review-required.md`, `trace.jsonl`) may be read for compatibility; new writers use canonical names.

### References

- [45-personal-daily-loop-0.4c-acceptance.md](../docs/development/45-personal-daily-loop-0.4c-acceptance.md)
- [46-review-layer-design.md](../docs/development/46-review-layer-design.md)
- [23-human-review-protocol.md](../docs/development/23-human-review-protocol.md)
- Chinese: [docs/zh/13-输出接口-人看MD机器看JSON.md](../docs/zh/13-输出接口-人看MD机器看JSON.md)

## Task / Constraints

- SQLite `reviews` table on each decision
- `reject` requires `--reason`
- No auto-approve, auto-commit, auto-push
- Tests: integration for review CLI + artifact presence per 45 checklist
