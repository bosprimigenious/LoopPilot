# Table 5: Baselines and Ablations

| ID | Configuration | What is removed / changed | Expected degradation | Maps to RQ |
|----|---------------|---------------------------|----------------------|------------|
| **A** | **Full LoopPilot** (default) | — | Baseline: truthful gates, manifest, recovery | RQ1–RQ7 |
| **B1** | **No review gate** | Patch runs finalize as `TERMINATED`/`SUCCEEDED` without `WAITING_APPROVAL` | FCR > 0% (F1); RGCR < 100% | RQ1 |
| **B2** | **Prompt-only review** | Advisory Markdown; no RGT hard state | FCR > 0% on stress cases | RQ1 |
| **B3** | **Orchestration interrupt only** | LangGraph pause without gate authority | Summary may overstate; no SAC enforcement | RQ1 (conceptual) |
| **C** | **No manifest checksum rescan** | Loops write manifest inline without disk rescan | MIR < 100% (F2); CFR failures | RQ2 |
| **D** | **No SafetyGate** | `schedule install --yes` allowed in prep stage | BVR > 0% (F9); UMBR < 100% | RQ4 |
| **E** | **Orchestration-only** | LangGraph/CrewAI pipeline without LoopPilot governance layer | No sealed manifest, no review queue, ad-hoc success | RQ1–RQ3, RQ6 (conceptual) |

## Ablation naming (paper prose)

- **Baselines B1–B3** compare review-gate designs (RQ1 GateBench)
- **Ablations C–E** isolate artifact, safety, and orchestration factors

**Implementation notes:**

- **B1** and **C** reproduced historically by pre-PR #8 commits (`logs/codex-review-cases.md`); regression tests on `stabilize/0.4-truthful-acceptance` enforce **A**
- **D** tested via `SafetyGate` with `safety.stage=prep` and `verify_0_5_prep.py`
- **E** is design comparison, not reimplemented system

**Caption:** Baselines B1–B3 and ablations C–E for RQ1–RQ7. Claims apply to **A**.
