# Figure 3: Artifact Finalization Pipeline

```mermaid
flowchart LR
    subgraph LoopWrites["Loop-phase writes"]
        W1[run_meta.json]
        W2[tool-results.json]
        W3[report.md / loop reports]
        W4[patch.diff / candidates]
        W5[review_required.md]
    end

    subgraph ReviewPrep["Review gating (InternLoop patch)"]
        MPR[mark_patch_run_waiting_review]
        WRS[write_review_suggestion]
        MPR --> WRS
    end

    subgraph Finalize["finalize_terminal_artifacts() — SOLE MANIFEST WRITER"]
        SCAN[Scan run_dir on disk]
        HASH[Recompute sha256 + size_bytes]
        META[Preserve kind / human_readable]
        EXCL[Exclude artifact-manifest.json]
        ATOM[Atomic .tmp + replace]
        SCAN --> HASH --> META --> EXCL --> ATOM
    end

    subgraph Output["Sealed terminal set"]
        MAN[artifact-manifest.json]
        GATE[gate_result.json]
        TRACE[loop_trace.jsonl<br/>after gating]
    end

    LoopWrites --> ReviewPrep
    ReviewPrep --> Finalize
    WRS --> Finalize
    Finalize --> MAN
    Finalize --> GATE
    Finalize --> TRACE
```

## Manifest invariants M1–M5

See `tables/artifact-contract.md` for full table.

## Report path priority

```text
report.md
  → development-report.md (InternLoop)
  → paper-development-report.md (PaperLoop)
  → daily-news-report.md (DailyNewsLoop)
  → manifest fallback: kind == "report" only (never diff-summary.md)
```

## Caption

**Figure 3.** Artifact finalization pipeline. TikZ source: `latex/main.tex` (Figure~\ref{fig:artifact-pipeline}). Mermaid below is a supplementary sketch.

## Reviewer defense

Checksums are not trust-on-write—they are **verify-on-seal**. Recomputing from disk catches late writes and ordering bugs that inline manifest updates miss (failure F2).
