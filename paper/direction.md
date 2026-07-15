# Mature Paper Direction

## One-sentence thesis

Long-running personal AI agents need a terminal-trust layer: completion must be admitted by the runtime after evidence, review, policy, and recovery checks, not emitted by the model or the task loop.

## Mature title

**Terminal Lies in Personal AI Agents: Completion Admission Control for Long-Running Automation**

The phrase "daily automation" is useful for motivation, but "long-running automation" is the stronger research frame: it covers coding, paper work, and information triage while keeping the paper out of lifestyle-tool territory.

## Paper type

**Systems position + design study + executable oracle evidence.**

This is not a task-SOTA paper and should not compete with SWE-bench-style patch quality results. Its unit of contribution is terminal truthfulness: whether the runtime is allowed to claim that a run is done.

## A-conference bar

The A-level version of this paper must be judged as both a research contribution and an artifact contribution. The research contribution is terminal admission control; the artifact contribution is an open, executable runtime whose tests and failure injections make terminal truthfulness inspectable. See `aa-open-source-standard.md` for the dual paper/open-source gate.

## Core contribution contract

1. Define **terminal lies** as false terminal claims that propagate into summaries, schedules, recovery, and user decisions.
2. Propose **Completion Admission Control (CAC)** as a runtime pattern separating completion proposal from admitted terminal truth.
3. Introduce the **Three-Loop Runtime Model**: Task Loop, Evidence Loop, Governance Loop.
4. Instantiate CAC in LoopPilot with evidence-carrying runs, review-gated terminalization, sealed artifact manifests, SafetyGate, and recovery scans.
5. Evaluate with executable semantic runtime oracles and fault-injection/ablation protocols, not with broad task-success claims.
6. Release the artifact in a form that reviewers can run, inspect, and modify without private credentials.

## Differentiation

| Neighboring line | Their trust object | LoopPilot trust object |
|------------------|--------------------|------------------------|
| Verify-gated completion | Completion claim checked by verifier | Terminal run admitted across review, summary, and recovery state |
| Proof-carrying agent actions | Action certificate | Run-level evidence bundle and post-admission summary truth |
| Policy-constrained runtime governance | Action safety and recovery control | Terminal truthfulness for a single-user long-running workflow |
| Software-engineering agents | Patch correctness / issue resolution | Whether an unapproved or unsealed run may be called complete |

## Strongest venue path

1. **Workshop/short systems paper:** nail terminology, figures, PR #8 failure-driven evidence, and executable acceptance oracles.
2. **Full systems paper:** run GateBench, ArtifactTruthBench, RecoveryFaultBench, SafetyBoundaryBench, and a daily-use trial.
3. **Artifact track:** release reproducible fixtures, acceptance scripts, and failure-injection configurations.

## What to remove or avoid

- Do not present LoopPilot as a general agent framework.
- Do not claim production reliability from local acceptance scripts.
- Do not overuse new acronyms; keep only Terminal Lies, CAC, Three-Loop Runtime Model, Evidence-Carrying Run, and Semantic Runtime CI.
- Do not make "human approval" the novelty. The novelty is durable terminal admission across evidence, review, policy, recovery, and summaries.
- Do not cite current README badge counts unless the paper records a version-pinned rerun.

## Next iteration queue

1. Refresh evidence snapshot after rerunning `ruff`, `pytest`, `verify_0_4_acceptance.py`, `verify_0_5_prep.py`, and the API/mobile static checks.
2. Grow `scripts/run_failure_injection_bench.py` from oracle execution into explicit fault injection.
3. Replace conceptual baselines with executable ablations where possible.
4. Add an explicit "threats to validity" subsection before Related Work.
5. Decide whether the first submission target is a systems workshop, SE workshop, or arXiv technical report.
6. Add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `GOVERNANCE.md` before inviting external artifact review.
