# LoopPilot Paper — Mature Direction

> **Gitignored.** This tree is not versioned. See `.gitignore` (`/paper/`, `paper/`).  
> **Tracked log:** `docs/development/logs/2026-06-22-paper-terminology-sharpening.md`

## Positioning

**Title:** Terminal Lies in Personal AI Agents: Completion Admission Control for Long-Running Automation
**Author:** Hengji Zhang, BUPT, bosprimigenious@bupt.edu.cn  
**Slogan:** Agent completion must be admitted, not emitted.

**Stance:** Systems position + design study + executable oracle evidence.

The mature direction is **terminal trust for long-running personal agent runtimes**. LoopPilot should not be framed as another planning/orchestration framework. The paper's contribution is a runtime admission layer that decides when a run is allowed to claim completion after evidence, review, policy, and recovery checks.

See `direction.md` for the current research contract and iteration queue.
See `aa-open-source-standard.md` for the A-conference and open-source readiness gate.

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
- Version-pinned acceptance snapshot (keep, refresh only after rerunning gates)
- **NEW:** CAC-to-LoopPilot mapping (`tables/cac-component-mapping.md`)

## Current research contract

| Claim | Keep it narrow |
|-------|----------------|
| Terminal lies | False terminal claims that corrupt summaries, schedules, recovery, and user decisions |
| CAC | Runtime admission pattern, not a button or prompt instruction |
| Evidence | Run-level bundle with manifests, reports, traces, and gate state |
| Evaluation | Executable semantic runtime oracles and fault-injection protocols |
| Open artifact | Clean-checkout reproducibility, contribution boundaries, and governance docs |
| Non-goal | Task-level SOTA, production safety guarantee, enterprise governance platform |

## LaTeX compile

```powershell
cd paper/latex
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Target: ~10–11 pages workshop PDF.
