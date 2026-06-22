# Cursor Prompt — Stabilize 0.4 Truthful Acceptance

Work on branch `stabilize/0.4-truthful-acceptance`.

Use Cursor Agent mode. Inspect and edit the repository directly; do not stop after proposing a plan. Continue through implementation, regression tests, and acceptance verification until all in-scope Milestone A gates pass or a concrete blocker remains that cannot be resolved from the repository.

Read first:

1. `docs/development/50-0.4-stabilization-and-truthful-acceptance.md`
2. `docs/development/logs/2026-06-21-truthful-0.4-acceptance.md`
3. `docs/development/10-testing-and-acceptance.md`
4. `docs/development/18-state-transition-spec.md`
5. `docs/development/23-human-review-protocol.md`
6. `docs/development/38-toolbroker-design.md`
7. `docs/development/45-personal-daily-loop-0.4c-acceptance.md`
8. `docs/development/48-personal-daily-loop-0.4d-acceptance.md`

Objective: make 0.4 acceptance truthful and reliable. Do not implement 0.5 features and do not claim full 0.4 READY until the aggregate gate passes.

Before editing:

- confirm `git branch --show-current` is exactly `stabilize/0.4-truthful-acceptance`;
- inspect `git status --short` and preserve every existing user change;
- run the current baseline and record exact exit codes;
- treat the existing truthful-acceptance changes as work to extend, not discard or rewrite.

Execute in small reviewable commits:

1. Correct status language and acceptance anti-cheat behavior.
2. Fix the confirmed review regressions: missing 0.4-c CLI registration, mutating migration dry-run, and missing Intern/Paper report links in daily summaries.
3. Make Ruff, full pytest and 0.3 acceptance green; replace bare pytest with the active interpreter and update ToolBroker policy safely.
4. Guarantee the canonical audit artifact set on every terminal path.
5. Add migration v4 and the historical-schema migration matrix; never rewrite applied v3.
6. Restore recovery tests to default pytest and fix exact-round/idempotent resume.
7. Implement the minimum 0.4-c review/decision layer and non-bypass tests.
8. Add `scripts/verify_0_4_acceptance.py` as the only full-0.4 READY authority.
9. Add controlled-real Ideas tests only after truthful 0.4 acceptance is green.

Specific regression requirements:

- `loop-pilot review list`, `approve`, `reject`, `defer`, `cancel`, and `resume` must be registered and persist decisions; do not register fake placeholders.
- `loop-pilot db migrate --dry-run` must not create or modify the target database, schema metadata, WAL/journal files, or timestamps.
- `summary today` must resolve Intern `development-report.md`, Paper `paper-development-report.md`, and DailyNews `daily-news-report.md`, preferably through the artifact manifest rather than duplicated filename knowledge.

For every commit:

- state the invariant being restored;
- add a failing regression test first where practical;
- run the smallest relevant test, then `ruff check .`, `pytest -q`, and `python scripts/verify_0_3_acceptance.py`;
- preserve user changes and historical logs;
- do not weaken, skip, rename away, or filter a failing required test;
- do not treat file existence, mocked output, or component readiness as full acceptance.

Required final verification from the repository virtual environment:

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/ruff check .
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python scripts/verify_0_3_acceptance.py
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python scripts/verify_0_4_acceptance.py
git diff --check
```

Do not mark a required test as skipped, xfail, filtered, or removed to obtain green output. Do not weaken assertions or acceptance predicates. A command that was not run is not a pass. If `verify_0_4_acceptance.py` does not yet exist, implementing it and its anti-cheat tests is part of this task.

Stop and report `NOT READY` if any required gate remains red. Report exact commands, exit codes, failing tests, artifacts, migration path tested, and remaining blockers.
