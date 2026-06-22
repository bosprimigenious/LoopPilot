# P2 decided-review immutability + reject/cancel DB manifest sync

Date: 2026-06-22  
Branch: `stabilize/0.4-truthful-acceptance`

## P2-6 — decided review cannot be changed twice

**Problem:** `approve` only blocked `rejected`/`cancelled`; `reject`/`cancel` used `_require_item()` and allowed re-decision on already-approved items.

**Fix:** `_require_decidable_item()` — only `pending` or `deferred` accept a decision; raises `ReviewDecisionError` otherwise. Used by `approve`, `reject`, and `cancel`.

**Tests:** `test_approved_review_cannot_be_rejected_later`, `test_rejected_review_cannot_be_cancelled_later`

## P2-7 — reject/cancel sync SQLite artifact_manifests

**Problem:** `reject`/`cancel` called `finalize_terminal_artifacts(gate=blocked)` on disk but did not update `artifact_manifests` in SQLite (approve already synced).

**Fix:** Capture manifest dict and call `state_store.save_artifact_manifest(run_id, manifest)` — symmetric with approve.

**Tests:** `test_reject_persists_blocked_artifact_manifest`, `test_cancel_persists_blocked_artifact_manifest`

## Self-check (2026-06-22)

| Check | Result |
|-------|--------|
| 已决 review 不可二次 reject/cancel | (run below) |
| reject/cancel 后 DB manifest == 磁盘 manifest | (run below) |
| ruff / pytest / verify_0_4 | (run below) |
