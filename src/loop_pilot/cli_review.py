"""Review CLI commands (0.4-c, sqlite-only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from loop_pilot.app import App
from loop_pilot.config import load_config
from loop_pilot.review.errors import ReviewDecisionError
from loop_pilot.review.service import ReviewService
from loop_pilot.runtime.approvals import ApprovalError
from loop_pilot.runtime.orchestrator import ResumeError


def _require_sqlite(config_dir: Path) -> App:
    if not config_dir.exists():
        raise click.ClickException(f"Config directory not found: {config_dir}")
    cfg = load_config(config_dir)
    backend = str(cfg.runtime.get("state_backend", "json")).lower()
    if backend != "sqlite":
        raise click.ClickException(
            "review commands require runtime.state_backend=sqlite "
            f"(current: {backend!r})"
        )
    return App.from_config_dir(config_dir)


def _review_service(config_dir: Path) -> ReviewService:
    app = _require_sqlite(config_dir)
    return ReviewService(
        config=app.config,
        state_store=app.state_store,
        orchestrator=app.orchestrator,
    )


@click.group()
@click.pass_context
def review(ctx: click.Context) -> None:
    """List and inspect runs waiting for human review (requires state_backend=sqlite)."""


@review.command("list")
@click.pass_context
def review_list(ctx: click.Context) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    service = _review_service(config_dir)
    rows = service.list_pending()
    if not rows:
        click.echo("No pending review items.")
        return
    for item, record in rows:
        phase = record.phase.value if record else "-"
        outcome = record.outcome.value if record and record.outcome else "-"
        click.echo(f"{item.run_id}  {item.loop_type:12}  {phase:18}  {outcome}")
        if item.artifact_path:
            click.echo(f"  artifacts: {item.artifact_path}")


@review.command("show")
@click.argument("run_id")
@click.pass_context
def review_show(ctx: click.Context, run_id: str) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    service = _review_service(config_dir)
    item, record = service.show(run_id)
    if record is None:
        raise click.ClickException(f"Run not found: {run_id}")
    payload = {
        "run": record.to_dict(),
        "review_item": None if item is None else item.__dict__,
    }
    click.echo(json.dumps(payload, indent=2))


def _handle_review_error(exc: Exception) -> None:
    message = getattr(exc, "message", str(exc))
    raise click.ClickException(message) from exc


@click.command()
@click.argument("run_id")
@click.option("--note", default="", help="Optional approval note")
@click.pass_context
def approve(ctx: click.Context, run_id: str, note: str) -> None:
    """Approve a run pending review (requires runtime.state_backend=sqlite)."""
    try:
        record = _review_service(ctx.obj["config_dir"]).approve(run_id, note)
    except (ApprovalError, ReviewDecisionError, ResumeError) as exc:
        _handle_review_error(exc)
    click.echo(f"Approved {run_id}; review_status={record.review_status}")


@click.command()
@click.argument("run_id")
@click.option("--reason", required=True, help="Rejection reason (required)")
@click.pass_context
def reject(ctx: click.Context, run_id: str, reason: str) -> None:
    """Reject a run pending review (requires runtime.state_backend=sqlite)."""
    try:
        record = _review_service(ctx.obj["config_dir"]).reject(run_id, reason)
    except (ApprovalError, ReviewDecisionError) as exc:
        _handle_review_error(exc)
    click.echo(f"Rejected {run_id}: {record.outcome.value if record.outcome else 'blocked'}")


@click.command()
@click.argument("run_id")
@click.option("--until", required=True, help="Defer until ISO date (YYYY-MM-DD)")
@click.option("--reason", default="", help="Optional defer reason")
@click.pass_context
def defer(ctx: click.Context, run_id: str, until: str, reason: str) -> None:
    """Defer review until a future date (requires runtime.state_backend=sqlite)."""
    try:
        item = _review_service(ctx.obj["config_dir"]).defer(run_id, until, reason)
    except (ApprovalError, ReviewDecisionError) as exc:
        _handle_review_error(exc)
    click.echo(f"Deferred {run_id} until {item.deferred_until}")


@click.command()
@click.argument("run_id")
@click.option("--reason", required=True, help="Cancellation reason")
@click.pass_context
def cancel(ctx: click.Context, run_id: str, reason: str) -> None:
    """Cancel a run and release review queue entry (requires runtime.state_backend=sqlite)."""
    try:
        record = _review_service(ctx.obj["config_dir"]).cancel(run_id, reason)
    except (ApprovalError, ReviewDecisionError) as exc:
        _handle_review_error(exc)
    click.echo(f"Cancelled {run_id}: {record.outcome.value if record.outcome else 'cancelled'}")


@click.command()
@click.argument("run_id")
@click.pass_context
def resume(ctx: click.Context, run_id: str) -> None:
    """Resume an approved or recoverable run (requires runtime.state_backend=sqlite)."""
    try:
        record = _review_service(ctx.obj["config_dir"]).resume(run_id)
    except (ApprovalError, ResumeError) as exc:
        _handle_review_error(exc)
    outcome = record.outcome.value if record.outcome else "in_progress"
    click.echo(f"Resumed {run_id}: {outcome}")


@click.command()
@click.argument("run_id")
@click.pass_context
def report(ctx: click.Context, run_id: str) -> None:
    """Show report path for a run (requires runtime.state_backend=sqlite)."""
    config_dir: Path = ctx.obj["config_dir"]
    app = _require_sqlite(config_dir)
    record = app.state_store.get_run(run_id)
    if record is None:
        raise click.ClickException(f"Run not found: {run_id}")
    from loop_pilot.summary.collector import report_path

    path = report_path(Path(app.config.artifact_dir), record.loop_type, run_id)
    if path is None:
        click.echo(f"No report found for {run_id}", err=True)
        sys.exit(1)
    click.echo(path)
