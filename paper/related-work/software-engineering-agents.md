# Software Engineering Agents — Expanded Notes (§5.2)

Benchmark-oriented coding agents optimize repository edits against test suites. Evaluation harnesses (SWE-bench, HumanEval variants) measure whether generated patches fix issues. Safety discussions in that literature focus on sandbox escape and malicious code, less on **personal workspace honesty** when a user runs agents daily against their own repos.

InternLoop aligns with dev-agent *tasks* but LoopPilot's acceptance tests target PR #8 semantics: `patch.diff` present ⇒ `WAITING_APPROVAL`, weekly summary exclusion, direct-finalize on approve without spurious `resume_requested`. ToolBroker ensures pytest and file writes are allowlisted and logged in `tool-results.json`.

**Reviewer defense:** We do not claim InternLoop achieves competitive SWE-bench scores under MockAdapter fixtures. We claim that **without** governance, even a perfect patch could be misreported as shipped—an operational failure personal users cannot tolerate.

**Citation targets (to add in bib):** SWE-agent, OpenDevin, Codex CLI product docs as engineering context—not as baselines reimplemented in LoopPilot.
