# Terminal Lies in Personal AI Agents: Completion Admission Control for Daily Automation

**Subtitle:** The LoopPilot Position Paper

**Author:** Hengji Zhang, BUPT, bosprimigenious@bupt.edu.cn

**Slogan:** Agent completion must be admitted, not emitted.

---

## Abstract

See `abstract.md`.

---

## 1. Introduction

Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims. LoopPilot reframes completion as an admission-control problem.

The central claim of this paper is that personal AI agents fail not only when they produce incorrect actions, but also when the runtime falsely admits those actions as completed work. We call this failure mode a terminal lie. Unlike ordinary task errors, terminal lies corrupt downstream trust: summaries, schedules, recovery scans, and human decisions may all treat an untrusted state as final. LoopPilot addresses this problem through completion admission control. Agents may propose completion, but terminal success is admitted only when evidence has been sealed, review decisions have been preserved, policy boundaries have been checked, and semantic runtime acceptance oracles agree. This shifts the research question from "Can the agent finish the task?" to "When is the runtime allowed to say the task is finished?"

### Contributions

- **C1** We identify terminal lies as a distinct failure mode in personal AI agent workflows.
- **C2** We propose completion admission control as a runtime principle for preventing terminal lies.
- **C3** We introduce the Three-Loop Runtime Model to separate task execution, evidence sealing, and governance admission.
- **C4** We instantiate the model in LoopPilot and provide preliminary acceptance evidence from regression oracles.

---

## 2–9. Sections

See `latex/main.tex` for full workshop draft. Key artifacts:

- `figures/terminal-lie-propagation.md` — Figure 1 notes
- `figures/cac-pipeline.md` — Figure 2 notes
- `figures/evidence-carrying-run-anatomy.md` — Figure 4 notes
- `tables/cac-component-mapping.md` — CAC mapping table
- `tables/terminal-lie-taxonomy.md` — F1–F6

---

## Related Work (sharp differentiation)

1. **Verify-gated completion** — step/claim verification; LoopPilot = terminal trust across personal daily workflow
2. **Proof-carrying agent actions** — action-level certificates; LoopPilot = run-level evidence-carrying terminal bundle
3. **Policy-constrained execution / Governance by Construction** — action safety / enterprise checkpoints; LoopPilot = terminal truthfulness for single-user daily automation

---

## Conclusion

Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims. LoopPilot reframes completion as an admission-control problem. **Agent completion must be admitted, not emitted.**
