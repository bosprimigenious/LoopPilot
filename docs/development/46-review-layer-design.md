# 46 Review Layer Design

> **Status:** Design spec for 0.4-c personal review layer.  
> **Output contract:** [47-output-interface-spec.md](47-output-interface-spec.md) — authoritative per-run artifact layout (human MD vs machine JSON).  
> **Protocol:** [23-human-review-protocol.md](23-human-review-protocol.md)  
> **Acceptance:** [45-personal-daily-loop-0.4c-acceptance.md](45-personal-daily-loop-0.4c-acceptance.md)

## 1. Purpose

The review layer bridges automated loop execution and human decisions:

```text
EVALUATE → gate_result.json → review_required.md → review list → approve|reject|defer|cancel
```

Humans never parse JSON for daily workflow; machines never infer review state from Markdown alone.

## 2. Review queue sources

Runs enter the review queue when:

- Terminal outcome is `PARTIAL`, `BLOCKED`, or `EXHAUSTED`
- Run phase is `WAITING_APPROVAL`
- `gate_result.json.gate` is `needs_review` or `blocked`
- Recovery scan recommends `manual_review_required`

## 3. Artifact pairing

| Human | Machine | When |
|-------|---------|------|
| `review_required.md` | `gate_result.json` | Always for queued runs (0.4-c) |
| — | `review_suggestion.json` | When structured hint aids CLI/automation |

See [47-output-interface-spec.md §9–§10](47-output-interface-spec.md) for the required-files matrix.

## 4. CLI ↔ SQLite

Each decision (`approve`, `reject`, `defer`, `cancel`) writes a `ReviewRecord` ([17-data-contracts.md §11](17-data-contracts.md)) without rewriting the original run outcome. `review list` joins SQLite state with artifact paths from manifest.

## 5. External evaluator

[agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner) may populate `gate_result.json` in the run directory. LoopPilot normalizes gate values to `pass` | `needs_review` | `blocked`. Human entry remains `review_required.md`.

## 6. Non-goals (0.4-c)

- Auto-approve on timeout (see [23-human-review-protocol.md §7](23-human-review-protocol.md))
- Auto commit / push / deploy
- Multi-user approval chains (1.3 preview)
