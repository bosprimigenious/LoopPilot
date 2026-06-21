"""Inbox / Queue / Today CLI commands (0.4-b)."""

from __future__ import annotations

import json
from pathlib import Path

import click

from loop_pilot.config import LoopPilotConfig, load_config
from loop_pilot.tasks.daily_news_importer import DailyNewsImporter
from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


def _require_sqlite(cfg: LoopPilotConfig) -> Path:
    backend = str(cfg.runtime.get("state_backend", "json")).lower()
    if backend != "sqlite":
        raise click.ClickException(
            "inbox/queue/today commands require runtime.state_backend=sqlite "
            f"(current: {backend!r}). See docs/development/40-personal-daily-loop-0.4-spec.md"
        )
    return cfg.sqlite_path


def _task_services(cfg: LoopPilotConfig) -> tuple[TaskStore, InboxService, QueueService, TodayService]:
    store = TaskStore(_require_sqlite(cfg))
    inbox = InboxService(store)
    queue = QueueService(store, inbox)
    timezone = str(cfg.runtime.get("timezone", "Asia/Shanghai"))
    today = TodayService(store, queue, timezone=timezone)
    return store, inbox, queue, today


def _format_inbox_table(items: list) -> None:
    click.echo(f"{'ID':10} {'Source':12} {'Loop':12} {'Priority':8} {'Status':10} Title")
    for item in items:
        click.echo(
            f"{item.id:10} {item.source:12} {item.loop_hint:12} {item.priority:<8} "
            f"{item.status:10} {item.title}"
        )


def _format_queue_table(items: list) -> None:
    click.echo(f"{'ID':10} {'Loop':12} {'Priority':8} {'Status':10} {'Scheduled':12} Title")
    for item in items:
        scheduled = item.scheduled_for or "-"
        click.echo(
            f"{item.id:10} {item.loop_type:12} {item.priority:<8} {item.status:10} "
            f"{scheduled:12} {item.title}"
        )


@click.group()
def inbox() -> None:
    """Personal task inbox (requires state_backend=sqlite)."""


