# Human-Gated Autonomy — Expanded Notes (§5.3)

Human-in-the-loop ML traditionally inserts labeling or approval at data boundaries. Agent literature adds "human oversight" via tool confirmation dialogs—often optional and session-scoped. LoopPilot's 0.4-c review layer makes oversight **persistent**: decisions write `ReviewRecord` rows without rewriting original run artifacts; `defer --until` hides items until due and must survive `sync_from_runs` (fixed in P2 deferred sync).

Design non-goals explicitly reject auto-approve on timeout ([46-review-layer-design.md](../../docs/development/46-review-layer-design.md)). This contrasts with enterprise workflow engines that escalate after SLAs. Personal automation prefers **stalling** over **silent approval**.

**Pairing principle:** Humans read `review_required.md`; machines read `gate_result.json`. Markdown alone must never be the source of truth for queue membership—preventing drift when users edit MD files by hand.

**Future work:** Multi-user approval chains (1.3 preview in design docs) remain out of scope; paper discusses single-user threat model.
