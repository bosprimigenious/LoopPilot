# RQ7: Daily-Use Utility — Personal Trial Protocol

## Research question

In realistic multi-day personal use (5–14 days), does LoopPilot maintain zero governance incidents while keeping human review burden acceptable?

> **Supersedes** the daily-use content formerly in `rq5-daily-use.md`.

## Protocol: 5–14 Day Personal Trial

| Parameter | Specification |
|-----------|---------------|
| Duration | **5 days minimum** (workdays); **14 days** preferred for habit formation |
| Loops | ≥1 run/day across InternLoop, PaperLoop, DailyNewsLoop |
| Adapter | MockAdapter + dry-run default; optional 1 controlled-real run if Milestone B ready |
| Log | `logs/5-day-trial.md` + `experiments/daily-use-log.md` |

### Daily log fields

- Date, runs triggered (by loop), review decisions (approve/reject/defer/cancel)
- Minutes in `review list` / `review show`
- Governance incidents (false completion, stale manifest, wrong report, defer regression)
- Qualitative trust note (1–5 Likert, optional)

### Weekly checkpoints

- Day 5: interim Table C
- Day 14: final Table C + themes

## Metrics (proprietary)

| Metric | Symbol | Formula | Target |
|--------|--------|---------|--------|
| Daily Audit Reliability | **DAR** | \|days with 0 governance incidents\| / \|trial days\| | **100%** |
| Human Approval Rate | **HAR** | \|approve\| / \|review-required runs\| | Report only |
| Review Burden | **RB** | Median minutes/day in review CLI | PENDING — user threshold |
| False Report Incidents | **FRI** | Count of user-observed false success/stale manifest/wrong report | **0** |
| User Self-Reported trust | **USR** | Mean Likert trust score (1–5) | PENDING |

## Procedure

1. Follow `logs/5-day-trial.md` template
2. Record RB per day; compute median and IQR at end
3. Any FRI > 0 triggers root-cause against invariants I1–I5, M1–M5
4. Do **not** claim productivity gains—only governance utility

## Result template — Table C

See `tables/daily-use-trial.md`.

| Day | Runs | Review min | Decisions | FRI | DAR |
|-----|------|------------|-----------|-----|-----|
| 1–14 | PENDING | PENDING | PENDING | PENDING | PENDING |

**Status:** Trial **NOT STARTED**. Paper reports protocol only.

## Expected findings (Finding 5 — pending)

- Zero FRI if PR #8 semantics hold in daily habit
- RB dominated by patch review, not manifest overhead (links RQ6)
- Qualitative themes: deferral without queue flooding (DPS)

## Links

- `tables/daily-use-trial.md` — Table C
- `logs/5-day-trial.md`
- `experiments/daily-use-log.md`
- `experiments/rq5-daily-use.md` — deprecated pointer to this file
