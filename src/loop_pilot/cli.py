"""LoopPilot CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from loop_pilot.app import App
from loop_pilot.config import load_config
from loop_pilot.domain.models import RunRequest
from loop_pilot.runtime.approvals import ApprovalError, approve_run, cancel_run, reject_run
from loop_pilot.runtime.orchestrator import ResumeError
from loop_pilot.runtime.run_ids import new_run_id


def _require_sqlite_backend(config_dir: Path) -> App:
    if not config_dir.exists():
        raise click.ClickException(f"Config directory not found: {config_dir}")
    config = load_config(config_dir)
    backend = str(config.runtime.get("state_backend", "json")).lower()
    if backend != "sqlite":
        raise click.ClickException(
            "V1 commands require state_backend=sqlite in loop-pilot.yaml"
        )
    return App.from_config_dir(config_dir)


@click.group()
@click.option("--config-dir", default="config", type=click.Path(exists=False, path_type=Path))
@click.pass_context
def app(ctx: click.Context, config_dir: Path) -> None:
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config_dir


@app.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check configuration and runtime health."""
    config_dir: Path = ctx.obj["config_dir"]
    issues: list[str] = []
    warnings: list[str] = []

    if not config_dir.exists():
        issues.append(f"Config directory missing: {config_dir}")
    else:
        try:
            cfg = load_config(config_dir)
            for sub in (cfg.state_dir, cfg.artifact_dir):
                sub.mkdir(parents=True, exist_ok=True)
            if cfg.allow_real_adapters:
                warnings.append("runtime.allow_real_adapters=true (Mini defaults to false)")
            backend = str(cfg.runtime.get("state_backend", "json")).lower()
            if backend == "sqlite":
                warnings.append("state_backend=sqlite (V1 recovery commands enabled)")
        except Exception as exc:
            issues.append(str(exc))

    fixture_roots = [
        Path("tests/fixtures/intern/simple_python_bug"),
        Path("tests/fixtures/paper/unsupported_claim"),
        Path("tests/fixtures/daily_news/github_star_snapshots"),
    ]
    for path in fixture_roots:
        if not path.exists():
            issues.append(f"Missing fixture: {path}")

    if issues:
        click.echo("Doctor: FAIL")
        for issue in issues:
            click.echo(f"  - {issue}")
        sys.exit(1)

    click.echo("Doctor: OK")
    click.echo("  Config loaded")
    click.echo("  Fixtures present")
    click.echo("  State directories ready")
    click.echo("  MockAdapter default (allow_real_adapters=false)")
    for warning in warnings:
        click.echo(f"  Warning: {warning}")


@app.group()
def run() -> None:
    """Run a Loop."""


@run.command("intern")
@click.option("--fixture", default="simple_python_bug")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def run_intern(ctx: click.Context, fixture: str, dry_run: bool) -> None:
    _run_single(ctx, "intern", fixture, dry_run)


@run.command("paper")
@click.option("--fixture", default="unsupported_claim")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def run_paper(ctx: click.Context, fixture: str, dry_run: bool) -> None:
    _run_single(ctx, "paper", fixture, dry_run)


@run.command("daily-news")
@click.option("--fixture", default="github_star_snapshots")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def run_daily_news(ctx: click.Context, fixture: str, dry_run: bool) -> None:
    _run_single(ctx, "daily_news", fixture, dry_run)


@run.command("all")
@click.option("--fixture-set", default="mini")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def run_all(ctx: click.Context, fixture_set: str, dry_run: bool) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    results = application.orchestrator.run_all(fixture_set=fixture_set, dry_run=dry_run)
    for record in results:
        outcome = record.outcome.value if record.outcome else "unknown"
        click.echo(f"{record.loop_type}: {outcome} ({record.run_id})")


@app.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show recent runs."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    runs = application.state_store.list_runs(limit=10)
    if not runs:
        click.echo("No runs found.")
        return
    for record in runs:
        outcome = record.outcome.value if record.outcome else "in_progress"
        click.echo(f"{record.run_id}  {record.loop_type:12}  {record.phase.value:12}  {outcome}")