@inbox.command("add")
@click.argument("text")
@click.option("--source", default="manual", show_default=True)
@click.option("--loop", "loop_hint", default="unknown", show_default=True)
@click.option("--priority", default=3, show_default=True, type=int)
@click.option("--body", default=None, help="Optional longer description")
@click.pass_context
def inbox_add(
    ctx: click.Context,
    text: str,
    source: str,
    loop_hint: str,
    priority: int,
    body: str | None,
) -> None:
    """Add a task to the inbox."""
    cfg = load_config(ctx.obj["config_dir"])
    _, inbox_service, _, _ = _task_services(cfg)
    try:
        result = inbox_service.add(
            text,
            body=body,
            source=source,
            loop_hint=loop_hint,
            priority=priority,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Inbox item created: {result.item.id}")


@inbox.command("list")
@click.option("--status", default="open", show_default=True, help="open, promoted, archived, or all")
@click.pass_context
def inbox_list(ctx: click.Context, status: str) -> None:
    """List inbox items."""
    cfg = load_config(ctx.obj["config_dir"])
    _, inbox_service, _, _ = _task_services(cfg)
    try:
        items = inbox_service.list_items(status=status)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    if not items:
        click.echo("No inbox items.")
        return
    _format_inbox_table(items)


@inbox.command("archive")
@click.argument("inbox_id")
@click.pass_context
def inbox_archive(ctx: click.Context, inbox_id: str) -> None:
    """Archive an inbox item."""
    cfg = load_config(ctx.obj["config_dir"])
    _, inbox_service, _, _ = _task_services(cfg)
    try:
        item = inbox_service.archive(inbox_id)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Inbox item archived: {item.id}")


@inbox.command("import-daily-news")
@click.option("--from", "from_path", required=True, type=click.Path(path_type=Path))
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def inbox_import_daily_news(ctx: click.Context, from_path: Path, dry_run: bool) -> None:
    """Import DailyNews candidate-actions.json into inbox."""
    cfg = load_config(ctx.obj["config_dir"])
    _, inbox_service, _, _ = _task_services(cfg)
    importer = DailyNewsImporter(inbox_service)
    try:
        result = importer.import_from_file(from_path, dry_run=dry_run)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc

    prefix = "Would import" if dry_run else "Imported"
    click.echo(f"{prefix}: {len(result.imported)} item(s)")
    if result.skipped_duplicates:
        click.echo(f"Skipped duplicates: {len(result.skipped_duplicates)}")
    for item_id in result.imported[:10]:
        click.echo(f"  - {item_id}")
    if len(result.imported) > 10:
        click.echo(f"  ... and {len(result.imported) - 10} more")


@click.group()
def queue() -> None:
    """Personal task queue (requires state_backend=sqlite)."""


@queue.command("promote")
@click.argument("inbox_id")
@click.option("--loop", "loop_type", default=None, help="intern, paper, or daily-news")
@click.option("--priority", default=None, type=int)
@click.pass_context
def queue_promote(
    ctx: click.Context,
    inbox_id: str,
    loop_type: str | None,
    priority: int | None,
) -> None:
    """Promote an inbox item to the queue."""
    cfg = load_config(ctx.obj["config_dir"])
    _, _, queue_service, _ = _task_services(cfg)
    try:
        item = queue_service.promote(inbox_id, loop_type=loop_type, priority=priority)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Queue item created: {item.id} (from {inbox_id})")


@queue.command("list")
@click.option("--status", default=None, help="Filter by queue status")
@click.pass_context
def queue_list(ctx: click.Context, status: str | None) -> None:
    """List queue items."""
    cfg = load_config(ctx.obj["config_dir"])
    _, _, queue_service, _ = _task_services(cfg)
    items = queue_service.list_items(status=status)
    if not items:
        click.echo("No queue items.")
        return
    _format_queue_table(items)


@queue.command("demote")
@click.argument("queue_id")
@click.pass_context
def queue_demote(ctx: click.Context, queue_id: str) -> None:
    """Move a queue item back to inbox."""
    cfg = load_config(ctx.obj["config_dir"])
    _, _, queue_service, _ = _task_services(cfg)
    try:
        item = queue_service.demote(queue_id)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Queue item demoted; inbox reopened: {item.id}")


@click.group(invoke_without_command=True)
@click.pass_context
def today(ctx: click.Context) -> None:
    """Show or schedule today's focus tasks."""
    if ctx.invoked_subcommand is not None:
        return
    cfg = load_config(ctx.obj["config_dir"])
    _, _, _, today_service = _task_services(cfg)
    date, items = today_service.list_today()
    click.echo(f"Today: {date}")
    click.echo("")
    if not items:
        click.echo("No tasks scheduled for today.")
        return
    click.echo(f"{'Priority':8} {'Loop':12} {'Status':10} Title")
    for item in items:
        click.echo(f"{item.priority:<8} {item.loop_type:12} {item.status:10} {item.title}")


@today.command("add")
@click.argument("inbox_id")
@click.option("--loop", "loop_type", default=None)
@click.option("--priority", default=None, type=int)
@click.pass_context
def today_add_inbox(
    ctx: click.Context,
    inbox_id: str,
    loop_type: str | None,
    priority: int | None,
) -> None:
    """Promote inbox item to queue and schedule for today."""
    cfg = load_config(ctx.obj["config_dir"])
    _, _, _, today_service = _task_services(cfg)
    try:
        item = today_service.add_inbox_to_today(inbox_id, loop_type=loop_type, priority=priority)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Scheduled for today: {item.id} ({item.title})")


@today.command("add-queue")
@click.argument("queue_id")
@click.pass_context
def today_add_queue(ctx: click.Context, queue_id: str) -> None:
    """Schedule an existing queue item for today."""
    cfg = load_config(ctx.obj["config_dir"])
    _, _, _, today_service = _task_services(cfg)
    try:
        item = today_service.add_queue_to_today(queue_id)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Scheduled for today: {item.id} ({item.title})")
