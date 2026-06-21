"""Integration: real adapters blocked by default."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from loop_pilot.cli import app
from loop_pilot.runtime.trace import read_trace


def _latest_intern_run_dir() -> Path | None:
    base = Path("var/artifacts/intern")
    if not base.is_dir():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda p: p.stat().st_mtime)


def test_intern_real_adapter_blocked_by_default() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "intern",
            "--workspace",
            "examples/intern_demo",
            "--adapter",
            "cursor_cli",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "allow_real_adapters=false" in result.output.lower()


def test_paper_deepseek_blocked_missing_key_with_opt_in() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "paper",
            "--workspace",
            "examples/paper_demo",
            "--adapter",
            "deepseek",
            "--allow-real-adapters",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "missing api key" in result.output.lower()
    assert "Traceback" not in result.output


def test_fake_adapter_is_blocked() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "intern", "--adapter", "fake_adapter", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "unknown adapter" in result.output.lower()
    assert "succeeded" not in result.output.lower()


def test_unknown_adapter_is_blocked() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "intern", "--adapter", "not_a_real_adapter_id", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "blocked" in result.output.lower()
    assert "unknown adapter" in result.output.lower()


def test_adapter_trace_created_for_blocked_adapter() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "intern",
            "--workspace",
            "examples/intern_demo",
            "--adapter",
            "cursor_cli",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    run_dir = _latest_intern_run_dir()
    assert run_dir is not None
    trace_path = run_dir / "adapter-call-trace.jsonl"
    assert trace_path.is_file()
    events = read_trace(trace_path)
    assert len(events) == 1
    assert events[0]["event"] == "adapter_blocked"
    assert events[0]["status"] == "blocked"
    assert "allow_real_adapters" in events[0]["blocked_reason"].lower() or events[0]["allow_real_adapters"] is False
    assert events[0]["dry_run"] is True


def test_artifact_manifest_includes_adapter_trace() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "intern",
            "--workspace",
            "examples/intern_demo",
            "--adapter",
            "fake_adapter",
            "--dry-run",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    run_dir = _latest_intern_run_dir()
    assert run_dir is not None
    manifest_path = run_dir / "artifact-manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    kinds = [item["kind"] for item in manifest.get("artifacts", [])]
    assert "trace" in kinds
    trace_refs = [item for item in manifest["artifacts"] if item["kind"] == "trace"]
    assert any("adapter-call-trace.jsonl" in item["path"] for item in trace_refs)
