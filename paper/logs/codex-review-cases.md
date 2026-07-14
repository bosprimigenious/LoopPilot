# Codex Review Cases — PR #8 Failure-Driven Design Evidence

**Branch:** `stabilize/0.4-truthful-acceptance`  
**PR:** #8 (ready for merge per stabilization doc; merge hash TODO)  
**Reviewer:** Codex automated review (not human peer review)  
**Paper role:** Demonstrates that governance failures are reproducible engineering bugs, fixable with explicit invariants and acceptance tests.

---

## Executive summary

Before PR #8, LoopPilot could **look successful** while still requiring human approval for InternLoop patch runs. Weekly summaries and gate artifacts disagreed with on-disk truth. Codex review treated these as **P0/P1/P2** release blockers. The resulting fixes define invariants I1–I5 and M1–M5 used throughout this paper.

This is not evidence that Codex "validates" LoopPilot scientifically—it is evidence that **without** automated governance review, personal agent runtimes ship false-success paths.

---

## Case 1: Review gate bypass (P0-1, P2-1)

### Symptom

InternLoop runs producing `patch.diff` finalized as completed (`TERMINATED` / `SUCCEEDED`) even though no human `approve` occurred. Weekly summary counted them in **Completed**.

### Engineering issue

Terminalization conflated "agent finished acting" with "run succeeded." Review was advisory (Markdown) rather than a **hard state**.

### Fix

Patch runs now finalize to:

```text
phase=WAITING_APPROVAL
outcome=PARTIAL
gate_result.json → gate=needs_review
```

Summary engine excludes these from Completed until approve.

### Invariants

- **I1** phase/outcome consistency
- **I2** gate_result authoritative

### Tests

Patch review behavior tests in 0.4-c acceptance; `verify_0_4_acceptance.py` aggregate gate.

---

## Case 2: Manifest checksum and sole writer (P1-1, P1-3)

### Symptom

`artifact-manifest.json` listed itself; checksums could drift when artifacts were written after an early manifest snapshot. InternLoop wrote its own manifest in addition to the finalizer.

### Engineering issue

Multiple writers and write-before-seal ordering violate auditability. Personal users tarball `var/artifacts/` for backup—stale hashes invalidate trust.

### Fix

- Only `finalize_terminal_artifacts()` writes manifest
- Scan run directory; recompute every sha256 from disk
- Exclude manifest from its own listing
- Atomic `.tmp` + replace

### Invariants

- **I3** sole manifest writer
- **M1–M3** listing, checksum, atomic write

---

## Case 3: Report selection (P1-2)

### Symptom

Daily summary / CLI linked `diff-summary.md` or wrong auxiliary file instead of canonical loop report.

### Engineering issue

Hard-coded filenames per loop broke when artifact contract evolved (`development-report.md`, `paper-development-report.md`, `daily-news-report.md`).

### Fix

Priority list:

```text
report.md → loop-specific report names → manifest entries with kind=="report"
```

Never promote `diff-summary.md` as primary human report.

### Failure taxonomy

**F3** in Table 3.

---

## Case 4: review_suggestion ordering (P2-2)

### Symptom

`review_suggestion.json` missing from manifest or checksum mismatch because finalize ran before suggestion was persisted.

### Fix

InternLoop path: `mark_patch_run_waiting_review()` → `write_review_suggestion()` → `finalize_terminal_artifacts()`.

### Invariant

**M4** all required artifacts on disk before seal.

---

## Case 5: Trace dishonesty (P2-3)

### Symptom

`loop_trace.jsonl` recorded terminal `succeeded` while gate still `needs_review`.

### Engineering issue

Trace appended before review gating downgraded outcome.

### Fix

Append terminal trace **after** outcome downgrade to `partial`.

### Invariant

**I5** trace reflects post-gate truth.

---

## Case 6: Deferred review sync bug (P2 deferred)

### Symptom

User runs `review defer --until <date>`; later `sync_from_runs` reset item to `pending`, resurfacing prematurely.

### Engineering issue

`ReviewStore.upsert_pending()` treated every sync as fresh pending state.

### Fix

- Preserve `deferred` until `deferred_until`
- `approved` / `rejected` / `cancelled` are terminal—sync never reopens

### Failure taxonomy

**F5**; supports RQ3 review queue fidelity.

---

## Case 7: Approve/resume confusion (P0-2)

### Symptom

Docs and behavior suggested `approve → resume_requested` for patch runs, leaving ambiguous lifecycle.

### Fix

**Direct-finalize:** approve sets terminal success without resume; `resume()` rejects already-finalized approved runs.

---

## Quantitative summary (TODO)

| Priority | Findings count | All addressed? |
|----------|----------------|----------------|
| P0 | TODO | Yes (per CHANGELOG) |
| P1 | TODO | Yes |
| P2 | TODO | Yes |

Pin exact comment/thread counts from GitHub PR #8 when merging.

---

## How to cite in paper

> "Automated Codex review on PR #8 identified seven governance failure modes (false completion, stale manifest, report misrouting, suggestion ordering, trace dishonesty, deferred sync, approve/resume ambiguity). Each maps to an invariant and regression test—illustrating failure-driven design for personal agent runtimes."

---

## Related files

- `CHANGELOG.md` Unreleased
- `docs/development/50-0.4-stabilization-and-truthful-acceptance.md`
- `docs/development/logs/2026-06-21-patch-review-terminated-state.md` (superseded banner)
- `experiments/codex-review-findings.md`
