"""Integration tests — Loop paths must route through ToolBroker."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from loop_pilot.domain.models import RunRecord, RunRequest
from loop_pilot.domain.states import RunPhase
from loop_pilot.loops.daily_news.loop import DailyNewsLoop
from loop_pilot.loops.intern.loop import InternLoop
from loop_pilot.loops.paper.loop import PaperLoop
from loop_pilot.policy.engine import PolicyEngine
from loop_pilot.reporting.renderer import ReportRenderer
from loop_pilot.tools.broker import ToolBroker


REPO_ROOT = Path(__file__).resolve().parents[2]
LOOP_SOURCES = {
    "intern": REPO_ROOT / "src" / "loop_pilot" / "loops" / "intern" / "loop.py",
    "paper": REPO_ROOT / "src" / "loop_pilot" / "loops" / "paper" / "loop.py",
    "daily_news": REPO_ROOT / "src" / "loop_pilot" / "loops" / "daily_news" / "loop.py",
}


def _forbidden_calls(source: Path, forbidden: set[str]) -> list[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            pair = f"{func.value.id}.{func.attr}"
            if pair in forbidden:
                hits.append(f"{source.name}:{node.lineno} {pair}")
        if isinstance(func, ast.Name) and func.id in {"subprocess", "run"}:
            hits.append(f"{source.name}:{node.lineno} {func.id}(...)")
    return hits


@pytest.mark.parametrize("loop_name", ["intern", "paper", "daily_news"])
def test_loop_modules_forbid_direct_subprocess_and_raw_workspace_writes(loop_name: str) -> None:
    source = LOOP_SOURCES[loop_name]
    forbidden = {"subprocess.run", "subprocess.Popen", "subprocess.call"}
    hits = _forbidden_calls(source, forbidden)
    assert not hits, f"{loop_name} must not call subprocess directly: {hits}"


def test_intern_run_pytest_routes_through_tool_broker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    broker = ToolBroker()
    calls: list[list[str]] = []

    original = broker.run_command

    def spy_run_command(command: list[str], **kwargs):  # noqa: ANN001
        calls.append(list(command))
        return original(command, **kwargs)

    monkeypatch.setattr(broker, "run_command", spy_run_command)

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "test_ok.py").write_text("def test_x(): assert True\n", encoding="utf-8")

    loop = InternLoop(
        artifact_dir,
        PolicyEngine(),
        ReportRenderer(Path("templates")),
        tool_broker=broker,
    )
    report = loop._run_pytest(work_dir, dry_run=False, fixture_dir=Path("."), round_num=1)

    assert "exit_code=0" in report
    assert calls, "InternLoop._run_pytest must invoke ToolBroker.run_command"
    assert calls[0][:3] == [sys.executable, "-m", "pytest"]


def test_intern_apply_fix_routes_through_tool_broker(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    broker = ToolBroker()
    work_dir = tmp_path / "work"
    src = work_dir / "src"
    src.mkdir(parents=True)
    target = src / "calculator.py"
    target.write_text(
        "def add(a, b):\n    return a - b\n\ndef subtract(a, b):\n    return a - b\n",
        encoding="utf-8",
    )

    loop = InternLoop(
        artifact_dir,
        PolicyEngine(),
        ReportRenderer(Path("templates")),
        tool_broker=broker,
    )
    loop._apply_fix(work_dir)

    assert target.read_text(encoding="utf-8").count("return a + b") == 1
    tools = {entry.tool for entry in broker.audit_log}
    assert "file_read" in tools
    assert "file_write" in tools


def test_paper_working_copy_reads_via_tool_broker(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    broker = ToolBroker()
    workspace = tmp_path / "paper_ws"
    workspace.mkdir()
    (workspace / "paper.md").write_text(
        "Our method significantly outperforms all baselines on ImageNet.",
        encoding="utf-8",
    )
    (workspace / "references.bib").write_text("@article{demo, title={Demo}}\n", encoding="utf-8")

    loop = PaperLoop(
        artifact_dir,
        PolicyEngine(),
        ReportRenderer(Path("templates")),
        tool_broker=broker,
    )
    request = RunRequest(
        run_id="paper-broker-test",
        loop_type="paper",
        fixture="unsupported_claim",
        dry_run=True,
    )
    record = RunRecord(run_id=request.run_id, loop_type="paper", phase=RunPhase.CREATED)
    loop.run(request, record)

    tools = {entry.tool for entry in broker.audit_log}
    assert "file_read" in tools
    assert "file_write" in tools


def test_daily_news_source_profile_uses_broker_fetch(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    broker = ToolBroker()
    source_file = tmp_path / "items.json"
    source_file.write_text(
        '{"items": [{"title": "Demo", "url": "https://example.com", "confidence": "high", "category": "github"}]}',
        encoding="utf-8",
    )
    profile = {
        "minimum_confidence": "medium",
        "sources": [{"kind": "local_json", "id": "demo", "path": str(source_file), "enabled": True}],
    }

    loop = DailyNewsLoop(
        artifact_dir,
        PolicyEngine(),
        ReportRenderer(Path("templates")),
        tool_broker=broker,
    )
    request = RunRequest(
        run_id="daily-broker-test",
        loop_type="daily_news",
        source_profile="demo",
        dry_run=True,
    )
    record = RunRecord(run_id=request.run_id, loop_type="daily_news", phase=RunPhase.CREATED)
    loop.run(request, record, source_profile=profile)

    http_calls = [entry for entry in broker.audit_log if entry.tool == "http_get"]
    assert http_calls, "DailyNewsLoop must fetch sources via ToolBroker.fetch_source"
    assert http_calls[0].status == "success"
