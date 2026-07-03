# Paper Outline — Workshop Position + Design Study + Preliminary Evidence

**Title:** Terminal Lies in Personal AI Agents: Completion Admission Control for Daily Automation  
**Subtitle:** The LoopPilot Position Paper

---

## Front matter

- **Authors:** Hengji Zhang, BUPT, bosprimigenious@bupt.edu.cn
- Abstract (`abstract.md`)
- Keywords: terminal lies, completion admission control, personal AI agents, evidence-carrying runs, semantic runtime CI
- **Slogan:** Agent completion must be admitted, not emitted.

---

## Five primary concepts (ONLY these in main narrative)

1. Terminal Lies
2. Completion Admission Control (CAC)
3. Three-Loop Runtime Model
4. Evidence-Carrying Run
5. Semantic Runtime CI

**Implementation layer only (§5):** RGR, RGT, SAC, SafetyGate

---

## Core sentences (repeat in Abstract, Intro, Discussion, Conclusion)

- Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims.
- LoopPilot reframes completion as an admission-control problem.

---

## 1. Introduction (~1.5 pages)

Verbatim central-claim paragraph. Contributions C1–C4 (terminal lies, CAC, Three-Loop, LoopPilot + oracles).

---

## 2. Terminal Lies: A Failure Taxonomy (~1.5 pages)

F1–F6 table. Mini-cases from PR #8.

---

## 3. Completion Admission Control (~1 page + **Figure 2: CAC Pipeline**)

Five dimensions. Evidence-carrying artifact table. CAC pipeline TikZ.

---

## 4. The Three-Loop Runtime Model (~1 page + **Figure 3: Nested Envelopes**)

Task / Evidence / Governance nested boxes. Caption: only surrounding loops admit terminal success.

---

## 5. LoopPilot Design (~2 pages + **Figure 4: Evidence Anatomy** + **§5.4 Walkthrough**)

CAC-to-LoopPilot table. RGR/RGT/SAC/SafetyGate as implementation. 11-step InternLoop walkthrough (patch → needs_review → admit).

---

## 6. Preliminary Evidence and Research Agenda (~1 page)

PR #8 regression + measured acceptance table. Brief semantic runtime CI agenda (RQ1–RQ7 → appendix).

---

## 7. Discussion (~0.75 page)

Core sentences + workshop positioning, scope, limitations.

---

## 8. Related Work (~1.5 pages)

2 paragraphs each: verify-gated completion, proof-carrying agent actions, policy-constrained execution / governance by construction. Shorter: orchestration, SE agents, artifact eval.

---

## 9. Conclusion (~0.5 page)

Core sentences + slogan.

---

## Figures (main text)

| Fig | Content | Section |
|-----|---------|---------|
| 1 | Terminal Lie Propagation | §1 |
| 2 | CAC Pipeline (colored branches) | §3 |
| 3 | Three-Loop Runtime Model (nested) | §4 |
| 4 | Evidence-Carrying Run Anatomy | §5 |

## Appendix figures

| Fig | Content |
|-----|---------|
| A1 | Orchestration-only vs LoopPilot |
| A2 | PR #8 failure-driven redesign |
| A3 | Semantic Runtime CI oracle matrix |

---

## Appendix

- Metric abbreviations
- RQ protocol summary (agenda only)
