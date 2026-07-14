# Figure 2: Runtime State Machine and Review Substates

```mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> LOCKING
    LOCKING --> OBSERVING
    OBSERVING --> SELECTING
    SELECTING --> PLANNING
    PLANNING --> POLICY_CHECK

    POLICY_CHECK --> WAITING_APPROVAL: REQUIRE_APPROVAL
    POLICY_CHECK --> BLOCKED: DENY
    POLICY_CHECK --> ACTING: ALLOW

    ACTING --> EVALUATING
    EVALUATING --> RETRYABLE: retry budget
    RETRYABLE --> DIAGNOSING
    DIAGNOSING --> REFLECTING
    REFLECTING --> REPLANNING
    REPLANNING --> PLANNING

    EVALUATING --> FINALIZING: pass or partial terminal
    EVALUATING --> NEEDS_HUMAN: needs_review
    NEEDS_HUMAN --> WAITING_APPROVAL

    FINALIZING --> PERSISTING
    PERSISTING --> REPORTING

    REPORTING --> WAITING_APPROVAL: patch.diff / needs_review
    REPORTING --> TERMINATED: gate pass or post-approve

    WAITING_APPROVAL --> TERMINATED: approve → SUCCEEDED
    WAITING_APPROVAL --> TERMINATED: reject / cancel
    WAITING_APPROVAL --> DEFERRED: defer --until

    DEFERRED --> WAITING_APPROVAL: deferred_until due

    BLOCKED --> TERMINATED
    note right of WAITING_APPROVAL
        Review substates:
        gate=needs_review
        outcome=PARTIAL
        NOT completed in summary
    end note
```

## Runtime invariants I1–I5

| ID | Invariant | Violation example (PR #8) |
|----|-----------|---------------------------|
| **I1** | `phase` and `outcome` are independent; terminal success requires consistent pair | `TERMINATED` + `SUCCEEDED` while `gate=needs_review` (P0/P2-1) |
| **I2** | `gate_result.json` is authoritative for review queue membership | Summary ignores gate, lists patch run as Completed |
| **I3** | No loop may write final `artifact-manifest.json` | InternLoop legacy manifest write (P1-3) |
| **I4** | Review substates persist until human decision or defer expiry | `upsert_pending` resetting deferred → pending (P2) |
| **I5** | `loop_trace.jsonl` terminal event reflects post-gate outcome | Trace shows succeeded before review downgrade (P2-3) |

## Caption

**Figure 2.** LoopPilot runtime state machine with review substates. TikZ source: `latex/main.tex` (Figure~\ref{fig:state-machine}). Mermaid below is a supplementary sketch.

## Reviewer defense

Reviewers may ask: "Why not treat approval as just another planning step?" Because planning errors are recoverable by replanning; **false terminal success** destroys auditability—downstream summaries, sync jobs, and humans believe work is done. LoopPilot makes review a **hard state**, not a prompt suggestion.
