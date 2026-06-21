"""Scheduler install (0.5-a: gated real install with marker/registry)."""

from __future__ import annotations

import json
import platform
import subprocess
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


@dataclass
class InstallResult:
    target: str
    task_name: str
    command: str
    marker_path: Path
    platform_detail: str


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


def _marker_path(cwd: Path) -> Path:
    return cwd / "var" / "artifacts" / "schedule" / "installed.json"


def schedule_status(*, cwd: Path) -> dict[str, object]:
    marker = _marker_path(cwd)
    if not marker.exists():
        return {"installed": False, "marker_path": str(marker)}
    payload = json.loads(marker.read_text(encoding="utf-8"))
    payload["installed"] = True
    payload["marker_path"] = str(marker)
    return payload


def install_schedule(
    *,
    yes: bool = False,
    target: str,
    cwd: Path,
    profile: ScheduleProfile | None = None,
    config_dir: Path | None = None,
) -> InstallResult:
    if not yes:
        raise RuntimeError("Refusing schedule install without --yes")

    profile = profile or DEFAULT_PROFILE
    config_dir = config_dir or Path("config")
    command = f"loop-pilot --config-dir {config_dir.resolve()} run daily --unattended --safe"
    profile = ScheduleProfile(time=profile.time, command=command, task_name=profile.task_name)
    preview = preview_install(target, cwd=cwd, profile=profile)
    output_dir = cwd / "var" / "artifacts" / "schedule"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "schedule-preview.md").write_text(preview.preview_markdown, encoding="utf-8")
    platform_detail = _install_platform(target, cwd=cwd, profile=profile)
    marker = _marker_path(cwd)
    marker.write_text(
        json.dumps(
            {
                "target": target,
                "task_name": profile.task_name,
                "command": profile.command,
                "schedule_time": profile.time,
                "cwd": str(cwd.resolve()),
                "config_dir": str(config_dir.resolve()),
                "platform_detail": platform_detail,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return InstallResult(target, profile.task_name, profile.command, marker, platform_detail)


def uninstall_schedule(*, cwd: Path, profile: ScheduleProfile | None = None) -> bool:
    profile = profile or DEFAULT_PROFILE
    marker = _marker_path(cwd)
    removed = False
    if platform.system().lower().startswith("win"):
        try:
            subprocess.run(["schtasks", "/Delete", "/TN", profile.task_name, "/F"], check=False, capture_output=True, text=True)
            removed = True
        except OSError:
            pass
    if marker.exists():
        marker.unlink()
        removed = True
    return removed


def _install_platform(target: str, *, cwd: Path, profile: ScheduleProfile) -> str:
    target = target.lower()
    if target in {"windows-task-scheduler", "windows", "task-scheduler"}:
        return _install_windows(cwd, profile)
    if target == "cron":
        return "cron install recorded in marker only (manual crontab edit required)"
    if target == "systemd":
        return "systemd install recorded in marker only (manual unit install required)"
    raise ValueError(f"unsupported schedule target: {target}")


def _install_windows(cwd: Path, profile: ScheduleProfile) -> str:
    hour, minute = profile.time.split(":")
    script = f'cd "{cwd.resolve()}"; {profile.command.replace(chr(34), "`" + chr(34))}'
    proc = subprocess.run(
        ["schtasks", "/Create", "/F", "/SC", "DAILY", "/TN", profile.task_name, "/TR", f'powershell.exe -NoProfile -Command "{script}"', "/ST", f"{hour}:{minute}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"schtasks failed: {(proc.stderr or proc.stdout or '').strip()}")
    return f"schtasks created: {profile.task_name}"
