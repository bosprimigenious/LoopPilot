# P2 manifest DB sync + schema_version

Date: 2026-06-22  
Branch: `stabilize/0.4-truthful-acceptance`

## P2-1 — approve refreshes SQLite artifact_manifests

**Problem:** `ReviewService.approve()` called `finalize_terminal_artifacts(gate=pass)` on disk but left the SQLite `artifact_manifests` row at the pre-approve `needs_review` / `partial` payload.

**Fix:** Capture the dict returned by `finalize_terminal_artifacts()` and call `state_store.save_artifact_manifest(run_id, manifest)` before `save_run()`.

**Test:** `test_approve_refreshes_persisted_artifact_manifest`

## P2-2 — canonical manifest schema

**Problem:** Writer omitted `schema_version`; strict JSON Schema rejected `loop_type` under `additionalProperties=false`.

**Fix:** Writer emits `"schema_version": "1"`; schema requires `schema_version`, `run_id`, `loop_type`, `terminal_outcome`, `artifacts` with `additionalProperties=false` on root and artifact items.

**Tests:** `test_generated_artifact_manifest_validates_against_schema`, `test_approved_manifest_validates_against_schema`

## Self-check (2026-06-22)

| Check | Result |
|-------|--------|
| approve 后 DB manifest == 磁盘 manifest | PASS — `test_approve_refreshes_persisted_artifact_manifest` |
| 生成 manifest 通过 `validate_artifact_manifest()` | PASS — `test_generated_artifact_manifest_validates_against_schema` |
| approve 后 manifest 通过 schema | PASS — `test_approved_manifest_validates_against_schema` |
| patch 审阅门语义 WAITING_APPROVAL | PASS — `test_patch_run_phase_is_waiting_approval_before_approve` |
| verify_0_4 11/11 READY | PASS — `verify_0_4_acceptance.py` 2026-06-22 |
