# Schema scaffold

JSON Schemas belong here. `docs/development/17-data-contracts.md` is the source specification. Per-run artifact layout: [47-output-interface-spec.md](../docs/development/47-output-interface-spec.md).

| Schema | Purpose |
|--------|---------|
| `artifact-manifest.json` | Run artifact index |
| `run-record.json` | RunRecord object |
| `agent-output.json` | AgentOutput object |
| `gate_result.schema.json` | Evaluator gate verdict (`pass` / `needs_review` / `blocked`) |

Every schema must have valid, invalid, migration, and round-trip tests.
