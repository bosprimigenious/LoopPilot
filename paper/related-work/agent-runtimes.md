# Agent Runtimes — Expanded Notes (§5.1)

General-purpose agent runtimes treat the agent loop as a graph or conversation: nodes for tools, memory, and delegation. LangGraph explicitly models cyclic graphs with checkpointing; CrewAI emphasizes role specialization; AutoGen centers multi-agent dialogue. These designs excel when the research question is **coordination efficiency** or **plan diversity**.

LoopPilot differs in scope. Our state machine (Figure 2) is not a planning graph—it is a **governance envelope** with mandatory terminal artifacts and review substates. Checkpointing in LoopPilot serves recovery and audit (`recovery-scan`, SQLite migrations), not replanning alone. Where LangGraph allows `interrupt()` before tool calls, LoopPilot requires `gate_result.json` and manifest sealing before any run influences daily summary "Completed" lists.

**Integration story:** A loop implementation may embed LangGraph internally for Plan/Act while LoopPilot's Orchestrator drives Observe→Evaluate→Report and enforces ToolBroker policy. Publishing this paper does not require LoopPilot to ship a LangGraph adapter; the claim is **composability** (G6), not dependency.

**Open gap:** Comparative microbenchmarks of overhead (latency/size of artifact bundle) versus raw LangGraph execution are TODO.
