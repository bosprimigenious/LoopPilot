# Evaluation Metrics

Metrics prioritize **governance correctness** over task success rate. Formulas use |S| for set cardinality.

## Main text (five primary metrics)

Spell out in paper body; abbreviations allowed after first use:

| Metric | Symbol | RQ |
|--------|--------|-----|
| False Completion Rate | **FCR** | RQ1 |
| Manifest Integrity Rate | **MIR** | RQ2 |
| Human Decision Preservation Rate | **HDPR** | RQ3 |
| Unsafe Mutation Block Rate | **UMBR** | RQ4 |
| Daily Actionability Rate | **DAR** | RQ7 |

### Primary formulas

```
FCR = |{r : patch(r) ∧ completed(r) ∧ gate(r)=needs_review}| / |patch_runs|
MIR = |{r : ∀e ∈ manifest(r): sha256_disk(e) = sha256_recorded(e)}| / |runs|
HDPR = |{d : defer(d) ∧ sync(d) ∧ status_unchanged(d)}| / |defer_test_cases|
UMBR = |{v : violation_attempted(v) ∧ blocked(v)}| / |violation_attempts|
DAR = |{day : FRI(day) = 0}| / |trial_days|
```

## Appendix metrics (protocol definitions only)

Moved to LaTeX Appendix `app:metrics` and listed here for markdown sync.

### RQ1 secondary
- **RGCR** — Review-gate correctness rate
- **TSC** — Terminal state consistency

### RQ2 secondary
- **CFR** — Checksum failure rate
- **RSA** — Required-artifact set adherence
- **ACR** — Artifact contract recall

### RQ3 secondary
- **RCA** — Recovery case acknowledgment
- **URBR** — Unsafe auto-resume block rate
- **ERRR** — Error recovery route rate

### RQ4 secondary
- **BVR** — Boundary violation rate
- **CER** — Compliance evidence rate

### RQ5 secondary
- **CLCC** — Cross-loop contract coverage
- **LSPA** — Loop-specific path adherence
- **GRR** — Governance rule reuse

### RQ6 secondary
- **GAL** — Gate application latency
- **MFW** — Manifest finalization wall time
- **RQST** — Review queue sync time
- **SAT** — Summary aggregation time

### RQ7 secondary
- **HAR** — Human approval rate
- **RB** — Review burden (minutes/day)
- **FRI** — False report incidents
- **USR** — User self-reported trust (Likert)

## Aggregate acceptance (measured)

`verify_0_4_acceptance.py` sub-gates READY; measured 2026-06-22: **11/11 READY** (`pytest -q`: 227 passed).

**Caption:** Main-text metrics are governance-focused; appendix abbreviations support benchmark protocols only—not claimed as measured results until benches run.
