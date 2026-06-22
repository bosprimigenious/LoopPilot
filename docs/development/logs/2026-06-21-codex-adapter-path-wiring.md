# Codex P1 — adapter path wiring (2026-06-21)

## Problem

`SafetyGate._check_adapter_invoke` existed but only ran when callers explicitly invoked `SafetyGate.check`. The real execution path `_run_single → Orchestrator.run_loop → create_adapter(...)` bypassed the gate: `allow_real_adapters=true` could reach real adapter instantiation even when `safety.max_level` blocked level 3+.

## Fix

| Area | Change |
|------|--------|
| `safety/adapter_levels.py` | Map adapter kinds → `SafetyLevel` (mock=1, cli/cursor_cli=3, api/openai_compatible=4) |
| `adapters/factory.py` | `_check_adapter_safety_gate()` before `build_adapter` / `validate_adapter_run` for real kinds when `config` is provided |
| `loops/*` + `orchestrator.py` | Pass `LoopPilotConfig` into loops → `create_adapter(..., config=...)` |

Fail-closed: gate deny → `AdapterBlockedError` (same blocked-run path as `allow_real_adapters=false`).

## Level mapping

| Kind | SafetyLevel |
|------|-------------|
| `mock` | 1 (COLLECT) — gate skipped (not real) |
| `cli`, `cursor_cli` | 3 (REAL_GUARDED) |
| `api`, `openai_compatible` | 4 (REAL_BOUNDED) |

## Tests

- `tests/integration/test_adapter_safety_gate_path.py`: `allow_real_adapters=true` + `max_level=2` → intern `--adapter cursor_cli` blocked with `LEVEL_EXCEEDS_MAX` / safety gate message
- Existing `test_safety_gate.py` unit coverage for gate logic unchanged

## Merge blocker

| Item | Status |
|------|--------|
| `adapter.invoke` bypass on real execution path | **Cleared** |

## Commits

- `fix(safety): wire SafetyGate into adapter execution path (Codex P1)`
- `fix(locks): treat PermissionError as live PID (Codex P2)`
- `docs: adapter path wiring fix log`
