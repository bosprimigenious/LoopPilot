"""Schedule preview CLI (0.4-d)."""

from __future__ import annotations

from pathlib import Path

import click

from loop_pilot.config import load_config
from loop_pilot.scheduler.installer import install_schedule, preview_install
from loop_pilot.scheduler.printer import default_target


@click.group()
def schedule() -> None:
    """Schedule preview (does not install until 0.5)."""


@schedule.command("print")
@click.option(
    "--target",
    default=None,
    help="cron | systemd | windows-task-scheduler (default: platform)",
)
@click.pass_context
def schedule_print(ctx: click.Context, target: str | None) -> None:
    """Print scheduler configuration without installing."""
    config_dir: Path = ctx.obj["config_dir"]
    load_config(config_dir)
    chosen = target or default_target()
    preview = preview_install(chosen, cwd=Path.cwd())
    click.echo(preview.config_text)


@schedule.command("install")
@click.option("--dry-run", is_flag=True, default=False, help="Preview install (default behavior)")
@click.option(
    "--target",
    default=None,
    help="cron | systemd | windows-task-scheduler",
)
@click.option("--yes", is_flag=True, default=False, help="Actually install (0.5 only)")
@click.pass_context
def schedule_install(ctx: click.Context, dry_run: bool, target: str | None, yes: bool) -> None:
    """Preview or refuse real scheduler installation."""
    if yes and not dry_run:
        try:
            install_schedule(yes=True)
        except NotImplementedError as exc:
            raise click.ClickException(str(exc)) from exc
        return

    config_dir: Path = ctx.obj["config_dir"]
    load_config(config_dir)
    chosen = target or default_target()
    preview = preview_install(chosen, cwd=Path.cwd())
    output_dir = Path("var/artifacts/schedule")
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_path = output_dir / "schedule-preview.md"
    preview_path.write_text(preview.preview_markdown, encoding="utf-8")

    click.echo("# Schedule install preview (dry-run)")
    click.echo("")
    click.echo(preview.config_text)
    click.echo("")
    click.echo(f"Preview written: {preview_path}")
    click.echo("No system scheduler entries were created.")
