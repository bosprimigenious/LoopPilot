# Paper Terminology Sharpening — 2026-06-22

## Summary

Sharpened LoopPilot workshop paper terminology: five primary concepts only, CAC pipeline as primary figure, merged implementation figure, real bibliography entries, core sentences repeated across Abstract/Intro/Discussion/Conclusion.

## Rule enforced

**No new terminology.** Primary concepts limited to:

1. Terminal Lies
2. Completion Admission Control (CAC)
3. Three-Loop Runtime Model
4. Evidence-Carrying Run
5. Semantic Runtime CI

RGR, RGT, SAC, SafetyGate demoted to §5 LoopPilot Design (implementation layer).

## Core narrative

- Repeated sentence: *Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims.*
- *LoopPilot reframes completion as an admission-control problem.*
- Slogan: **Agent completion must be admitted, not emitted.**

## Contributions (C1–C4)

- C1: Terminal lies as distinct failure mode
- C2: CAC as runtime principle
- C3: Three-Loop Runtime Model
- C4: LoopPilot instantiation + regression oracle evidence

## Figures reorganized

| # | Figure | Notes |
|---|--------|-------|
| 1 | Three-Loop Runtime Model | Stronger TikZ hierarchy, shared color palette |
| 2 | CAC Pipeline | **New primary figure** — full admission pipeline |
| 3 | LoopPilot Implementation Mapping | Merged old architecture + state machine |

Removed standalone state-machine figure (admission states inlined in Fig 3).

## New table

CAC-to-LoopPilot mapping (`paper/tables/cac-component-mapping.md` → Table in §5).

## Related Work

Two paragraphs each for: verify-gated completion, proof-carrying agent actions, policy-constrained execution / governance by construction.

## Bibliography updates

Replaced placeholders with:

- `nguyen2026verifygated` (arXiv:2605.17998)
- `wang2026pcaa` (arXiv:2606.04104)
- `qin2026policy` (arXiv:2604.07833)
- `besanson2026sarc` (arXiv:2605.07728)
- `safeagent2024` (arXiv:2412.13178)

Removed unused placeholder entries (artifactcopilot, verifygated2025, etc.).

## De-emphasized

- RQ1–RQ7 moved to brief agenda + appendix
- Metric abbreviations appendix-only
- No RGR/RGT/SAC as innovation headings

## Files touched (gitignored `paper/` tree)

- `paper/latex/main.tex`
- `paper/latex/references.bib`
- `paper/abstract.md`, `paper.md`, `outline.md`, `README.md`
- `paper/tables/cac-component-mapping.md` (NEW)
- `paper/figures/cac-pipeline.md` (NEW)

## Compile

```powershell
cd paper/latex
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Post-compile metrics

| Metric | Value |
|--------|-------|
| PDF pages | **10** |
| Figures | 3 (Three-Loop; CAC Pipeline; LoopPilot Implementation Mapping) |
| Bib entries | 13 in `references.bib`; 12 cited in compiled `main.bbl` |
| Build | `pdflatex` + `bibtex` + `pdflatex` ×2 — success |
