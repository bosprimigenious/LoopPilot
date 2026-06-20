# LoopPilot

LoopPilot is currently a private, documentation-first project for building three controlled AI work loops:

- `InternLoop`: resolve one real development problem with verification.
- `PaperLoop`: advance one evidence-backed research or writing gap.
- `DailyNewsLoop`: select a small number of high-value engineering, research, political, and financial signals.

No runtime implementation is included yet. The repository currently contains architecture, implementation specifications, safety boundaries, test plans, and an empty source layout for Cursor to implement the Mini version.

## Start here

- [Development plan](DEVELOPMENT_PLAN.md)
- [Complete development documentation](docs/development/README.md)
- [Mini run path](docs/development/25-mini-run-path.md)
- [Agent development guide](docs/development/28-agent-development-guide.md)
- [Model routing policy](docs/development/29-model-routing-and-runtime-policy.md)
- [Cursor Mini implementation prompt](prompts/CURSOR_MINI_IMPLEMENTATION_PROMPT.md)

## Repository status

- Private implementation phase; no local code has been pushed by this setup step
- Version `0.0.0`
- Not published to PyPI
- No real model, crawler, company code, paper draft, experiment data, credentials, or personal workspace should be committed

## Safety

Read [SECURITY.md](SECURITY.md) before adding any Adapter, Tool, Connector, workspace, or secret.
