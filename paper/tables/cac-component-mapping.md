# CAC-to-LoopPilot Component Mapping

| CAC Dimension | LoopPilot Component | Artifact / State |
|---------------|---------------------|------------------|
| Completion claim | RunOutcome / phase | `run_meta.json` |
| Evidence bundle | ArtifactStore / finalizer | `artifact-manifest.json` |
| Review state | Review Gate | `gate_result.json` |
| Policy state | SafetyGate / ToolBroker | `tool-results.json` |
| Admission decision | Orchestrator | `loop_trace.jsonl` / summary |

Used in `latex/main.tex` Table~\ref{tab:cac-mapping} (Section~5).
