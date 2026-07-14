# Abstract

Personal AI agents do not merely fail by producing wrong actions; they fail by producing false terminal claims. They are deployed as long-running daily workflows that mutate workspaces, invoke tools, and accumulate state across days. Orchestration frameworks excel at planning and multi-step execution, yet they treat terminal success as a model-visible output rather than a runtime admission decision. LoopPilot reframes completion as an admission-control problem: agents may propose completion, but terminal success is admitted only when evidence has been sealed, review decisions preserved, policy boundaries checked, and semantic runtime acceptance oracles agree.

We call inconsistent terminal claims **terminal lies** and address them through **completion admission control (CAC)**, the **Three-Loop Runtime Model** (Task, Evidence, Governance), and **evidence-carrying runs**, implemented in **LoopPilot** for InternLoop, PaperLoop, and DailyNewsLoop.

This paper is a **position and design study with preliminary acceptance evidence**: Codex PR #8 regression cases, measured acceptance oracles (ruff pass; pytest 227 passed; `verify_0_4` 11/11; `verify_0_4c` 36/36), and a research agenda for **semantic runtime CI**.

**Slogan:** Agent completion must be admitted, not emitted.
