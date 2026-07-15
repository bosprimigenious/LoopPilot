# Acceptance Runs (Milestone A — Truthful 0.4)

## Purpose

Document the aggregate acceptance gate linking implementation to paper claims. Acceptance oracles instantiate subsets of **InternLoop-GateBench** (RQ1), **ArtifactTruthBench** (RQ2), and **RecoveryFaultBench** (RQ3).

## Aggregate gate

```bash
python scripts/verify_0_4_acceptance.py
```

**Target:** 11/11 READY on branch `stabilize/0.4-truthful-acceptance` (PR #8).

## RQ mapping

| RQ | Bench | Acceptance coverage |
|----|-------|---------------------|
| RQ1 | InternLoop-GateBench | Patch review tests, 0.4-c (22 checks) |
| RQ2 | ArtifactTruthBench | `test_terminal_artifacts.py`, manifest schema |
| RQ3 | RecoveryFaultBench | 0.4-a recovery-scan, defer sync |
| RQ4 | SafetyBoundaryBench | `verify_0_5_prep.py` (partial) |
| RQ5 | Cross-loop suite | Per-loop acceptance fixtures |
| RQ6 | Overhead profile | NOT in acceptance gate |
| RQ7 | Daily trial | NOT in acceptance gate |

## Component scripts (representative)

| Script | Milestone | Status note |
|--------|-----------|-------------|
| `verify_0_3_acceptance.py` | 0.3 ToolBroker | Prerequisite |
| `verify_0_4a_acceptance.py` | SQLite + recovery | Required |
| `verify_0_4c_acceptance.py` | Review layer | 22/22 per spec |
| `verify_0_4d_acceptance.py` | Summary + schedule preview | Required for 0.5 path |
| `verify_0_4_acceptance.py` | **Aggregate** | Sole authority for "Full 0.4 READY" |
| `verify_0_5_prep.py` | SafetyGate prep | RQ4 partial |

## Milestone B (NOT conflated)

Ideas controlled-real E2E — Intern/Paper/DailyNews on real tasks — **NOT READY**; do not cite as paper results.

## Current pinned snapshot

See `acceptance-snapshot-2026-07-16.md` for the current paper-facing snapshot:
commit `03d9dae814623a5005d97d784069867caf80480d`, Python `3.14.6`,
`verify_0_4_acceptance.py` 11/11 READY, full pytest `258 passed`, PR #8
failure-oracle bench FI-1..FI-9 PASS, WSL/API/mobile static checks PASS, and
artifact bundle sha256 `057872cbffe85f9d38ab2f81645e3c2e374f744277beaa260e23c3a67c60a052`.

## Evidence to capture for paper

- [x] Local log snippet with 11/11 READY and pinned commit hash
- [ ] One sample artifact dir under `var/artifacts/` per loop type
- [ ] Link PR #8 URL in appendix
- [ ] Table A partial fills from unit/integration tests

## Paper reference

Milestone A proves **governance truthfulness**, not task SOTA. Full benchmark suites (30-task GateBench, 24-run ArtifactTruthBench) are **PENDING** execution beyond acceptance oracles.
