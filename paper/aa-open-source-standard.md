# A-Conference and Open-Source Standard

This note turns external venue and open-source norms into a LoopPilot paper and engineering gate.

## What "A-level" means for this paper

The target is not "more agent features." The A-level claim must satisfy five conditions:

1. **Problem sharpness:** name a failure mode that reviewers recognize after one example. For LoopPilot, this is **terminal lies**: false terminal claims that corrupt summaries, schedules, recovery, and user decisions.
2. **Conceptual novelty:** provide a small vocabulary that changes how people reason. The allowed vocabulary remains Terminal Lies, CAC, Three-Loop Runtime Model, Evidence-Carrying Run, and Semantic Runtime CI.
3. **Systems substance:** show a real implementation with hard state, not a prompt pattern. For LoopPilot, that means review-gated terminalization, sealed manifests, SafetyGate, recovery scans, API/mobile visibility, and acceptance scripts.
4. **Executable evidence:** convert claims into runnable oracles and fault-injection tests. A paper without a reproducible artifact should be treated as below the intended bar.
5. **Negative scope discipline:** state what is not claimed: no task-SOTA, no production safety guarantee, no general agent framework, no enterprise governance platform.

## Open-source standard

Open source is not merely putting code online. The project should be usable, inspectable, modifiable, and reviewable by people outside the author.

| Layer | Engineering requirement | Paper value |
|-------|-------------------------|-------------|
| License | Root license and dependency clarity | Makes artifacts legally reusable |
| README | One-command setup, WSL path, API/mobile path | Lowers artifact review friction |
| Contributing | How to run tests, propose changes, and avoid unsafe paths | Shows governance is practiced, not only theorized |
| Code of conduct | Community behavior expectations | Supports future contributor funnel |
| Governance | Maintainer decision rights, release gates, review gates | Connects open-source governance to terminal admission |
| Artifact package | Docker/WSL script, fixtures, expected outputs, logs | Enables ACM-style artifact evaluation |
| Reproducibility | Pinned commit, commands, hashes, environment notes | Supports paper claims and future validation |

## Dual gate

LoopPilot should not claim A-level maturity until both gates pass.

### Paper gate

- [ ] Title and abstract state terminal trust, not generic agent orchestration.
- [ ] Related work distinguishes trust objects: completion claim, action certificate, policy action, terminal run.
- [x] Fault-injection table maps each terminal lie to an executable oracle.
- [x] Acceptance snapshot pins commit, commands, environment, and results.
- [x] Threats to validity separate fixture-heavy evidence from live-adapter evidence.

### Open-source gate

- [x] `README.md` includes WSL setup, API bridge, mobile client, and full validation commands.
- [x] `LICENSE` exists and matches paper artifact license statement.
- [x] `CONTRIBUTING.md` explains local setup, tests, SafetyGate boundaries, and review expectations.
- [x] `CODE_OF_CONDUCT.md` or equivalent community norm exists before soliciting external contributors.
- [x] `GOVERNANCE.md` states who may release, approve artifact claims, and change safety policy.
- [x] Artifact review bundle can be generated from a clean checkout without private credentials.

## Engineering implication

The open-source project itself becomes part of the paper's evidence. If a reviewer cannot run the artifact, inspect the gates, or understand contribution boundaries, the paper's claim about terminal truthfulness is weakened.

## Paper implication

The innovation is not just CAC as a concept. The innovation is **CAC as an open, executable, inspectable governance layer**: the repository demonstrates the same admission discipline that the paper argues for.
