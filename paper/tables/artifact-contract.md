# Table 2: Terminal Artifact Contract

| Artifact | Format | Required | `human_readable` | Purpose |
|----------|--------|----------|------------------|---------|
| `run_meta.json` | JSON | Yes | false | Run ID, loop type, timestamps, phase/outcome |
| `gate_result.json` | JSON | Yes | false | Normalized gate: `pass` \| `needs_review` \| `blocked` |
| `tool-results.json` | JSON | Yes | false | ToolBroker audit trail (empty allowed with explanation) |
| `report.md` | Markdown | Yes | true | Primary human summary (loop-specific names via priority) |
| `artifact-manifest.json` | JSON | Yes | false | Sealed index; sha256 recomputed from disk; excludes self |
| `loop_trace.jsonl` | JSONL | Yes | false | Phase transitions; must reflect gated outcome |
| `trace.jsonl` | JSONL | Optional | false | Fine-grained runtime events |
| `review_required.md` | Markdown | If queued | true | Human-facing review brief |
| `review_suggestion.json` | JSON | If suggested | false | Structured hint (written before manifest finalize) |
| `patch.diff` | diff | InternLoop patch runs | false | Triggers review gate |
| `candidate-actions.json` | JSON | DailyNewsLoop | false | Inbox candidates (no direct code mutation) |

**Manifest invariants (M1–M5):**

| ID | Invariant |
|----|-----------|
| M1 | Manifest lists every on-disk artifact in run directory except itself |
| M2 | Every listed entry's `sha256` and `size_bytes` are recomputed from final disk content |
| M3 | Manifest is written exactly once via atomic `.tmp` + replace |
| M4 | All required terminal artifacts exist before manifest write |
| M5 | `kind` and `human_readable` metadata preserved across finalize scan |

**Caption:** Terminal artifact contract for LoopPilot runs. The manifest finalizer in `terminal_artifacts.py` is the sole writer of `artifact-manifest.json` (G2, M1–M3).
