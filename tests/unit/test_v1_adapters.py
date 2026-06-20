"""V1 Adapter contract tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from loop_pilot.adapters.api_model import APIModelAdapter, APIModelConfig
from loop_pilot.adapters.base import (
    AdapterStatus,
    AdapterUsage,
    BaseAdapter,
    CostEstimate,
    HealthStatus,
)
from loop_pilot.adapters.coding_cli import CodingCLIAdapter
from loop_pilot.domain.errors import ErrorCode
from loop_pilot.runtime.boundaries import CancellationToken


def test_coding_cli_adapter_dry_run_writes_transcript_without_running(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    artifacts = tmp_path / "artifacts"
    worktree.mkdir()
    adapter = CodingCLIAdapter(
        adapter_id="test-cli",
        command=[sys.executable, "-c", "raise SystemExit(99)"],
        approved_worktree=worktree,
        artifact_dir=artifacts,
        env_allowlist=["LOOPPILOT_ALLOWED"],
    )

    result = adapter.execute({"prompt": "plan only", "dry_run": True}, timeout=2)

    assert result.status == AdapterStatus.SUCCESS.value
    assert result.structured_output == {"dry_run": True}
    assert result.transcript_artifact is not None
    assert (artifacts / result.transcript_artifact.path).read_text(encoding="utf-8")


def test_coding_cli_adapter_enforces_cwd_timeout_and_env_allowlist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    worktree = tmp_path / "worktree"
    artifacts = tmp_path / "artifacts"
    worktree.mkdir()
    monkeypatch.setenv("LOOPPILOT_ALLOWED", "visible")
    monkeypatch.setenv("LOOPPILOT_SECRET", "hidden")
    script = (
        "import os, time; "
        "print(os.environ.get('LOOPPILOT_ALLOWED')); "
        "print(os.environ.get('LOOPPILOT_SECRET')); "
        "time.sleep(5)"
    )
    adapter = CodingCLIAdapter(
        adapter_id="test-cli",
        command=[sys.executable, "-u", "-c", script],
        approved_worktree=worktree,
        artifact_dir=artifacts,
        env_allowlist=["LOOPPILOT_ALLOWED"],
    )

    result = adapter.execute({"cwd": str(worktree)}, timeout=0.2)

    assert result.status == AdapterStatus.TIMEOUT.value
    assert result.error_code == ErrorCode.TOOL_TIMEOUT.value
    assert result.stdout_artifact is not None
    stdout = (artifacts / result.stdout_artifact.path).read_text(encoding="utf-8")
    assert "visible" in stdout
    assert "hidden" not in stdout


def test_coding_cli_adapter_rejects_unapproved_cwd(tmp_path: Path) -> None:
    adapter = CodingCLIAdapter(
        adapter_id="test-cli",
        command=[sys.executable, "-c", "print('ok')"],
        approved_worktree=tmp_path / "approved",
        artifact_dir=tmp_path / "artifacts",
    )

    result = adapter.execute({"cwd": str(tmp_path / "elsewhere")}, timeout=1)

    assert result.status == AdapterStatus.ERROR.value
    assert result.error_code == ErrorCode.POLICY_DENIED.value


def test_coding_cli_adapter_honors_cancellation(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    token = CancellationToken()
    token.cancel()
    adapter = CodingCLIAdapter(
        adapter_id="test-cli",
        command=[sys.executable, "-c", "print('should not run')"],
        approved_worktree=worktree,
        artifact_dir=tmp_path / "artifacts",
    )

    result = adapter.execute({"cwd": str(worktree)}, timeout=1, cancellation=token)

    assert result.status == AdapterStatus.CANCELLED.value
    assert result.error_code == ErrorCode.TOOL_FAILED.value


def test_adapter_contract_exports_structured_health_usage_and_cost_types() -> None:
    assert BaseAdapter
    assert AdapterUsage(duration_ms=12).duration_ms == 12
    assert CostEstimate(estimated_cost=None).estimated_cost is None
    assert HealthStatus(status="ok", adapter_id="mock").to_dict()["status"] == "ok"


def test_coding_cli_adapter_rejects_push_and_deploy_commands(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    adapter = CodingCLIAdapter(
        adapter_id="test-cli",
        command=["git", "push", "origin", "main"],
        approved_worktree=worktree,
        artifact_dir=tmp_path / "artifacts",
    )

    result = adapter.execute({"cwd": str(worktree)}, timeout=1)

    assert result.status == AdapterStatus.ERROR.value
    assert result.error_code == ErrorCode.POLICY_DENIED.value


def test_api_model_adapter_maps_schema_and_auth_errors_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_http(_payload: dict, _headers: dict) -> dict:
        return {"id": "local-fixture", "choices": [{"message": {"content": "not json"}}]}

    adapter = APIModelAdapter(
        adapter_id="fake-api",
        endpoint="https://example.invalid/v1/chat/completions",
        model="fixture-model",
        auth_env="LOOPPILOT_TEST_API_KEY",
        artifact_dir=tmp_path / "artifacts",
        http_client=fake_http,
    )

    missing_auth = adapter.execute({"messages": []}, timeout=1)
    assert missing_auth.status == AdapterStatus.ERROR.value
    assert missing_auth.error_code == ErrorCode.CONFIG_INVALID.value

    monkeypatch.setenv("LOOPPILOT_TEST_API_KEY", "fixture-key")
    invalid_schema = adapter.execute({"messages": []}, timeout=1)

    assert invalid_schema.status == AdapterStatus.ERROR.value
    assert invalid_schema.error_code == ErrorCode.MODEL_OUTPUT_INVALID.value


def test_api_model_adapter_config_redacts_auth_env_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOOPPILOT_TEST_API_KEY", "super-secret")
    config = APIModelConfig(
        provider="deepseek_compatible",
        endpoint="https://example.invalid/v1/chat/completions",
        model="fixture-model",
        auth_env="LOOPPILOT_TEST_API_KEY",
    )

    adapter = APIModelAdapter.from_config("fake-api", config, tmp_path / "artifacts", http_client=lambda *_: {})

    assert adapter.provider == "deepseek_compatible"
    assert adapter.safe_config()["auth_env"] == "LOOPPILOT_TEST_API_KEY"
    assert "super-secret" not in str(adapter.safe_config())
