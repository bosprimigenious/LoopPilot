# RQ2: Artifact Contract Integrity — ArtifactTruthBench

## Research question

Does the sole-writer manifest finalizer produce checksum-accurate, complete artifact bundles for every terminal run?

## Benchmark: ArtifactTruthBench

**Purpose:** Systematic fault injection against the Sealed Artifact Contract (SAC).

| Parameter | Specification |
|-----------|---------------|
| Fault classes | **F1–F12** (see matrix below) |
| Loop coverage | InternLoop, PaperLoop, DailyNewsLoop (4 faults each minimum) |
| Detection | Independent sha256 recompute script + manifest schema validation |
| Runs | 12 injected faults + 12 clean terminal runs = **24** minimum |

### Fault classes F1–F12

| ID | Fault | Injection | Expected detection |
|----|-------|-----------|-------------------|
| F1 | Early manifest write | Loop writes manifest mid-run | Finalizer overwrites; B1 historical |
| F2 | Post-seal append | Write file after manifest | Integrity script fails (M2) |
| F3 | Self-listing manifest | Manifest lists itself | Validator rejects (M1) |
| F4 | Missing required file | Skip `gate_result.json` | Finalizer blocks seal (M4) |
| F5 | Stale checksum | Edit file after hash recorded | Recompute mismatch |
| F6 | Wrong report path | Summary picks `diff-summary.md` | Report router fails (F3) |
| F7 | Missing review_suggestion | Finalize before suggestion | Ordering violation (P2-2) |
| F8 | Duplicate manifest writer | InternLoop legacy write | Sole-writer test (I3) |
| F9 | Empty tool-results silent | Block before Act without explanation | Audit gap flagged |
| F10 | Metadata loss | Drop `human_readable` on rescan | M5 preservation check |
| F11 | Atomic write race | Simulate partial manifest | `.tmp` + replace prevents |
| F12 | Cross-loop report name | Wrong loop-specific report | LSPA sub-metric (RQ5) |

## Baselines

| ID | Configuration | Expected MIR |
|----|---------------|--------------|
| **A** | Full SAC + SAO | 100% |
| **C** | Inline manifest, no rescan | <100% on F1/F5 |
| **B1** | (from RQ1) N/A | — |

## Metrics (proprietary)

| Metric | Symbol | Formula | Target (A) |
|--------|--------|---------|------------|
| Manifest Integrity Rate | **MIR** | \|runs with ∀e: sha256_disk(e) = manifest(e)\| / \|runs\| | **100%** |
| Checksum Failure Rate | **CFR** | \|fault injections detected before user trust\| / \|injected faults\| | **100%** |
| Required-artifact Set Adherence | **RSA** | \|runs with complete Table 2 set\| / \|terminal runs\| | **100%** |
| Artifact Contract Recall | **ACR** | \|manifest entries matching on-disk files\| / \|on-disk files (excl. manifest)\| | **100%** |

## Procedure

1. Run each loop to clean terminal path under **A**; verify MIR, RSA, ACR
2. Inject F1–F12 per fault matrix; verify CFR catches each class
3. Ablation **C**: replay inline manifest behavior (documented pre-P1)
4. Report path sub-test: priority list for all three loops

## Result template

| Loop | Clean runs | MIR | CFR (12 faults) | RSA | ACR |
|------|------------|-----|-----------------|-----|-----|
| InternLoop | PENDING | **100%** (expected) | PENDING | **100%** (expected) | PENDING |
| PaperLoop | PENDING | **100%** (expected) | PENDING | **100%** (expected) | PENDING |
| DailyNewsLoop | PENDING | **100%** (expected) | PENDING | **100%** (expected) | PENDING |

## Expected findings (Finding 2)

- Sole-writer `finalize_terminal_artifacts()` eliminates F1/F8 (Codex Case 2)
- `review_suggestion.json` ordering fix addresses F7 (Case 4)
- Report priority fixes F6 (Case 3)

## Links

- `tables/evaluation-metrics.md`
- `tables/failure-injection-results.md` — Table A
- `figures/artifact-contract.md`, `tables/artifact-contract.md`
- `experiments/failure-injection.md`
