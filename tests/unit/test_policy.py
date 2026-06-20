"""Policy Gate tests."""

from __future__ import annotations

from loop_pilot.policy.engine import PolicyEngine


class TestPolicyEngine:
    def test_forbidden_path_denied(self) -> None:
        engine = PolicyEngine()
        decision = engine.check_write(
            ".env.local",
            allowed_paths=["src/**"],
            forbidden_paths=[".env*"],
        )
        assert not decision.allowed
        assert decision.rule_id == "FORBIDDEN_PATH"

    def test_allowed_path_permitted(self) -> None:
        engine = PolicyEngine()
        decision = engine.check_write(
            "src/calculator.py",
            allowed_paths=["src/**", "tests/**"],
            forbidden_paths=[".env*"],
        )
        assert decision.allowed

    def test_forbidden_command_denied(self) -> None:
        engine = PolicyEngine()
        decision = engine.check_command(["git", "push", "origin", "main"])
        assert not decision.allowed
        assert decision.rule_id == "FORBIDDEN_COMMAND"

    def test_dry_run_allows_simulated_write(self) -> None:
        engine = PolicyEngine()
        decision = engine.check_write(
            "secrets/key.txt",
            allowed_paths=[],
            forbidden_paths=["secrets/**"],
            dry_run=True,
        )
        assert decision.allowed
        assert decision.rule_id == "DRY_RUN"