@app.command()
@click.argument("run_id")
@click.pass_context
def inspect(ctx: click.Context, run_id: str) -> None:
    """Inspect a run by ID."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    record = application.state_store.get_run(run_id)
    if record is None:
        click.echo(f"Run not found: {run_id}", err=True)
        sys.exit(1)
    click.echo(json.dumps(record.to_dict(), indent=2))


@app.command()
@click.argument("run_id")
@click.pass_context
def resume(ctx: click.Context, run_id: str) -> None:
    """Resume a run from the latest legal checkpoint (V1 / SQLite)."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _require_sqlite_backend(config_dir)
    try:
        record = application.orchestrator.resume_run(run_id)
    except ResumeError as exc:
        raise click.ClickException(exc.message) from exc
    outcome = record.outcome.value if record.outcome else "unknown"
    click.echo(f"resumed from checkpoint: {record.run_id} {outcome}")


@app.command()
@click.argument("run_id")
@click.pass_context
def approve(ctx: click.Context, run_id: str) -> None:
    """Approve a run waiting for human review (V1 / SQLite)."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _require_sqlite_backend(config_dir)
    try:
        record = approve_run(application.state_store, run_id)
    except ApprovalError as exc:
        raise click.ClickException(exc.message) from exc
    click.echo(f"approved: {record.run_id}")


@app.command()
@click.argument("run_id")
@click.option("--reason", required=True)
@click.pass_context
def reject(ctx: click.Context, run_id: str, reason: str) -> None:
    """Reject a run waiting for human review (V1 / SQLite)."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _require_sqlite_backend(config_dir)
    try:
        record = reject_run(application.state_store, run_id, reason)
    except ApprovalError as exc:
        raise click.ClickException(exc.message) from exc
    click.echo(f"rejected: {record.run_id}")


@app.command()
@click.argument("run_id")
@click.option("--reason", default="Cancelled by user")
@click.pass_context
def cancel(ctx: click.Context, run_id: str, reason: str) -> None:
    """Cancel an in-progress or waiting run (V1 / SQLite)."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _require_sqlite_backend(config_dir)
    try:
        record = cancel_run(application.state_store, run_id, reason)
    except ApprovalError as exc:
        raise click.ClickException(exc.message) from exc
    click.echo(f"cancelled: {record.run_id}")


@app.command()
@click.argument("run_id")
@click.pass_context
def report(ctx: click.Context, run_id: str) -> None:
    """Show run summary and report status (V1 / SQLite)."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _require_sqlite_backend(config_dir)
    record = application.state_store.get_run(run_id)
    if record is None:
        raise click.ClickException(f"Run not found: {run_id}")
    outcome = record.outcome.value if record.outcome else "in_progress"
    click.echo(f"Run: {record.run_id}")
    click.echo(f"Loop: {record.loop_type}")
    click.echo(f"Phase: {record.phase.value}")
    click.echo(f"Outcome: {outcome}")
    click.echo(f"Report status: {record.report_status}")
    if record.terminal_reason:
        click.echo(f"Reason: {record.terminal_reason}")
    plan = application.orchestrator.recovery_plan(run_id)
    if plan is not None:
        click.echo(f"Can resume: {plan.can_resume} ({plan.reason})")


def _get_app(config_dir: Path) -> App:
    if not config_dir.exists():
        raise click.ClickException(f"Config directory not found: {config_dir}")
    return App.from_config_dir(config_dir)


def _run_single(ctx: click.Context, loop_type: str, fixture: str, dry_run: bool) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    request = RunRequest(
        run_id=new_run_id(loop_type),
        loop_type=loop_type,
        fixture=fixture,
        dry_run=dry_run,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    outcome = record.outcome.value if record.outcome else "unknown"
    click.echo(f"Run {record.run_id} completed: {outcome}")
    if record.terminal_reason:
        click.echo(f"Reason: {record.terminal_reason}")


if __name__ == "__main__":
    app()
