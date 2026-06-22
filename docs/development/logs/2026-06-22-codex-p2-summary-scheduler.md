# Codex P2 — summary decided-review suppression & scheduler `--no-dry-run`

**Date:** 2026-06-22  
**Branch:** `feat/0.5-safe-autonomy`  
**PR:** #7 @ 911884e

## P2-1: Suppress decided review items in summaries

**Problem:** `SummaryCollector._run_signals_review()` still returned true for rejected/cancelled runs (`outcome=blocked`, `gate=blocked`) even after `ReviewService.reject()` / `cancel()` recorded terminal decisions in `review_items`. Daily/weekly `needs_review` sections disagreed with `review list`.

**Fix:** `_needs_review()` now checks `ReviewStore` — if `review_items.status` is `rejected`, `cancelled`, or `approved`, the run is excluded from summary `needs_review`. Future-deferred hide logic unchanged.

**Tests:** `test_rejected_review_item_not_in_summary_needs_review`, `test_cancelled_review_item_not_in_summary_needs_review`, `test_approved_review_item_not_in_summary_needs_review`.

## P2-2: Include `--no-dry-run` in ready-stage install command

**Problem:** `install_schedule()` built `run daily --unattended --safe` without `--no-dry-run`. Daily defaults to dry-run, so an installed scheduler would only preview.

**Fix:** `ready_stage_command(config_dir)` in `profiles.py`; ready-stage install uses:

```text
loop-pilot --config-dir <dir> run daily --unattended --safe --no-dry-run
```

`DEFAULT_PROFILE.command` remains `loop-pilot run daily --dry-run` for prep/preview paths.

**Tests:** `test_installed_scheduler_command_includes_no_dry_run`, integration marker assertion updated.

## Self-check

```text
ruff check .
python -m pytest -q
python scripts/verify_0_4c_acceptance.py
python scripts/verify_0_5_prep.py
```
