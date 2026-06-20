# Source package scaffold

This directory intentionally contains no Python implementation yet.

Cursor should create the package according to:

- `docs/development/01-architecture.md`
- `docs/development/14-implementation-manifest.md`
- `docs/development/17-data-contracts.md`
- `docs/development/18-state-transition-spec.md`
- `docs/development/28-agent-development-guide.md`
- `docs/development/29-model-routing-and-runtime-policy.md`

Planned subpackages:

```text
loop_pilot/
├── domain/
├── runtime/
├── policy/
├── loops/
│   ├── intern/
│   ├── paper/
│   └── daily_news/
├── agents/
├── skills/
├── tools/
├── connectors/
├── adapters/
├── models/
├── storage/
├── reporting/
└── cli.py
```
