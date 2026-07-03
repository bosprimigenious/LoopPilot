# Runtime State Machine Table

**Caption:** Primary runtime states, entry conditions, permitted actions, and exit transitions. Review substates implement RGT (Review-Gated Transition).

| State | Entered When | Allowed Actions | Exit |
|-------|--------------|-----------------|------|
| `CREATED` | Run accepted; run_id allocated | Lock workspace, load config | → `LOCKING` or `INVALID_INPUT` |
| `LOCKING` | Workspace lock requested | Acquire lock, verify identity | → `OBSERVING` or `BLOCKED` (conflict) |
| `OBSERVING` | Lock held | Gather context, fixtures | → `SELECTING` |
| `SELECTING` | Context ready | Choose task/item | → `PLANNING` |
| `PLANNING` | Task selected | Generate plan | → `POLICY_CHECK` |
| `POLICY_CHECK` | Plan ready | Policy Engine evaluate | → `ACTING` (ALLOW), `WAITING_APPROVAL` (REQUIRE), `BLOCKED` (DENY) |
| `ACTING` | Policy allows mutation | ToolBroker execute tools | → `EVALUATING`, `INTERRUPTED`, `FAILED` |
| `EVALUATING` | Act phase complete | Evaluate outcomes | → `FINALIZING`, `RETRYABLE` |
| `RETRYABLE` | Eval failed within budget | Diagnose, reflect | → `REPLANNING` → `PLANNING` |
| `FINALIZING` | Eval complete | Prepare terminal artifacts | → `PERSISTING` |
| `PERSISTING` | Artifacts staged | SQLite write, checkpoint | → `REPORTING` |
| `REPORTING` | DB persisted | Review gating, manifest seal | → `TERMINATED`, `WAITING_APPROVAL` |
| `WAITING_APPROVAL` | `patch.diff` or gate=needs_review | Human: approve/reject/defer/cancel | → `TERMINATED` (decision), `DEFERRED` (defer) |
| `DEFERRED` | `review defer --until` | Wait until date; hidden from default list | → `WAITING_APPROVAL` (due) |
| `TERMINATED` | Terminal path complete | Read-only; audit | — (resume rejected if approved patch) |
| `BLOCKED` | Policy/safety deny | Inspect artifacts | → manual recovery or abandon |
| `INTERRUPTED` | SIGINT/crash mid-phase | `recovery-scan` | → manual review or controlled resume |
| `FAILED` | Unrecoverable error | Inspect failure bundle | — |
| `PARTIAL` | **Outcome** (not phase): agent work exists, gate blocks success | Review queue | Resolved via `WAITING_APPROVAL` path |

## Invariant cross-reference

| Invariant | States affected |
|-----------|-----------------|
| I1 | `phase`/`outcome` consistency at `REPORTING`, `TERMINATED` |
| I2 | `gate_result.json` authoritative at `WAITING_APPROVAL` |
| I3 | Manifest write only at `REPORTING` via finalizer |
| I4 | `DEFERRED` persists through sync |
| I5 | `loop_trace.jsonl` written after gate downgrade |

**Reference:** `figures/runtime-state-machine.md`, PR #8 Codex fixes
