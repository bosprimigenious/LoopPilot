# Acceptance Snapshot — 2026-07-16

This snapshot pins executable evidence for the LoopPilot paper and open artifact
gate. It records terminal-truthfulness oracles only; it does not claim task-level
SOTA, production safety, or live-adapter reliability.

## Commit Under Test

- Commit: `03d9dae814623a5005d97d784069867caf80480d`
- Commit time: `2026-07-16T05:18:12+08:00`
- Subject: `Add paper threats to validity section`
- Branch at run time: `main`

The documentation commit that records this file is intentionally later than the
commit under test.

## Environment

- Host workspace: macOS local checkout
- Python: `Python 3.14.6` from `.venv/bin/python`
- Dependency mode: existing editable development environment
- Private credentials required: no
- Live adapters required: no

## Commands and Results

| Command | Result |
|---------|--------|
| `.venv/bin/ruff check .` | PASS, `All checks passed!` |
| `.venv/bin/python scripts/verify_0_4_acceptance.py` | PASS, `Truthful 0.4 aggregate acceptance (READY): 11/11 passed`; includes `258 passed in 5.69s` full pytest suite |
| `.venv/bin/python scripts/verify_0_5_prep.py` | PASS, `0.5-prep: PASS (3/3 checks)`; `0.5-ready: NOT READY` as expected |
| `.venv/bin/python scripts/verify_open_artifact_readiness.py` | PASS, `5/5 checks` |
| `.venv/bin/python scripts/build_artifact_review_bundle.py` | PASS, archive `dist/artifact-review/looppilot-artifact-review-03d9dae81462.tar.gz`, sha256 `057872cbffe85f9d38ab2f81645e3c2e374f744277beaa260e23c3a67c60a052`, `544` tracked files, `8` commands |
| `.venv/bin/python scripts/run_failure_injection_bench.py --execute-oracles` | PASS, FI-1..FI-9 oracle execution |
| `.venv/bin/python scripts/verify_wsl_deploy_static.py` | PASS, `5/5 checks` |
| `.venv/bin/python scripts/verify_api_bridge_contract.py` | PASS, `6/6 checks` |
| `.venv/bin/python scripts/verify_wechat_miniprogram_static.py` | PASS, `11/11 checks` |

## Paper Scope

This snapshot supports the paper's version-pinned claims about terminal
truthfulness: false completion blocking, manifest integrity, review-state
preservation, safety-boundary blocking, summary/API/mobile visibility, and
artifact-review reproducibility. It should not be cited as evidence for task
quality, real-adapter reliability, or full semantic runtime CI benchmark
coverage.
