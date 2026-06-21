"""Schedule CLI (0.4-d preview, 0.5-a gated install)."""

from __future__ import annotations

import json
from pathlib import Path

import click

from loop_pilot.config import load_config
from loop_pilot.safety.gate import SafetyGate
from loop_pilot.scheduler.installer import install_schedule, preview_install, schedule_status, uninstall_schedule
from loop_pilot.scheduler.printer import default_target


@click.group()
def schedule() -> None:
    """Schedule preview and gated install (0.5-prep blocks real OS writes)."""


@schedule.command("print")
@click.option("--target", default=None, help="cron | systemd | windows-task-scheduler")
@click.pass_context
def schedule_print(ctx: click.Context, target: str | None) -> None:
    load_config(ctx.obj["config_dir"])
    preview = preview_install(target or default_target(), cwd=Path.cwd())
    click.echo(preview.config_text)


@schedule.command("status")
@click.pass_context
def schedule_status_cmd(ctx: click.Context) -> None:
    load_config(ctx.obj["config_dir"])
    click.echo(json.dumps(schedule_status(cwd=Path.cwd()), indent=2))


@schedule.command("install")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--target", default=None)
@click.option("--yes", is_flag=True, default=False)
@click.option("--confirm-schedule", is_flag=True, default=False)
@click.pass_context
def schedule_install(ctx: click.Context, dry_run: bool, target: str | None, yes: bool, confirm_schedule: bool) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    chosen = target or default_target()
    if yes and not dry_run:
        result = SafetyGate.from_config(cfg).check(
            "schedule.install",
            confirm=confirm_schedule,
            target=chosen,
        )
        if result.denied:
            raise click.ClickException(f"BLOCKED: {result.message} ({result.reason_code})")
        try:
            installed = install_schedule(
                yes=True,
                target=chosen,
                cwd=Path.cwd(),
                config_dir=config_dir,
                config=cfg,
            )
        except RuntimeError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(
            f"Schedule {installed.install_status.value}: {installed.task_name}\n"
            f"  command: {installed.command}\n"
            f"  marker: {installed.marker_path}"
        )
        return
    preview = preview_install(chosen, cwd=Path.cwd())
    output_dir = Path("var/artifacts/schedule")
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_path = output_dir / "schedule-preview.md"
    preview_path.write_text(preview.preview_markdown, encoding="utf-8")
    click.echo(
        f"# Schedule install preview (dry-run)\n\n{preview.config_text}\n\n"
        f"Preview written: {preview_path}\nNo system scheduler entries were created."
    )


@schedule.command("uninstall")
@click.option("--yes", is_flag=True, default=False)
@click.option("--confirm-schedule", is_flag=True, default=False)
@click.pass_context
def schedule_uninstall(ctx: click.Context, yes: bool, confirm_schedule: bool) -> None:
    if not yes:
        raise click.ClickException("Refusing uninstall without --yes")
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    result = SafetyGate.from_config(cfg).check("schedule.uninstall", confirm=confirm_schedule)
    if result.denied:
        raise click.ClickException(f"BLOCKED: {result.message} ({result.reason_code})")
    try:
        removed = uninstall_schedule(cwd=Path.cwd(), config=cfg)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo("Schedule uninstalled." if removed else "No schedule install marker found.")
