# Table A: Failure Injection Results (Template)

**Caption:** Fault injection results across ArtifactTruthBench, RecoveryFaultBench, and SafetyBoundaryBench. Baseline **B1** = pre-PR #8; **A** = full LoopPilot.

| Fault Class | Cases | Baseline (B1/B/C/D) | LoopPilot (A) | Metric | Status |
|-------------|-------|---------------------|---------------|--------|--------|
| F1 False completion | 12 patch | FCR > 0% (historical) | FCR = 0% (expected) | FCR | **Partial** (regression tests) |
| F2 Stale manifest | 4 | MIR < 100% | MIR = 100% (expected) | MIR | **Partial** (unit tests) |
| F3 Wrong report | 3 | LSPA fail | LSPA pass (expected) | LSPA | **Partial** (P1-2 fix) |
| F4 Suggestion ordering | 2 | CFR miss | CFR = 100% (expected) | CFR | **Partial** (P2-2) |
| F5 Deferred sync reset | 4 | HDPR < 100% | HDPR = 100% (expected) | HDPR | **Partial** (Case 6) |
| F6 Trace dishonesty | 2 | TSC fail | TSC = 100% (expected) | TSC | **Partial** (P2-3) |
| R1 ACTING interrupt | 3 | RCA low (conceptual) | RCA = 100% (expected) | RCA | **Partial** (0.4-a) |
| R2 Stale lock | 2 | PENDING | PENDING | RCA | PENDING |
| S1 Prep schedule install | 1 | BVR > 0% (D) | UMBR = 100% | UMBR | **Partial** (verify_0_5_prep) |
| S2 Adapter without flag | 2 | PENDING | PENDING | UMBR | PENDING |
| S3 ToolBroker deny | 3 | PENDING | PENDING | CER | PENDING |
| **Total injected** | **38** | — | — | — | **Consolidated bench PENDING** |

## Codex PR #8 evidence (design, not bench)

Cases 1–7 in `logs/codex-review-cases.md` map to rows above. These are **failure-driven design evidence**, not 30-run benchmark results.

## How to fill

Run `scripts/run_failure_injection_bench.py` (TODO) and paste measured counts. Until then, mark **Partial** where unit/acceptance tests cover the fault class.
