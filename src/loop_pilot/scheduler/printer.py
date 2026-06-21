"""Print scheduler configuration for cron, systemd, and Windows."""

from __future__ import annotations

import platform
from pathlib import Path

from loop_pilot.scheduler.profiles import ScheduleProfile, DEFAULT_PROFILE
from loop_pilot.summary.renderer import render_schedule_preview


def default_target() -> str:
    if platform.system().lower().startswith("win"):
        return "windows-task-scheduler"
    if Path("/etc/systemd").exists():
        return "systemd"
    return "cron"


def print_schedule(target: str, *, cwd: Path, profile: ScheduleProfile | None = None) -> str:
    profile = profile or DEFAULT_PROFILE
    target = target.lower()
    if target == "cron":
        return _render_cron(profile, cwd)
    if target == "systemd":
        return _render_systemd(profile, cwd)
    if target in {"windows-task-scheduler", "windows", "task-scheduler"}:
        return _render_windows(profile, cwd)
    raise ValueError(f"unsupported schedule target: {target}")


def schedule_preview_markdown(target: str, *, cwd: Path, profile: ScheduleProfile | None = None) -> str:
    profile = profile or DEFAULT_PROFILE
    return render_schedule_preview(
        target=target,
        command=profile.command,
        schedule_time=profile.time,
        cwd=str(cwd.resolve()),
    )


def _render_cron(profile: ScheduleProfile, cwd: Path) -> str:
    hour, minute = profile.time.split(":")
    return "\n".join(
        [
            "# cron preview",
            f"# Run daily at {profile.time}",
            f"{minute} {hour} * * * cd {cwd.resolve()} && {profile.command}",
            "",
            "# Safety: dry-run only; no auto approve; real adapters disabled by default",
        ]
    )


def _render_systemd(profile: ScheduleProfile, cwd: Path) -> str:
    hour, minute = profile.time.split(":")
    return "\n".join(
        [
            "# systemd timer preview",
            "[Unit]",
            "Description=LoopPilot daily dry-run",
            "",
            "[Timer]",
            f"OnCalendar=*-*-* {hour}:{minute}:00",
            "Persistent=true",
            "",
            "[Install]",
            "WantedBy=timers.target",
            "",
            "# service unit would run:",
            f"# WorkingDirectory={cwd.resolve()}",
            f"# ExecStart=/usr/bin/env {profile.command}",
        ]
    )


def _render_windows(profile: ScheduleProfile, cwd: Path) -> str:
    hour, minute = profile.time.split(":")
    command = profile.command.replace('"', '\\"')
    return "\n".join(
        [
            "# Windows Task Scheduler preview",
            f"# Daily at {profile.time}",
            "$Action = New-ScheduledTaskAction `",
            f"  -Execute 'powershell.exe' -Argument '-NoProfile -Command \"cd {cwd.resolve()}; {command}\"'",
            "$Trigger = New-ScheduledTaskTrigger -Daily -At "
            f"{hour}:{minute}",
            f"Register-ScheduledTask -TaskName '{profile.task_name}' -Action $Action -Trigger $Trigger",
            "",
            "# Preview only — 0.4-d does not register tasks",
        ]
    )
