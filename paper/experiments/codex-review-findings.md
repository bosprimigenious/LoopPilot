# Codex Review Findings (PR #8 Summary)

## Context

Automated Codex review on PR #8 (`stabilize/0.4-truthful-acceptance`) surfaced **governance bugs**, not planning failures. Fixes became acceptance criteria for Milestone A.

## Priority themes

| Priority | Theme | Fix summary |
|----------|-------|-------------|
| P0-1 | Patch review gate | `WAITING_APPROVAL` / `PARTIAL` / `needs_review` until approve |
| P0-2 | Direct-finalize approve | No spurious `resume_requested` after approve |
| P1-1 | Manifest self-exclusion | Rescan disk; manifest excludes itself |
| P1-2 | Report path priority | Canonical report names; no `diff-summary.md` as primary |
| P1-3 | Sole manifest writer | InternLoop stops legacy manifest write |
| P2-1 | Patch phase honesty | Not `TERMINATED` while awaiting review |
| P2-2 | review_suggestion ordering | Write before finalize for checksum inclusion |
| P2-3 | Trace truthfulness | Terminal trace after review gating |
| P2 | Deferred sync | Preserve deferred; terminal decisions immutable |

## Paper role

This PR is **failure-driven design evidence**: real review bot caught false success paths that unit tests missed. Cite in §2 Motivating Examples and §9 Results Finding 1–2.

## Detailed case study

See `logs/codex-review-cases.md` for narrative suitable for appendix.

## CHANGELOG reference

Full list in repo root `CHANGELOG.md` Unreleased section.

## TODO for paper

- [ ] Pin merged commit hash after PR #8 merge
- [ ] Count of Codex findings by priority (TODO if not archived in PR comments)
