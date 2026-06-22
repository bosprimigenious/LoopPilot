# Codex P2 — review guards & CLI alignment (2026-06-22)

Branch: `feat/0.5-safe-autonomy` @ ab7d205+

## P2-1: Preserve finalized review decisions

**Problem:** `reject()`, `defer()`, `cancel()` (and partially `approve()`) called `_require_item()` without checking whether the review item was already finalized. A stale `reject` after `approve` could rewrite the run to `BLOCKED` and corrupt terminal artifacts.

**Fix:** Added `ReviewDecisionError` and `_require_decidable_item()` — only `pending` and `deferred` items accept new decisions. `approve`, `reject`, `defer`, and `cancel` all use this guard before mutating run state or recording decisions.

**Tests:**

- `test_reject_after_approve_raises_and_preserves_state`
- `test_defer_after_approve_raises`
- `test_cancel_after_reject_raises`
- `test_approve_after_reject_raises`

## P2-2: CLI docs vs wiring

**Problem:** Acceptance docs listed `review approve`, `review reject`, etc., but only `review list` / `review show` were registered under the `review` group; decision commands lived at the CLI root.

**Approach:** **Option A** — register `approve`, `reject`, `defer`, `cancel`, `resume` as `review` subcommands in `cli_review.py`; keep root-level commands in `cli.py` for backward compatibility.

**Docs:** Updated `50-personal-daily-loop-0.4-full-acceptance.md` command matrix (aliases noted); `docs/zh/12-0.4c-审阅与决策层.md`; `verify_0_4c_acceptance.py` checks `review <subcommand> --help`.

## Self-check

```bash
ruff check .
python -m pytest -q
python scripts/verify_0_4c_acceptance.py
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
```
