# Figure 2 — Completion Admission Control Pipeline

**Location:** TikZ in `latex/main.tex` (`fig:cac-pipeline`), Section~3 (CAC).

**Branches:** ADMITTED (green) | NEEDS_REVIEW (orange) | REJECTED (red) → Trace / Summary / Manifest updated

**Flow (left to right):**

```
Agent proposes completion
  → Completion Claim
  → Evidence Seal Check
  → Review State Check
  → Policy / SafetyGate Check
  → Recovery Consistency Check
  → Admission Decision (ADMITTED | NEEDS_REVIEW | REJECTED)
  → Summary / Trace / Manifest updated
```

**Design notes:** Horizontal pipeline with consistent box sizing; check stages in neutral fill; decision node emphasized; post-admission outputs as a grouped tail.
