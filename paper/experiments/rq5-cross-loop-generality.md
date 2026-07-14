# RQ5: Cross-Loop Generality — Shared Governance Across Loops

## Research question

Do InternLoop, PaperLoop, and DailyNewsLoop share the same governance primitives (SAC, RGT, TT) without loop-specific escape hatches?

> **Note:** Former `rq5-daily-use.md` addressed daily burden; that content moved to **RQ7**. This RQ replaces cross-cutting generality formerly implicit in acceptance tests.

## Benchmark: Cross-Loop Governance Suite

| Parameter | Specification |
|-----------|---------------|
| Loops | InternLoop, PaperLoop, DailyNewsLoop |
| Runs per loop | 10 terminal paths (success, partial, blocked, failed) |
| Shared checks | M1–M5, I1–I5, report priority, manifest sole-writer |
| Total runs | **30** minimum |

### Per-loop governance checklist

| Check | InternLoop | PaperLoop | DailyNewsLoop |
|-------|------------|-----------|---------------|
| SAC terminal bundle | ✓ | ✓ | ✓ |
| Canonical report name | `development-report.md` | `paper-development-report.md` | `daily-news-report.md` |
| Review gate when mutating | patch.diff | proposed-revision | N/A (triage only) |
| No direct cross-loop mutation | — | read-only policy | inbox import boundary |
| `finalize_terminal_artifacts()` only | ✓ | ✓ | ✓ |

## Metrics (proprietary)

| Metric | Symbol | Formula | Target |
|--------|--------|---------|--------|
| Cross-Loop Contract Coverage | **CLCC** | \|loops passing all SAC checks\| / 3 | **100%** |
| Loop-Specific Path Adherence | **LSPA** | \|runs with correct canonical report\| / \|runs\| | **100%** |
| Governance Rule Reuse | **GRR** | \|shared invariant checks reused without fork\| / \|total checks\| | **100%** |

## Procedure

1. Execute 10 terminal paths per loop under configuration **A**
2. Verify CLCC: all three loops pass M1–M5 on clean runs
3. Verify LSPA: summary links correct report per loop
4. Verify GRR: same `terminal_artifacts.py` finalizer, same state machine enums
5. DailyNewsLoop: confirm no code mutation; `candidate-actions.json` → explicit import

## Result template — Table B

See `tables/cross-loop-coverage.md`.

| Loop | Runs | CLCC | LSPA | GRR | Notes |
|------|------|------|------|-----|-------|
| InternLoop | PENDING | **PASS** (expected) | **PASS** (expected) | **PASS** | PR #8 primary |
| PaperLoop | PENDING | **PASS** (expected) | PENDING | **PASS** | Mock fixtures |
| DailyNewsLoop | PENDING | **PASS** (expected) | PENDING | **PASS** | var/artifacts samples exist |

## Expected findings

- Governance is loop-agnostic; differences are Select/Plan/Act only (Innovation 1)
- DailyNewsLoop signal-to-action boundary preserved (no silent inbox writes)
- No loop writes legacy manifest (I3)

## Links

- `tables/cross-loop-coverage.md` — Table B
- `experiments/rq5-daily-use.md` — **deprecated index**; see RQ7
- `experiments/acceptance-runs.md`
