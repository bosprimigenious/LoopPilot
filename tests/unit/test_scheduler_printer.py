"""Scheduler printer tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.scheduler.printer import print_schedule


def test_print_cron_schedule(tmp_path: Path) -> None:
    text = print_schedule("cron", cwd=tmp_path)
    assert "cron preview" in text
    assert "loop-pilot run daily --dry-run" in text


def test_print_systemd_schedule(tmp_path: Path) -> None:
    text = print_schedule("systemd", cwd=tmp_path)
    assert "systemd timer preview" in text
    assert "LoopPilot daily dry-run" in text


def test_print_windows_schedule(tmp_path: Path) -> None:
    text = print_schedule("windows-task-scheduler", cwd=tmp_path)
    assert "Windows Task Scheduler preview" in text
    assert "Register-ScheduledTask" in text


def test_unsupported_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported"):
        print_schedule("kubernetes", cwd=tmp_path)
