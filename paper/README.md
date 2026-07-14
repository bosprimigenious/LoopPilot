# LoopPilot Paper — Workshop Position Paper (Primary Target)

> **Gitignored.** This tree is not versioned. See `.gitignore` (`/paper/`, `paper/`).  
> **Tracked log:** `docs/development/logs/2026-06-22-paper-terminology-sharpening.md`

## Positioning

**Title:** Terminal Lies in Personal AI Agents: Completion Admission Control for Daily Automation  
**Author:** Hengji Zhang, BUPT, bosprimigenious@bupt.edu.cn  
**Slogan:** Agent completion must be admitted, not emitted.

**Stance:** Position + Design Study + Preliminary Evidence.

## Five primary concepts (no new terms in main text)

1. Terminal Lies
2. Completion Admission Control (CAC)
3. Three-Loop Runtime Model
4. Evidence-Carrying Run
5. Semantic Runtime CI

RGR/RGT/SAC/SafetyGate → §5 implementation only.

## Figures (TikZ in `latex/main.tex`)

1. Three-Loop Runtime Model
2. CAC Pipeline (primary)
3. LoopPilot Implementation Mapping (merged old arch + state machine)

## Tables

- Terminal lie taxonomy (keep)
- Evidence-carrying artifacts (keep)
- Measured acceptance 11/11, 227 passed (keep)
- **NEW:** CAC-to-LoopPilot mapping (`tables/cac-component-mapping.md`)

## LaTeX compile

```powershell
cd paper/latex
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Target: ~10–11 pages workshop PDF.
