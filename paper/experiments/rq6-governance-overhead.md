# RQ6: Governance Overhead — Cost of Truthful Runtime

## Research question

What is the measurable overhead of review-gated runtime governance compared to orchestration-only execution, and is it acceptable for personal daily workflows?

## Benchmark: Governance Overhead Profile

| Parameter | Specification |
|-----------|---------------|
| Configurations | **A** (full LoopPilot) vs **E** (orchestration-only conceptual) vs **A-minus-gate** (ablation: no WAITING_APPROVAL) |
| Workloads | 30 InternLoop tasks (shared with GateBench) + 10 summary/sync operations |
| Environment | Local machine; MockAdapter; cold CLI start |
| Repetitions | 3 runs per task for median wall time |

## Overhead metrics (proprietary)

| Metric | Symbol | Definition | Acceptable threshold |
|--------|--------|------------|----------------------|
| Gate Application Latency | **GAL** | Δ wall time: finalize with RGT vs without | PENDING — target <2s p50 |
| Manifest Finalization Wall | **MFW** | Time in `finalize_terminal_artifacts()` | PENDING — target <500ms p50 |
| Manifest Scan Bytes | **MSB** | Bytes hashed per finalize | Report only |
| Review Queue Sync Time | **RQST** | `sync_from_runs` duration | PENDING — target <1s |
| Summary Aggregation Time | **SAT** | `summary week` with 50 runs | PENDING |
| Governance CPU Share | **GCS** | CPU time in governance path / total run | PENDING — qualitative |
| Storage Amplification | **SA** | Artifact bytes / agent output bytes | Report only |

## Procedure

1. Instrument `finalize_terminal_artifacts()`, review gating, summary engine
2. Run GateBench 30 tasks under **A**; record GAL, MFW, MSB
3. Run 10 defer/sync cycles; record RQST
4. Compare **A** vs **E** (documented conceptual delta — no LangGraph reimplementation)
5. Report medians and IQR; no inferential stats until n≥30 repetitions

## Result template

| Metric | A (median) | E (conceptual) | Δ | Status |
|--------|------------|----------------|---|--------|
| GAL | PENDING | — | PENDING | NOT RUN |
| MFW | PENDING | — | — | NOT RUN |
| RQST | PENDING | — | — | NOT RUN |
| SAT | PENDING | — | — | NOT RUN |

## Expected findings

- Governance overhead is dominated by agent execution, not manifest sealing (hypothesis)
- SAC checksum rescan is O(n) in artifact bytes — acceptable for personal run dirs
- Honest reporting cost is **intentional**; RQ7 measures user-perceived burden

## Links

- `experiments/rq1-review-gate.md` — shared 30-task set
- `tables/evaluation-metrics.md`
- Innovation 4 (Truthful Acceptance) — overhead justified by trust
