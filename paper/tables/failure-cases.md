# Table 3: Failure Case Taxonomy

| ID | Failure mode | Symptom | Root cause class | LoopPilot response | PR #8 / test ref |
|----|--------------|---------|------------------|-------------------|------------------|
| F1 | False completion | Patch run in weekly "Completed" before approve | Missing review gate on terminalize | `WAITING_APPROVAL` / `PARTIAL` / `needs_review` | P0-1, P2-1 |
| F2 | Stale manifest | Checksum mismatch or missing late artifact | Multiple manifest writers / early write | Sole-writer finalize + disk rescan | P1-1, P1-3 |
| F3 | Wrong report link | Summary points to auxiliary file | Hard-coded report names | `REPORT_NAME_PRIORITY` + manifest `kind==report` fallback | P1-2 |
| F4 | Trace dishonesty | `loop_trace` shows succeeded while gate needs review | Trace appended before review gating | Append terminal trace after outcome downgrade | P2-3 |
| F5 | Deferred sync bug | Deferred item reappears as pending | `upsert_pending` overwrites status | Preserve `deferred` until `deferred_until`; terminal decisions immutable | P2 deferred |
| F6 | Interrupt mid-ACTING | Stale lock, partial artifacts | No checkpoint / unclear outcome | `recovery-scan` → `manual_review_required` | 0.4-a |
| F7 | ToolBroker rejection | Mutating call blocked | Policy deny | `BLOCKED` outcome + auditable `tool-results.json` | failure injection |
| F8 | Adapter block | Real adapter without flag | Fail-closed adapter policy | `AdapterBlockedError`, trace entry | RQ4 |
| F9 | Prep-stage schedule install | OS task registered during 0.5 prep | Missing SafetyGate stage check | `PREP_STAGE_BLOCKED` denial | `verify_0_5_prep.py` |
| F10 | SQLite migration drift | Review tables missing after v3 | Schema history | Idempotent v4 repair migration | Phase 3 stabilization |

**Caption:** Representative governance failures that motivated LoopPilot design and acceptance tests. Task-level agent mistakes (wrong patch content) are out of scope; this table covers **runtime honesty** failures.
