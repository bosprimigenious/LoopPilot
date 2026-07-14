# Table B: Cross-Loop Governance Coverage

**Caption:** Cross-loop generality (RQ5). Target: CLCC = 100%, LSPA = 100%, GRR = 100%.

| Loop | Terminal paths | SAC (M1–M5) | Canonical report | Review gate | Cross-mutation blocked | CLCC | LSPA | GRR |
|------|----------------|---------------|------------------|-------------|------------------------|------|------|-----|
| **InternLoop** | PENDING (target 10) | **PASS** (expected) | `development-report.md` | patch.diff → RGT | N/A | **PASS** | **PASS** (expected) | **PASS** |
| **PaperLoop** | PENDING (target 10) | **PASS** (expected) | `paper-development-report.md` | proposed-revision | read-only policy | **PASS** (expected) | PENDING | **PASS** |
| **DailyNewsLoop** | PENDING (target 10) | **PASS** (expected) | `daily-news-report.md` | triage only | inbox import boundary | **PASS** (expected) | PENDING | **PASS** |
| **Shared finalizer** | — | `finalize_terminal_artifacts()` | report priority router | I1–I5 | G6 composability | — | — | **100%** reuse |

## Notes

- `var/artifacts/daily-news/` contains sample runs (2026-06-22) for manual MIR spot-check
- Milestone B controlled-real runs **NOT READY** — MockAdapter dominates
- Full 30-run cross-loop suite execution: **PENDING**
