# RQ1: Review Gate Correctness — InternLoop-GateBench

## Research question

Does LoopPilot prevent mutating runs (especially InternLoop patch runs) from reaching terminal success before explicit human approval?

## Benchmark: InternLoop-GateBench

**Purpose:** Reproducible evidence for review-gate correctness independent of ad-hoc acceptance scripts.

| Parameter | Specification |
|-----------|---------------|
| Task count | **30** curated InternLoop scenarios |
| Task mix | 12 patch-producing, 8 policy-blocked, 6 no-patch success, 4 malformed fixture |
| Adapter | MockAdapter (deterministic); Milestone B adds controlled-real overlay (NOT READY) |
| Seeds | Fixed fixture IDs in `tests/fixtures/`; manifest `bench_seed` in run_meta |
| Runs per config | 1 run per task × baseline (90 total for A vs B1–B3) |

### Task categories (30)

1. **T01–T12 (patch):** Emit `patch.diff`; must end `WAITING_APPROVAL` / `PARTIAL` / `needs_review`
2. **T13–T20 (blocked):** Policy deny before patch; `BLOCKED` or `FAILED` with audit
3. **T21–T26 (clean success):** No patch; may reach `SUCCEEDED` without review
4. **T27–T30 (malformed):** Invalid fixture; `INVALID_INPUT` with honest artifacts

## Baselines

| ID | Name | Configuration |
|----|------|---------------|
| **A** | Full LoopPilot | PR #8 semantics: RGT enforced, summary exclusion |
| **B1** | No review gate | Historical pre-PR #8: patch → `TERMINATED`/`SUCCEEDED` |
| **B2** | Prompt-only review | Advisory Markdown; no `WAITING_APPROVAL` state |
| **B3** | Orchestration interrupt | LangGraph-style pause node without gate authority |

**Ablations C–E** (artifact/safety) are out of scope for RQ1; see RQ2/RQ4.

## Metrics (proprietary)

| Metric | Symbol | Formula | Target (A) |
|--------|--------|---------|------------|
| False Completion Rate | **FCR** | \|runs with summary Completed ∧ gate=needs_review\| / \|patch runs\| | **0%** |
| Review Gate Correctness Rate | **RGCR** | \|patch runs with correct WAITING_APPROVAL triple\| / \|patch runs\| | **100%** |
| Terminal State Consistency | **TSC** | \|runs where phase/outcome/gate agree per I1\| / \|all runs\| | **100%** |

## Procedure

1. Execute all 30 tasks under configuration **A**
2. For each patch run: inspect `run_meta.json`, `gate_result.json`, `loop_trace.jsonl`
3. Run `summary week`; verify Completed membership
4. `review approve` on subset; verify direct-finalize (P0-2); attempt `resume` → reject
5. Replay **B1** from documented pre-PR #8 behavior (historical, not re-enabled in CI)
6. Record FCR, RGCR, TSC per configuration

## Result template

| Config | Tasks | FCR | RGCR | TSC | Notes |
|--------|-------|-----|------|-----|-------|
| A | 30 | **0%** (expected; regression tests) | **100%** (expected) | **100%** (expected) | PR #8 + 0.4-c acceptance |
| B1 | 12 patch | **>0%** (historical) | **<100%** | **<100%** | Codex Case 1 |
| B2 | 12 patch | PENDING | PENDING | PENDING | Conceptual ablation |
| B3 | 12 patch | PENDING | PENDING | PENDING | Conceptual ablation |

**Status:** Acceptance fixtures cover subset; full 30-task bench run **PENDING**.

## Expected findings (Finding 1)

- Patch runs never appear Completed before approve (F1 fix)
- `loop_trace.jsonl` reflects post-gate outcome (I5, P2-3)
- Ablation B1 reproduces false completion documented in `logs/codex-review-cases.md`

## Links

- `tables/evaluation-metrics.md` — metric definitions
- `tables/baselines-ablations.md` — B1–B3, Abl C–E
- `tables/failure-injection-results.md` — Table A (gate-related faults)
- `experiments/acceptance-runs.md`
- `logs/codex-review-cases.md` — Cases 1, 5, 7
