# Security Policy

LoopPilot can eventually read files, execute development commands, call models, and fetch external sources. Until its safety controls are implemented and tested, treat every execution capability as untrusted.

## Never commit

- API keys, tokens, cookies, credentials, private keys, or `.env` files;
- company, internship, laboratory, or private repository contents;
- unpublished paper drafts and private experiment data;
- personal workspaces, memory, reports, traces, model transcripts, caches, or SQLite state;
- third-party content that cannot legally be redistributed.

## Required controls before real execution

- explicit workspace allowlist;
- command and path policy enforcement;
- dry-run mode;
- time, round, model-call, token, and cost budgets;
- process timeout and cancellation;
- secret redaction;
- Artifact and audit logging;
- human approval for destructive or external writes;
- fixture and permission-boundary tests.

## Current status

This repository is an architecture scaffold. Do not connect it to real private workspaces or production credentials until the Mini implementation passes the acceptance criteria in `docs/development/10-testing-and-acceptance.md`.
