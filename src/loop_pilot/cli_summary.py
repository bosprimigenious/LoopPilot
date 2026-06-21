"""Summary CLI commands (0.4-d)."""

from __future__ import annotations

from pathlib import Path

import click

from loop_pilot.app import App
from loop_pilot.cli_tasks import _require_sqlite, _task_services
from loop_pilot.config import load_config
from loop_pilot.summary.service import SummaryService


@click.group()
def summary() -> None:
    """Daily and weekly summaries (requires state_backend=sqlite)."""


@summary.command("today")
@click.option("--date", "date_str", default=None, help="YYYY-MM-DD (default: today in config timezone)")
@click.pass_context
def summary_today(ctx: click.Context, date_str: str | None) -> None:
    """Generate today's daily-summary.md."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    _require_sqlite(cfg)
    app = App.from_config_dir(config_dir)
    task_store, _, _, _ = _task_services(cfg)
    service = SummaryService(cfg, app.state_store, task_store)
    result = service.generate_daily(date_str)
    click.echo(f"Daily summary: {result.path}")


@summary.command("week")
@click.option("--week", "week_label", default=None, help="ISO week e.g. 2026-W25")
@click.pass_context
def summary_week(ctx: click.Context, week_label: str | None) -> None:
    """Generate weekly rollup Markdown."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    _require_sqlite(cfg)
    app = App.from_config_dir(config_dir)
    task_store, _, _, _ = _task_services(cfg)
    service = SummaryService(cfg, app.state_store, task_store)
    result = service.generate_weekly(week_label)
    click.echo(f"Weekly summary: {result.path}")
