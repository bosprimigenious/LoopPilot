# Terminal Lies in Personal AI Agents: Completion Admission Control for Long-Running Automation

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
- **C4** We instantiate the model in LoopPilot and provide executable semantic runtime oracles from regression evidence.

---

## 2–9. Sections

See `latex/main.tex` for full workshop draft. Key artifacts:

- `figures/terminal-lie-propagation.md` — Figure 1 notes
- `figures/cac-pipeline.md` — Figure 2 notes
- `figures/evidence-carrying-run-anatomy.md` — Figure 4 notes
- `tables/cac-component-mapping.md` — CAC mapping table
- `tables/terminal-lie-taxonomy.md` — F1–F6

---

## Mature Direction

LoopPilot should be framed as a terminal-trust layer for long-running personal agent runtimes. The mature claim is deliberately narrow: a runtime should not say a run is done until evidence, review, policy, recovery, and summary state agree. This makes the work comparable to verify-gated completion, proof-carrying agent actions, and policy-constrained runtime governance, but keeps the trust object different: LoopPilot certifies the terminal run, not merely a verifier event, an action certificate, or a policy-admitted tool call.

The first submission should be a systems position/design study with executable oracle evidence. The full-paper path is to run fault-injection and ablation suites around false completion, manifest integrity, review-state preservation, safety-boundary blocking, and daily-use summary truthfulness.

The open-source repository is not only dissemination. It is evidence. If reviewers cannot run the artifact from a clean checkout, inspect the gates, or understand contribution and governance boundaries, the paper's claim about terminal truthfulness is weaker. The mature artifact target is therefore ACM-style artifact evaluation readiness: functional, reusable, available, and documented enough for external inspection.

## Related Work (sharp differentiation)

1. **Verify-gated completion** — step/claim verification; LoopPilot = terminal trust across long-running personal workflow
2. **Proof-carrying agent actions** — action-level certificates; LoopPilot = run-level evidence-carrying terminal bundle
3. **Policy-constrained execution / Governance by Construction** — action safety / enterprise checkpoints; LoopPilot = terminal truthfulness for single-user long-running automation

---

## Conclusion

Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims. LoopPilot reframes completion as an admission-control problem. **Agent completion must be admitted, not emitted.**
