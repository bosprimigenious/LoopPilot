# Cursor Prompt — Implement LoopPilot Mini

Copy everything below into Cursor Agent after opening the LoopPilot repository.

---

You are implementing the **Mini version of LoopPilot** in this repository.

## 1. Non-negotiable scope

Implement Mini only. Do not implement V1/V2/V3, real production integrations, PyPI publishing, GitHub Actions, Web UI, vector memory, multi-user support, real scheduling, real company repositories, real unpublished papers, or live political/financial crawling.

Do not commit, push, publish, deploy, install a scheduler, or modify any remote system.

Do not treat `ideas.md` as an implementation specification. It is historical material only.

## 2. Read before coding

Read these documents completely, in this order:

1. `docs/development/README.md`
2. `docs/development/00-system-definition.md`
3. `docs/development/01-architecture.md`
4. `docs/development/02-runtime-mechanism.md`
5. `docs/development/09-versions.md`
6. `docs/development/10-testing-and-acceptance.md`
7. `docs/development/14-implementation-manifest.md`
8. `docs/development/17-data-contracts.md`
9. `docs/development/18-state-transition-spec.md`
10. `docs/development/19-adapter-specifications.md`
11. `docs/development/21-test-fixtures-and-golden-cases.md`
12. `docs/development/22-error-and-budget-policy.md`
13. `docs/development/24-configuration-spec.md`
14. `docs/development/25-mini-run-path.md`
15. `docs/development/28-agent-development-guide.md`
16. `docs/development/29-model-routing-and-runtime-policy.md`

Then read the three Loop specifications:

- `docs/development/03-intern-loop.md`
- `docs/development/04-paper-loop.md`
- `docs/development/05-daily-news-loop.md`

If documents appear to conflict, apply the authority rules in `docs/development/README.md`. Before coding, list every discovered conflict and propose the smallest resolution. Do not silently invent behavior.

## 3. First response before edits

Before modifying files, respond with:

1. your understanding of Mini;
2. the exact files you plan to create or modify;
3. the state and outcome model you will implement;
4. the tests and fixtures that will prove each Loop;
5. any documentation conflict or blocking ambiguity;
6. commands you intend to run.

Wait for approval if your plan includes anything outside the Mini scope, network access, destructive commands, dependency upgrades, or changes to the architecture documents.

## 4. Architecture constraints

- Python package name: `loop_pilot`.
- CLI command: `loop-pilot`.
- Use `src/` layout.
- Orchestrator and ModelRouter are deterministic components, not Agents.
- `RunPhase` and `RunOutcome` are separate types.
- Agents live only in L4 Capability.
- Agents cannot call other Agents directly.
- Agents cannot choose concrete models or instantiate Adapters.
- Agents cannot retry themselves.
- Worker output cannot directly become PASS.
- Policy Gate is mandatory before every write action.
- User-facing results are Markdown; machine state and contracts are structured.
- No private path, secret, real paper, company code, or live personal data may enter fixtures.

## 5. Mini implementation target

Implement only enough production-quality structure to run deterministic offline Mini scenarios:

### Shared Runtime

- validated configuration;
- domain models and JSON Schemas;
- legal state-transition engine;
- `RunPhase` + `RunOutcome`;
- time, round, and model-call budget objects;
- local locks suitable for tests;
- Artifact Manifest and JSONL trace;
- deterministic Markdown report renderer;
- cancellation and timeout boundaries;
- Policy decisions;
- MockAdapter;
- explicit error taxonomy;
- CLI commands required by Mini.

Mini may use a simple local state store behind an interface. Do not implement the full V1 SQLite recovery system unless the approved plan explicitly requires it. The interface must allow SQLite to replace it later without changing Loop logic.

### InternLoop Mini

- use a tiny synthetic Git fixture;
- detect one predefined failing test;
- operate in an isolated temporary workspace/worktree;
- apply a controlled fixture patch through the Mini Worker path;
- run real `pytest` on the fixture;
- evaluate the result independently;
- generate trace, Artifact Manifest, diff summary, test report, and `development-report.md`;
- demonstrate one retryable failure scenario;
- never commit or push.

Do not build a general autonomous coding Agent yet. Use MockAdapter and deterministic fixture behavior to prove the orchestration contract.

