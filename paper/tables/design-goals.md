# Table 1: Design Goals for LoopPilot Runtime Governance

| ID | Goal | Description | Primary mechanism | Evidence |
|----|------|-------------|-------------------|----------|
| **G1** | Review-gated lifecycle | No terminal success for mutating runs until explicit human decision or pass gate | `WAITING_APPROVAL`, review CLI, `gate_result.json` | RQ1, PR #8 P0/P2, `experiments/rq1-review-gate.md` |
| **G2** | Auditable artifact contract | Every terminal run exposes a complete, checksum-sealed artifact set | `finalize_terminal_artifacts()`, manifest M1–M5 | RQ2, PR #8 P1, `figures/artifact-contract.md` |
| **G3** | Recoverable persistent state | Crashes and interrupts leave inspectable state; recovery-scan guides resume | SQLite StateStore, `recovery-scan`, migration v4 | RQ3, 0.4-a acceptance |
| **G4** | Fail-closed safety defaults | Real adapters, schedule install, unattended runs blocked unless explicitly enabled | `SafetyGate`, `allow_real_adapters`, ToolBroker policy | RQ4, `verify_0_5_prep.py` |
| **G5** | Truthful terminal reporting | Traces, summaries, and weekly reports must not overstate completion | Phase/outcome split, report path priority, loop_trace honesty | RQ1, PR #8 P2-3, daily summary engine |
| **G6** | Composable orchestration | LoopPilot governs lifecycle; planners/agents may use LangGraph/CrewAI/etc. internally | Adapter boundary, loop definitions as plugins | Architecture §4, related work §5.1 |

**Caption (for paper):** Design goals G1–G6 map runtime governance concerns to concrete LoopPilot mechanisms. Goals G1, G2, and G5 were directly motivated by Codex PR #8 failure-driven redesign.
