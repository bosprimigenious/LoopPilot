"""ToolBroker policy enforcement tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.tools.broker import ToolBroker
from loop_pilot.tools.policy import ToolPolicy


def test_tool_broker_blocks_forbidden_command() -> None:
    broker = ToolBroker(ToolPolicy(allowed_commands=["pytest"], forbidden_tokens=["push"]))
    with pytest.raises(LoopPilotError) as exc:
        broker.run_command(["git", "push", "origin"], cwd=Path("."))
    assert exc.value.code == ErrorCode.POLICY_DENIED


def test_tool_broker_blocks_unlisted_command(tmp_path: Path) -> None:
    broker = ToolBroker(ToolPolicy(allowed_commands=["pytest"], cwd_roots=[str(tmp_path)]))
    with pytest.raises(LoopPilotError) as exc:
        broker.run_command(["curl", "https://example.com"], cwd=tmp_path)
    assert exc.value.code == ErrorCode.POLICY_DENIED


def test_tool_broker_blocks_write_outside_allowlist(tmp_path: Path) -> None:
    broker = ToolBroker()
    secret = tmp_path / ".env"
    with pytest.raises(LoopPilotError) as exc:
        broker.write_file(secret, "KEY=secret", forbidden=[".env"])
    assert exc.value.code == ErrorCode.POLICY_DENIED


def test_tool_broker_allows_pytest_in_worktree(tmp_path: Path) -> None:
    broker = ToolBroker(ToolPolicy(cwd_roots=[str(tmp_path)]))
    (tmp_path / "test_ok.py").write_text("def test_x(): assert True\n", encoding="utf-8")
    result = broker.run_command(["pytest", "-q", "test_ok.py"], cwd=tmp_path, timeout=30)
    assert result.exit_code == 0
