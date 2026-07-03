# Figure 1 — Terminal Lie Propagation

**Location:** TikZ in `latex/main.tex` (`fig:lie-propagation`), end of Section~1 (Introduction).

**Flow (top to bottom, red propagation path):**

```
Agent creates patch.diff
  → Runtime marks SUCCEEDED too early
  → gate_result.json still says needs_review
  → weekly summary lists Completed
  → user believes work is done
  → next day automation skips the task
```

**Caption:** How a terminal lie propagates through a personal agent workflow.

**Design notes:** Vertical chain with `lpLie` accent arrows; problem figure before taxonomy section.
