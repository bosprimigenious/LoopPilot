# LoopPilot Governance

LoopPilot governance mirrors the runtime thesis: trusted outcomes require explicit admission. Project decisions should leave an auditable trail and should not weaken safety gates for convenience.

## Maintainer Authority

The current maintainer is Hengji Zhang (`bosprimigenious`). Maintainers may:

- merge reviewed changes;
- cut releases;
- update safety policy;
- accept or reject artifact claims for the paper;
- decide when public artifact review is ready.

## Release Gate

A release or paper artifact snapshot should include:

- a pinned commit;
- a clean working tree;
- `ruff check .`;
- `pytest -q`;
- `python scripts/verify_0_4_acceptance.py`;
- `python scripts/verify_0_5_prep.py`;
- WSL/static/API/mobile validation where relevant;
- a short note of warnings that remain.

## Safety Policy Changes

Any change to `SafetyGate`, review gates, ToolBroker policy, scheduler install paths, or unattended execution must:

- include a regression test or static guard;
- document the before/after boundary;
- preserve fail-closed behavior by default;
- avoid hidden credential or network requirements;
- be reviewed as a safety-sensitive change.

## Artifact Claim Admission

Paper claims about measured results are admitted only when the repository records:

- command;
- commit;
- environment;
- result;
- relevant generated artifact path or log.

README badges and historical notes are not enough for new paper claims.

## Contributor Path

Before inviting external contributors, the project should maintain:

- `CONTRIBUTING.md`;
- `CODE_OF_CONDUCT.md`;
- `SECURITY.md`;
- license clarity;
- clean-checkout setup and validation commands.
