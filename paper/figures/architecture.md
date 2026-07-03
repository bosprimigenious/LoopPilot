# Figure 1: LoopPilot Architecture

```mermaid
flowchart TB
    subgraph Triggers["L0 Triggers"]
        CLI[CLI / manual]
        SCH[OS Scheduler<br/>0.5 unattended]
    end

    subgraph Control["L1 Control Plane — Runtime Governance"]
        ORCH[Orchestrator]
        SM[State Machine<br/>phases + review substates]
        SG[SafetyGate L0–L4]
        POL[Policy Engine]
        REV[Review Layer<br/>approve / reject / defer]
        CKPT[Checkpoint / Lock Manager]
    end

    subgraph Loops["L2 Loop Definitions"]
        IL[InternLoop]
        PL[PaperLoop]
        DNL[DailyNewsLoop]
    end

    subgraph Pipeline["L3 Runtime Pipeline"]
        OBS[Observe → Plan → Act]
        TB[ToolBroker<br/>allowlisted tools]
        EV[Evaluate → Report]
    end

    subgraph State["L5 State & Evidence"]
        SQL[(SQLite StateStore)]
        ART[Artifact dir<br/>manifest + traces]
    end

    subgraph External["Composable backends (optional)"]
        LG[LangGraph / CrewAI / AutoGen<br/>planning inside Adapter]
    end

    CLI --> ORCH
    SCH --> SG
    SG --> ORCH
    ORCH --> SM
    SM --> Loops
    IL & PL & DNL --> OBS
    OBS --> POL
    POL --> TB
    TB --> EV
    EV --> REV
    REV --> ART
    ORCH --> SQL
    CKPT --> SQL
    TB -.-> External
```

## Caption

**Figure 1.** LoopPilot architecture. TikZ source: `latex/main.tex` (Figure~\ref{fig:architecture}). Mermaid below is a supplementary sketch.

## Text for paper body

LoopPilot separates **orchestration** (inside loop implementations and adapters) from **governance** (control plane). Triggers may be manual CLI or, in 0.5, OS-scheduled unattended invocations that must pass SafetyGate before Orchestrator starts. Every mutating path flows through Policy Engine and ToolBroker; terminal paths produce sealed artifacts and may enter the review queue rather than claiming success.