### PaperLoop Mini

- use a synthetic Markdown paper fixture;
- contain one unsupported claim and a small trusted citation fixture;
- extract the claim;
- map it to evidence;
- either revise/qualify it using fixture evidence or stop with `SOURCE REQUIRED`;
- run structure, claim-evidence, and consistency checks required by Mini;
- never fabricate citation metadata or experiment values;
- generate `paper-development-report.md` and evidence artifacts.

Do not call live scholarly APIs in Mini.

### DailyNewsLoop Mini

- use two fixed offline snapshot days;
- normalize SourceItems;
- deduplicate repeated events;
- distinguish published time from event time;
- compute GitHub star delta only when both snapshots exist;
- filter a low-confidence signal;
- enforce category and total item limits;
- generate `daily-news-report.md` and proposed Inbox candidates.

Do not access live GitHub, RSS, political news, finance news, or social media in Mini.

### `run all`

Run in fixed order:

```text
DailyNewsLoop → InternLoop → PaperLoop
```

A failure in one Loop must be reported and must not corrupt the others. Generate one daily summary Markdown report.

## 6. Required CLI behavior

Implement the smallest Mini command surface consistent with the docs:

```bash
loop-pilot doctor
loop-pilot run intern --fixture simple_python_bug --dry-run
loop-pilot run paper --fixture unsupported_claim --dry-run
loop-pilot run daily-news --fixture github_star_snapshots --dry-run
loop-pilot run all --fixture-set mini --dry-run
loop-pilot status
loop-pilot inspect <run-id>
```

If `resume`, `approve`, `reject`, or `cancel` cannot be implemented correctly in Mini, expose no fake behavior. Document them as later work rather than returning misleading success.

## 7. Required repository work

- Update `pyproject.toml` with the smallest justified runtime and dev dependencies.
- Pin only minimum compatible ranges; do not add every future optional dependency.
- Create package files under `src/loop_pilot/` according to the implementation manifest.
- Add example configuration without credentials.
- Implement JSON Schemas under `schemas/`.
- Add Markdown templates under `templates/`.
- Add deterministic fixtures under `tests/fixtures/`.
- Add unit, integration, scenario, permission-boundary, timeout, invalid-schema, and Golden tests.
- Keep `.gitignore` protections intact. Strengthen it if generated artifacts reveal missing patterns.
- Update README only with commands that actually pass.

## 8. Testing requirements

At minimum prove:

- illegal state transitions are rejected;
- terminal phase and outcome remain distinct;
- Policy Gate prevents a forbidden write;
- Worker cannot self-approve or self-retry;
- timeout and budget produce a safe outcome and report;
- invalid Agent/Adapter output is rejected;
- Intern fixture changes only allowed files and real pytest passes;
- Paper fixture never invents a citation;
- DailyNews first snapshot does not claim a 24-hour winner;
- second snapshot computes the correct delta;
- duplicate and low-confidence news are filtered;
- reports have required front matter and valid Artifact links;
- `run all` isolates Loop failures;
- no fixture contains secrets, private paths, personal paper text, or company code.

Use MockAdapter for deterministic tests. Do not make tests depend on network access or a paid model.

## 9. Implementation discipline

- Prefer small typed modules and explicit interfaces.
- Do not create a generic framework abstraction until Mini needs it twice.
- Do not add an Agent when deterministic code is sufficient.
- Do not duplicate state in trace, report, and store; RunRecord is authoritative.
- Do not shell-concatenate user input.
- Do not swallow exceptions or convert failure into success.
- Do not weaken tests to make them pass.
- Do not edit architecture documents merely to fit an implementation shortcut.
- Do not leave placeholder code on a path reported as working.

## 10. Completion report

When implementation and tests are complete, provide:

1. files created and modified;
2. implemented Mini capabilities;
3. commands run and exact test results;
4. one result for each Mini Loop;
5. known limitations and intentionally deferred V1+ work;
6. security checks performed;
7. whether every acceptance criterion in `25-mini-run-path.md` passed;
8. a proposed commit message, but do not commit or push.

If any required test fails, do not claim Mini is complete. Stop with the evidence and the smallest next action.

---

End of prompt.
