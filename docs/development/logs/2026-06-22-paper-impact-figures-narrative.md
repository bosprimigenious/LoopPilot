# 2026-06-22 — Workshop paper impact figures & narrative

**Scope:** `paper/latex/main.tex` (+ figure stubs, outline notes).  
**Goal:** Move from "explains enough" to memorable impact without new terminology.

## Main figures (4)

| # | Label | Title | Section | Page (approx.) |
|---|-------|-------|---------|----------------|
| 1 | `fig:lie-propagation` | Terminal Lie Propagation | §1 Introduction (end) | 3 |
| 2 | `fig:cac-pipeline` | Completion Admission Control Pipeline (colored ADMITTED / NEEDS_REVIEW / REJECTED branches) | §3 CAC | 4 |
| 3 | `fig:three-loop` | Three-Loop Runtime Model (nested envelopes) | §4 Three-Loop | 5 |
| 4 | `fig:evidence-anatomy` | Evidence-Carrying Run Anatomy (directory tree + side labels) | §5 Design | 6 |

**Removed from main text:** old `fig:implementation` (implementation mapping swimlane) — content absorbed by walkthrough + appendix comparison.

## Appendix

| ID | Label | Content |
|----|-------|---------|
| A1 | `fig:comparison` | Orchestration-only vs LoopPilot; annotation: "The difference is not planning. The difference is terminal admission." |
| A2 | `fig:pr8-redesign` | PR #8 before/after failure-driven redesign |
| A3 | `tab:semantic-ci` | Semantic Runtime CI oracle matrix |

## Main tables (3)

1. `tab:terminal-lies` — Terminal Lie Taxonomy (F1–F6)
2. `tab:cac-mapping` — CAC Dimension → LoopPilot Component
3. `tab:acceptance-measured` — Acceptance Oracle Results (11/11, 227 passed)

**Demoted:** `tab:artifact-contract` — replaced by Figure 4 anatomy.

## New narrative

- **§1:** Core design principle ("completion is a privilege, not a return value"); enterprise vs personal governance buffers; Figure 1 propagation chain.
- **§2:** Terminal lie propagation prose; durable review state sentence.
- **§3:** CAC ≠ approval button; evidence-carrying run intro; strengthened pipeline colors.
- **§5.4** (`sec:walkthrough`): 11-step InternLoop walkthrough (Task / Evidence / Governance / Admission / Summary).
- **§6:** Traditional CI vs semantic runtime CI contrast.
- **§7:** Completion privilege + appendix comparison pointer.

## Figure stubs

- `paper/figures/terminal-lie-propagation.md`
- `paper/figures/evidence-carrying-run-anatomy.md`
- Updated `paper/figures/cac-pipeline.md`, `paper/outline.md`, `paper/paper.md`

## Build

```powershell
cd paper/latex
pdflatex main.tex; bibtex main; pdflatex main.tex; pdflatex main.tex
```

**Result:** `main.pdf` — **12 pages** (workshop target 11–13).

## Terminology discipline

No new primary concepts. Five core terms only: terminal lies, CAC, Three-Loop Runtime Model, evidence-carrying run, semantic runtime CI. RGR/RGT/SAC/SafetyGate remain §5 implementation details.

## Slogan preserved

> Agent completion must be admitted, not emitted.
