# Abstract

Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims. They are deployed as long-running workflows that mutate workspaces, invoke tools, accumulate state across days, and feed later summaries, schedules, and recovery decisions. Orchestration frameworks excel at planning and multi-step execution, yet they treat terminal success as a model-visible output rather than a runtime admission decision. LoopPilot reframes completion as an admission-control problem: agents may propose completion, but terminal success is admitted only when evidence has been sealed, review decisions preserved, policy boundaries checked, recovery state remains consistent, and semantic runtime acceptance oracles agree.

We call inconsistent terminal claims **terminal lies** and address them through **completion admission control (CAC)**, the **Three-Loop Runtime Model** (Task, Evidence, Governance), and **evidence-carrying runs**, implemented in **LoopPilot** for InternLoop, PaperLoop, and DailyNewsLoop.

This paper is a **systems position and design study with executable oracle evidence**: Codex PR #8 regression cases, version-pinned acceptance oracles, and a research agenda for **semantic runtime CI**. The claim is not task-level SOTA or production safety; it is narrower and testable: terminal truthfulness can be encoded as runtime invariants over evidence bundles, review state, policy boundaries, recovery scans, and post-admission summaries.

**Slogan:** Agent completion must be admitted, not emitted.
