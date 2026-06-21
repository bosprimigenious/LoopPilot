# Patch review: TERMINATED + needs_review state model

**Date:** 2026-06-21  
**Branch:** `feat/0.5-safe-autonomy`

## Change

Patch-producing runs (`patch.diff` present) now finalize as **TERMINATED / PARTIAL / needs_review** before human approve — not `WAITING_APPROVAL`. Approve direct-finalizes to **TERMINATED / SUCCEEDED / pass** without `resume_requested`. Reject/cancel set `gate=blocked`; resume blocked for patch runs awaiting review.

## Rationale

Codex PR #8 P1: summary and gate artifacts must not show patch runs as completed until approved; resume must not be a substitute for approve/reject/cancel.
