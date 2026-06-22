# Paper Workshop Position Reframe — 2026-06-22

## Summary

Repositioned LoopPilot paper from **review-gated runtime governance** thesis to **terminal lies + completion admission control (CAC)** for workshop submission (Position + Design Study + Preliminary Evidence).

## Rationale

| Old framing | New framing |
|-------------|-------------|
| Safe personal automation requires review-gated runtime governance | Agent completion is a runtime admission decision, not a model output |
| RGR/RGT/SAC as primary novelty (4+ abbreviations) | Five core terms: Terminal Lie, CAC, Three-Loop Model, Evidence-Carrying Run, Semantic Runtime CI |
| Preliminary Empirical Evidence (v0.3) | Position + Design Study + Preliminary Evidence (workshop honest) |
| RQ1–RQ7 as evaluation centerpiece | Semantic Runtime CI as agenda; measured acceptance oracles only in §6 |

## New title

**Main:** Terminal Lies in Personal AI Agents: Completion Admission Control for Daily Automation  
**Subtitle:** The LoopPilot Position Paper

## Section structure (9 sections)

1. Introduction
2. Terminal Lies: A Failure Taxonomy (F1–F6)
3. Completion Admission Control
4. The Three-Loop Runtime Model
5. LoopPilot Design (RGR/RGT/SAC/SafetyGate as implementation)
6. Preliminary Evidence and Research Agenda
7. Discussion
8. Related Work
9. Conclusion

## Files updated (gitignored `paper/` tree)

- `paper/latex/main.tex` — full LaTeX restructure
- `paper/latex/references.bib` — SafeAgent, Governance by Construction entries
- `paper/abstract.md`, `paper.md`, `outline.md`, `README.md`
- `paper/related-work.md`
- `paper/drafts/v1-workshop-paper.md` — primary workshop target
- `paper/tables/terminal-lie-taxonomy.md` — NEW

## Preserved sentences

- governance failure not planning error
- orchestration necessary but insufficient
- patch existence is evidence; human approve is the claim gate

## Measured vs agenda

**Measured (reported in §6 only):**

- `ruff check .` — pass
- `pytest -q` — 227 passed
- `verify_0_4_acceptance.py` — 11/11 READY
- `verify_0_4c_acceptance.py` — 36/36 READY
- PR #8 regression design evidence (seven Codex cases)

**Agenda (not claimed as results):**

- Semantic Runtime CI benchmark suites (RQ1–RQ7 protocols)
- Daily-use trial
- Controlled-real E2E
- Full failure-injection at scale

## Related work differentiation added

1. Verify-gated completion — lifecycle honesty vs step verifier
2. SafeAgent — action safety vs terminal claim honesty
3. Governance by Construction — enterprise ops vs single-user daily consistency

## Commit policy

Only this log file is tracked; `paper/` remains gitignored per project convention.
