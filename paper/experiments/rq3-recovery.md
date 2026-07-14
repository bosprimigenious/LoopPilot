# RQ3: Recovery Fidelity — RecoveryFaultBench

## Research question

After crashes, stale locks, or interrupted ACTING phases, does LoopPilot surface recoverable state and route ambiguous cases to manual review without unsafe auto-resume?

## Benchmark: RecoveryFaultBench

| Parameter | Specification |
|-----------|---------------|
| Interrupt classes | 8 injected scenarios (ACTING, LOCKING, PERSISTING, sync) |
| Recovery tool | `loop-pilot recovery-scan` |
| DB state | SQLite v4 with review_items |
| Deferred cases | 4 defer/sync permutations |

### Interrupt scenarios

| ID | Injection | Expected outcome |
|----|-----------|------------------|
| R1 | SIGINT mid-ACTING | `INTERRUPTED`; recovery-scan → manual_review |
| R2 | Stale lock file | `BLOCKED` or recovery flag |
| R3 | Kill during PERSISTING | Partial artifacts; no false SUCCEEDED |
| R4 | DB write fault (simulated) | `FAILED`; run_id preserved |
| R5 | Resume after cancel | Reject resume |
| R6 | Resume after reject | Reject resume |
| R7 | Defer → sync → before date | Status stays `deferred` (DPS) |
| R8 | Approve → sync | Terminal; never reopen pending |

## Baselines

| ID | Configuration |
|----|---------------|
| **A** | Full recovery + DPS |
| **B1** | No recovery-scan (conceptual) |
| **E** | Orchestration checkpoint only, no review queue |

## Metrics (proprietary)

| Metric | Symbol | Formula | Target (A) |
|--------|--------|---------|------------|
| Recovery Case Acknowledgment | **RCA** | \|injected interrupts flagged by recovery-scan\| / \|injections\| | **100%** |
| Unsafe Auto-Resume Block Rate | **URBR** | \|unsafe resume attempts blocked\| / \|unsafe attempts\| | **100%** |
| Error Recovery Route Rate | **ERRR** | \|failures with full terminal artifact set\| / \|injected failures\| | **100%** |
| Honest Deferral Persistence Rate | **HDPR** | \|defer items unchanged after sync\| / \|defer test cases\| | **100%** |

## Procedure

1. Inject R1–R6 per `experiments/failure-injection.md`
2. Run `recovery-scan`; record recommendations
3. Execute R7–R8 deferred sync matrix (Codex Case 6)
4. Verify review queue fidelity vs `gate_result.json`

## Result template

| Scenario set | RCA | URBR | ERRR | HDPR |
|--------------|-----|------|------|------|
| Interrupts R1–R6 | **100%** (0.4-a tests, expected) | **100%** (expected) | PENDING | — |
| Defer R7–R8 | — | — | — | **100%** (PR #8 fix, expected) |
| Full bench | PENDING | PENDING | PENDING | PENDING |

## Expected findings (Finding 3)

- `recovery-scan` flags ACTING interrupts without silent success
- DPS preserves `deferred_until` across `sync_from_runs` (F5)
- Terminal decisions never reopen (approved/rejected/cancelled)

## Links

- `experiments/failure-injection.md`
- `tables/failure-injection-results.md`
- `docs/development/43-personal-daily-loop-0.4a-acceptance.md`
- `logs/codex-review-cases.md` — Case 6
