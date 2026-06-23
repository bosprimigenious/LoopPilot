# 2026-06-23 Main CLI Smoke Log

## Scope

This run verifies latest `main` as a connected CLI user would use it. It checks automated gates, offline demo loops, sqlite review flow, daily summary flow, and fail-closed adapter behavior.

## Git state

```text
branch: main
head: cfc8e0e
remote: origin/main
status before docs: clean
```

`main` was fast-forwarded from remote on 2026-06-23.

## Automated gates

| Check | Result |
|---|---|
| `ruff check .` | PASS |
| `pytest -q` | PASS — 254 passed |
| `python scripts/verify_0_3_acceptance.py` | PASS — 20/20 |
| `python scripts/verify_0_4_acceptance.py` | READY — 11/11 |
| `python scripts/verify_0_5_prep.py` | PASS for 0.5-prep; 0.5-ready remains NOT READY |

Important: `0.5-ready: NOT READY` is correct and should not be treated as a failure.

## JSON/default CLI smoke

Commands:

```bash
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config doctor
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config adapters list
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config adapters doctor
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config run all --profile demo --dry-run
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config status
```

Observed:

- `doctor`: OK
- default adapter posture: real adapters disabled
- `run all --profile demo --dry-run`:
  - `daily_news`: succeeded
  - `intern`: partial / waiting approval
  - `paper`: partial
- default JSON backend clearly blocks sqlite-only commands.

Concern:

- `--config-dir` does not isolate runtime paths by itself; relative `var/` paths still resolve against repository cwd.

## SQLite/review CLI smoke

Config:

```text
tests/fixtures/acceptance_0_4a/config
```

Commands:

```bash
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config doctor
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config db status
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config db migrate --dry-run
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config run intern --fixture simple_python_bug --dry-run
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config review list
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config review show <run_id>
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config report <run_id>
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config approve <run_id> --note "CLI smoke approval"
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config inspect <run_id>
```

Observed:

- sqlite doctor: OK
- db schema version: 4
- pending migrations: none
- intern fixture produced `WAITING_APPROVAL / partial`
- `review list` showed the pending review item
- `review show` returned run + review item JSON
- `report` returned the canonical report path
- `approve` finalized run as `TERMINATED / succeeded`

Concern:

- `resume <run_id>` after approval returns `cannot resume: run already finalized after approval`.
- That behavior is acceptable if approve-finalizes is the intended model, but CLI help should no longer imply approved runs are normally resumed.

## Daily/summary/schedule CLI smoke

Commands:

```bash
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config run daily --dry-run
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config summary today
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config schedule status
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config schedule print --target cron
```

Observed:

- daily dry-run completed
- summary written to `var/artifacts/daily/2026-06-23/daily-summary.md`
- schedule status reports not installed
- cron preview is dry-run only

Concern:

- `run daily` printed `recovery-scan: 1 finding(s)`, while a standalone `recovery-scan` immediately after showed `OK (no issues)`.
- The daily output needs to explain recovery findings or avoid showing transient/non-actionable counts.

## Today CLI smoke

Command:

```bash
python -m loop_pilot.cli today --help
```

Observed commands:

```text
add
add-queue
```

Missing expected user-facing commands:

- `today list`
- `today show`
- `today done`
- `today defer`

This is the biggest daily-use gap after the automated gates have gone green.

## Fail-closed adapter smoke

Command:

```bash
python -m loop_pilot.cli --config-dir tests/fixtures/acceptance_0_4a/config run intern --workspace examples/intern_demo --adapter cursor_cli --dry-run
```

Observed:

```text
completed: blocked
Reason: Role coding_agent blocked: adapter cursor_cli blocked by allow_real_adapters=false
```

Artifacts existed:

- `adapter-call-trace.jsonl`
- `artifact-manifest.json`
- `gate_result.json`
- `loop_trace.jsonl`
- `report.md`
- `review_required.md`
- `review_suggestion.json`
- `run_meta.json`
- `tool-results.json`
- `trace.jsonl`

Concern:

- `report.md` for the blocked run was too minimal:

```markdown
# Run <run_id>

Outcome: blocked
```

For real use, blocked/failed reports need reason, command, gate status, artifact links, and suggested next action.

## Final assessment

Latest `main` is credible from a regression/acceptance standpoint. It can run the offline three-loop demo, sqlite review gate, summary, schedule preview, and fail-closed adapter blocking.

It is not yet a polished daily personal CLI. The next work should focus on:

1. runtime path/profile isolation;
2. personal sqlite quickstart;
3. `today` read/update commands;
4. clear approve/resume semantics;
5. richer blocked/failure reports;
6. explainable recovery findings in daily output.

