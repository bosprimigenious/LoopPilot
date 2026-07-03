# v1 — Workshop Paper (Primary Target)

**Title:** Terminal Lies in Personal AI Agents: Completion Admission Control for Daily Automation  
**Subtitle:** The LoopPilot Position Paper  
**Target venues:** Agent governance workshops, HCI+AI ops, personal AI systems tracks  
**Status:** Position + Design Study + Preliminary Evidence

## Thesis chain

Problem → Terminal Lie | Principle → CAC | Architecture → Three-Loop | Artifact → Evidence-Carrying Run | Evaluation → Semantic Runtime CI | Implementation → RGR/RGT/SAC/SafetyGate

## Structure (9 sections)

1. Introduction — agents can lie about being done
2. Terminal Lies — F1–F6 taxonomy (`tables/terminal-lie-taxonomy.md`)
3. Completion Admission Control — five admission dimensions
4. Three-Loop Runtime Model — Task / Evidence / Governance
5. LoopPilot Design — implementation mechanisms
6. Preliminary Evidence and Research Agenda — PR #8 + measured table; NOT full Results
7. Discussion — workshop positioning, limitations
8. Related Work — verify-gated completion, SafeAgent, Governance by Construction
9. Conclusion

## Key paragraph (Introduction)

> We argue that long-running personal agent workflows expose a failure mode that is under-specified by current orchestration-centric designs: the terminal lie. A terminal lie occurs when a system-visible terminal claim, such as completed, passed, or succeeded, is inconsistent with the run's evidence, review state, policy state, or recovery status. Terminal lies are especially damaging in personal automation because downstream summaries, schedules, and human decisions may treat the false terminal state as trusted. LoopPilot addresses this failure class through completion admission control: agents may propose completion, but the runtime admits terminal success only after evidence has been sealed, review decisions have been preserved, and semantic runtime acceptance checks have passed.

## Measured vs agenda

| Type | Content |
|------|---------|
| **Measured** | ruff pass; pytest 227 passed; verify_0_4 11/11; verify_0_4c 36/36; PR #8 regression cases |
| **Agenda** | Semantic Runtime CI; RQ1–RQ7 benchmark protocols; daily trial; controlled-real E2E |

## Page budget (~10–12 pages)

| Section | Pages |
|---------|-------|
| Intro + taxonomy | 3 |
| CAC + Three-Loop | 2 |
| LoopPilot design | 2.5 |
| Evidence + agenda | 1.5 |
| Discussion + related + conclusion | 2 |

## Preserve sentences

- governance failure not planning error
- orchestration necessary but insufficient
- patch existence is evidence; human approve is the claim gate

## Acceptance criteria before submission

- PR #8 regression cases documented
- 11/11 + 36/36 acceptance logs attached
- PDF compiles; workshop honest positioning throughout
