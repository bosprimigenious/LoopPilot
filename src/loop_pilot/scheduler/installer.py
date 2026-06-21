"""Scheduler install preview (no real install until 0.5)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loop_pilot.scheduler.printer import print_schedule, schedule_preview_markdown
from loop_pilot.scheduler.profiles import ScheduleProfile, DEFAULT_PROFILE


@dataclass
class InstallPreview:
    target: str
    config_text: str
    preview_markdown: str
    would_install: bool


def preview_install(
    target: str,
    *,
    cwd: Path,
    profile: ScheduleProfile | None = None,
) -> InstallPreview:
    profile = profile or DEFAULT_PROFILE
    return InstallPreview(
        target=target,
        config_text=print_schedule(target, cwd=cwd, profile=profile),
        preview_markdown=schedule_preview_markdown(target, cwd=cwd, profile=profile),
        would_install=False,
    )


def install_schedule(*, yes: bool = False) -> None:
    if not yes:
        raise RuntimeError("Refusing schedule install without --yes")
    raise NotImplementedError("schedule install --yes is not available until 0.5 Unattended Safe Mode")
