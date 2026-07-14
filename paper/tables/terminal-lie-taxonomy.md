# Terminal Lie Taxonomy

| Terminal Lie Type | Example | LoopPilot Mechanism |
|-------------------|---------|---------------------|
| False Completion | patch unapproved but summary shows completed | RGT |
| Evidence Drift | manifest hash ≠ disk | SAC |
| Human Decision Erasure | deferred → pending via sync | Decision-Preserving Sync |
| Report Misdirection | diff-summary as canonical report | Terminal Truthfulness |
| Boundary Violation | schedule install before readiness | SafetyGate |
| Recovery Misclassification | unsafe resume after reject | recovery-scan |

## Mapping to failure IDs (PR #8)

| ID | Terminal Lie Type | Codex case |
|----|-------------------|------------|
| F1 | False Completion | patch run TERMINATED before approve |
| F2 | Evidence Drift | stale manifest / dual writers |
| F3 | Human Decision Erasure | defer reset on sync |
| F4 | Report Misdirection | diff-summary as primary report |
| F5 | Boundary Violation | prep schedule before readiness |
| F6 | Recovery Misclassification | unsafe resume after reject |
