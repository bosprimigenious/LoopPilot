# Contributing to LoopPilot

LoopPilot is a controlled runtime for long-running personal AI agents. Contributions are welcome when they preserve the project's core safety rule: completion must be admitted by runtime evidence, not emitted by a model or task loop.

## Local Setup

```bash
python -m pip install -e ".[dev]"
python scripts/bootstrap_local.py
loop-pilot doctor
```

On WSL/Linux, the recommended path is:

```bash
bash scripts/deploy_wsl.sh --repo-dir "$HOME/LoopPilot"
```

## Validation Before a Pull Request

Run the smallest relevant tests while developing, then run the full local gate before asking for review:

```bash
ruff check .
python scripts/verify_wsl_deploy_static.py
python scripts/verify_api_bridge_contract.py
python scripts/verify_wechat_miniprogram_static.py
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
pytest -q
```

For WeChat mini program changes, also run JS syntax checks for touched files:

```bash
node --check clients/wechat-miniprogram/pages/runs/runs.js
```

## Safety Boundaries

- Do not bypass `SafetyGate`, `ReviewService`, ToolBroker policy, or review gates.
- Do not add auto-approve, auto-commit, auto-push, or deployment side effects.
- Do not require private credentials for tests or artifact review.
- Keep real adapters fail-closed unless an explicit gate allows them.
- Keep mutating artifacts behind human review until approval is recorded.

## Paper and Artifact Contributions

The paper treats the repository as an artifact. Changes that improve reproducibility, fault injection, acceptance oracles, WSL setup, API bridge visibility, or governance documentation are research contributions as well as engineering contributions.

When updating paper claims, pin the commit, command, environment, and result. Do not update measured claims from README badges alone.

## Pull Request Expectations

- Explain the terminal-trust invariant affected by the change.
- Include the validation commands you ran.
- Mention any remaining warnings or unverified paths.
- Keep unrelated refactors separate.
- Preserve user data, local artifacts, and gitignored private workspaces.
