# PR #8 Fault-Injection Map

**Role:** Convert Codex PR #8 review findings into a semantic runtime CI plan.

| ID | Injected fault | Terminal lie type | Oracle / guard | Expected block |
|----|----------------|-------------------|----------------|----------------|
| FI-1 | Force patch run to finalize `TERMINATED/SUCCEEDED` while `gate_result.json=needs_review` | False completion | 0.4-c patch review tests; aggregate `verify_0_4_acceptance.py` | Run held at `WAITING_APPROVAL/PARTIAL`; summary excludes Completed |
| FI-2 | Let loop write `artifact-manifest.json` before all files exist | Evidence drift | terminal artifact unit tests; manifest finalizer checks | Finalizer recomputes disk state and seals only after required artifacts exist |
| FI-3 | Include `artifact-manifest.json` inside its own manifest | Evidence drift | manifest self-exclusion assertion | Manifest excludes itself |
| FI-4 | Promote `diff-summary.md` as canonical report | Report misdirection | report path priority test | Summary picks canonical loop report or manifest report entry |
| FI-5 | Write `review_suggestion.json` after finalization | Evidence drift | checksum inclusion test | Suggestion is written before finalizer and appears in manifest |
| FI-6 | Append terminal trace before review gating downgrades outcome | Trace dishonesty | loop trace truthfulness assertion | Trace records post-gate `PARTIAL/WAITING_APPROVAL` |
| FI-7 | Reset `deferred` review item to `pending` during sync | Human decision erasure | review sync/defer preservation test | `deferred_until` survives sync; terminal decisions remain terminal |
| FI-8 | Treat approved patch run as `resume_requested` instead of direct terminalization | Recovery misclassification | approve/resume behavior test | Approve directly admits terminal success; resume rejects finalized run |
| FI-9 | Allow schedule install or unattended daily in prep stage | Boundary violation | `verify_0_5_prep.py`; SafetyGate tests | Prep stage denies install/unattended paths |

## Paper phrasing

This table should be cited as **failure-driven design evidence** until the unified fault-injection bench is implemented. Rows FI-1 to FI-9 are not broad benchmark results; they are concrete, reproducible invariants derived from review findings and acceptance tests.

## Next engineering step

Implement `scripts/run_failure_injection_bench.py` so each row becomes an executable scenario with:

```text
fault_id, fixture, injected_mutation, oracle_command, expected_status, observed_status
```
