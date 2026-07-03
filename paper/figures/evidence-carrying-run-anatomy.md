# Figure 4 — Evidence-Carrying Run Anatomy

**Location:** TikZ in `latex/main.tex` (`fig:evidence-anatomy`), Section~5 (LoopPilot Design).

**Directory tree:**

```
var/artifacts/intern/<run-id>/
├── run_meta.json          (machine state)
├── gate_result.json       (admission state)
├── tool-results.json      (tool audit)
├── loop_trace.jsonl       (lifecycle trace)
├── report.md              (human-readable)
├── review_required.md     (human decision brief)
├── patch.diff             (mutating artifact)
└── artifact-manifest.json (sealed checksum index)
```

**Side labels:** Machine-readable / Human-readable / Mutating artifact / Seal

**Design notes:** Bracket groups with palette tags; replaces standalone artifact-contract table in main text.
