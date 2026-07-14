# Failure Injection Matrix

## Goal

Systematically inject operational failures and verify terminal artifact contract + governance responses (Phase 2 stabilization). Results feed **ArtifactTruthBench** (RQ2), **RecoveryFaultBench** (RQ3), and **SafetyBoundaryBench** (RQ4).

## Benchmark linkage

| Bench | RQ | Fault subset |
|-------|-----|--------------|
| ArtifactTruthBench | RQ2 | F1–F12 artifact faults |
| RecoveryFaultBench | RQ3 | R1–R8 interrupt/defer |
| SafetyBoundaryBench | RQ4 | S1–S15 boundary denies |
| InternLoop-GateBench | RQ1 | Gate bypass (B1) |

Consolidated results: `tables/failure-injection-results.md` (Table A).

## Injected failure classes

| Class | Injection method | Expected terminal outcome | Required artifacts | Bench |
|-------|------------------|---------------------------|-------------------|-------|
| Missing fixture | Invalid `--fixture` | `INVALID_INPUT` or `FAILED` | run_meta + gate + manifest | RQ2 F12 |
| Missing workspace | Bad path | `FAILED` / `BLOCKED` | full contract | RQ3 |
| Command not found | Broken tool config | `FAILED` | tool-results explains | RQ4 |
| pytest failure | Failing test fixture | `PARTIAL` or `FAILED` | report + trace | RQ1 |
| pytest timeout | Timeout budget | `EXHAUSTED` / `FAILED` | gate + manifest | RQ3 |
| git failure | Dirty repo policy | `BLOCKED` | policy trace | RQ4 |
| ToolBroker reject | Disallowed write | `BLOCKED` | tool-results audit | RQ4 S3 |
| Adapter block | Real adapter without flag | `BLOCKED` | adapter-call-trace | RQ4 S2 |
| Malformed source | DailyNews bad profile | `FAILED` | honest report | RQ5 |
| Lock conflict | Parallel run same workspace | `BLOCKED` | run_meta | RQ3 R2 |
| SQLite write error | Simulated DB fault | `FAILED` | no silent loss of run ID | RQ3 R4 |
| Interrupt | SIGINT mid-ACTING | `INTERRUPTED` → recovery-scan | partial artifacts OK | RQ3 R1 |
| Early manifest | Loop writes manifest mid-run | Detected by MIR/CFR | RQ2 F1 |
| Deferred sync reset | sync after defer | HDPR failure if bug | RQ3 R7 |

## Verification checklist per run

1. Run directory created before risky work
2. All required files from Table 2 present (or documented partial path)
3. Manifest sha256 matches disk (MIR)
4. No unhandled traceback for expected operational failure
5. CLI exit code non-zero where appropriate
6. Record pass/fail in Table A

## Status

- **Partial:** Individual tests exist across pytest suite
- **Unified matrix report:** PENDING — `tables/failure-injection-results.md`
- Link results to RQ2, RQ3, RQ4 when consolidated

## Commands

```bash
pytest -q tests/integration/
pytest -q tests/unit/test_terminal_artifacts.py
pytest -q tests/unit/test_review_service_patch_gate.py
# TODO: scripts/run_failure_injection_bench.py
```

## Paper reference

Failure injection validates **ERRR** (RQ3) and **CFR** (RQ2). Codex PR #8 cases are failure-driven design evidence, not bench runs.
