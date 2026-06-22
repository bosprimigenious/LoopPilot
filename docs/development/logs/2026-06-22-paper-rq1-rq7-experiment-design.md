# 2026-06-22 — Paper RQ1–RQ7 Experiment Design Log

**Branch:** `stabilize/0.4-truthful-acceptance`  
**Scope:** Upgrade LoopPilot paper from research plan to research paper (markdown + LaTeX)  
**Git:** `paper/` remains gitignored; this log is **tracked**.

---

## Decision summary

We restructured evaluation from RQ1–RQ5 to **RQ1–RQ7** with named benchmarks and proprietary metrics. The thesis remains **review-gated runtime governance**, not a new agent framework.

| RQ | Bench | Key metrics | Evidence today |
|----|-------|-------------|----------------|
| RQ1 | InternLoop-GateBench (30 tasks) | FCR, RGCR, TSC | Partial — PR #8 regression + 0.4-c |
| RQ2 | ArtifactTruthBench (F1–F12) | MIR, CFR, RSA, ACR | Partial — `test_terminal_artifacts.py` |
| RQ3 | RecoveryFaultBench (R1–R8) | RCA, URBR, ERRR, HDPR | Partial — 0.4-a + defer fix |
| RQ4 | SafetyBoundaryBench (S1–S15) | UMBR, BVR, CER | Partial — `verify_0_5_prep.py` |
| RQ5 | Cross-loop suite (30 runs) | CLCC, LSPA, GRR | Partial — per-loop fixtures |
| RQ6 | Governance overhead profile | GAL, MFW, RQST, SAT | **NOT RUN** |
| RQ7 | 5–14 day daily trial | DAR, HAR, RB, FRI, USR | **NOT RUN** |

Former `rq5-daily-use.md` → **RQ7**; new **RQ5** = cross-loop generality.

---

## Benchmark design rationale

1. **InternLoop-GateBench (30 tasks):** Sized for Wilson CI at n≥30 if we later report proportions; mixes patch, blocked, clean, malformed paths. Baselines B1–B3 isolate RGT vs prompt-only vs orchestration interrupt.

2. **ArtifactTruthBench (F1–F12):** Maps Codex PR #8 cases to injectable faults; CFR measures detection before user trust, not just post-hoc audit.

3. **RecoveryFaultBench:** Separates interrupt handling (RCA/URBR) from defer persistence (HDPR/DPS).

4. **SafetyBoundaryBench:** Prep-stage fail-closed is shippable evidence; Level 4 unattended deferred to 0.5 Step 1.

5. **Cross-loop (RQ5):** Proves governance is loop-agnostic — supports Innovation 1 (Governance–Orchestration Separation).

6. **Overhead (RQ6):** Answers reviewer "is governance too heavy?" without conflating with task quality.

7. **Daily trial (RQ7):** Only source of user-burden claims; 5-day minimum, 14-day preferred.

---

## Proprietary terminology (frozen for paper)

| Term | Meaning |
|------|---------|
| **RGR** | Review-Gated Runtime — governance envelope |
| **RGT** | Review-Gated Transition — hard state edge before terminal success |
| **SAC** | Sealed Artifact Contract — terminal bundle + M1–M5 |
| **TT** | Truthful Trace — traces/summaries reflect post-gate outcomes |
| **DPS** | Deferred Persistence Semantics — defer survives sync |
| **SAO** | Sole-writer Artifact Ordering — finalizer-only manifest |

---

## Reproducibility package plan (future, not in this commit)

```
repro/
  benchmarks/
    gatebench_30/          # fixture manifest + expected gate triples
    artifact_truth_f1_f12/ # fault injection scripts
    recovery_r1_r8/
    safety_s1_s15/
  scripts/
    run_failure_injection_bench.py   # TODO
    verify_manifest_integrity.py     # TODO
  results/
    table_a_failure_injection.csv
    table_b_cross_loop.csv
    table_c_daily_trial.csv
  pin/
    commit_hash.txt
    verify_0_4_acceptance.log
```

**Pin after PR #8 merge:** commit hash, Python version, `verify_0_4_acceptance.py` 11/11 log.

---

## Honest PENDING inventory

- Full 30-task GateBench execution (beyond acceptance subset)
- Unified failure injection report (Table A consolidated)
- RQ6 overhead measurements
- RQ7 5–14 day trial
- Milestone B controlled-real E2E
- PR #8 merge commit hash in paper appendix
- `scripts/run_failure_injection_bench.py` — not implemented

**Allowed citations without bench runs:** Codex PR #8 cases 1–7 as failure-driven design evidence; expected metrics from regression tests marked "expected" not "measured."

---

## Files created/updated (paper/, gitignored)

- `experiments/rq1-review-gate.md` … `rq7-daily-use.md`, `rq5-cross-loop-generality.md`, `rq6-governance-overhead.md`
- `tables/evaluation-metrics.md`, `failure-injection-results.md`, `cross-loop-coverage.md`, `daily-use-trial.md`, `state-machine-table.md`, `baselines-ablations.md`
- `paper.md`, `abstract.md`, `outline.md`, `README.md`
- `latex/main.tex`, `latex/references.bib`

---

## Next steps (engineering)

1. Merge PR #8; pin 11/11 READY log
2. Implement `run_failure_injection_bench.py` + manifest verifier
3. Execute GateBench 30 + ArtifactTruthBench 24
4. Run RQ6 overhead instrumentation
5. Execute RQ7 trial (`logs/5-day-trial.md`)
6. Promote mermaid figures to TikZ/PDF for submission
