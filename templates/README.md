# Template scaffold

Tracked Markdown templates will live under:

```text
templates/
├── report.md                   # canonical human run summary (see 47-output-interface-spec)
├── review_required.md          # human review entry (0.4-c)
├── next_actions.md             # human follow-up list
├── intern/
├── paper/
├── daily_news/
├── approvals/
└── daily_summary/
```

Canonical per-run names use **underscores** per [docs/development/47-output-interface-spec.md](../docs/development/47-output-interface-spec.md). Loop-specific templates (e.g. `intern/development-report.md`) remain until merged into `report.md` sections.

Templates must not contain private paths, real reports, credentials, paper text, or company data.
