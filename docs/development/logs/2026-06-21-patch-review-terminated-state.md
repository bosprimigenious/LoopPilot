# Patch review: TERMINATED + needs_review state model

> **Correction (2026-06-22):** Superseded by Codex P2-1. Patch runs before approve now use **`WAITING_APPROVAL` / `PARTIAL` / `needs_review`**, not `TERMINATED`. See [50-0.4-stabilization-and-truthful-acceptance.md](../50-0.4-stabilization-and-truthful-acceptance.md) Phase 0.6.

**Date:** 2026-06-21  
**Branch:** `feat/0.5-safe-autonomy`

## Change (historical)

Patch-producing runs (`patch.diff` present) initially finalized as **TERMINATED / PARTIAL / needs_review** before human approve. Approve direct-finalizes to **TERMINATED / SUCCEEDED / pass** without `resume_requested`. Reject/cancel set `gate=blocked`; resume blocked for patch runs awaiting review.

## Rationale

Codex PR #8 P1: summary and gate artifacts must not show patch runs as completed until approved; resume must not be a substitute for approve/reject/cancel.
