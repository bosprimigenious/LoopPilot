"""LoopPilot CLI — Mini + Practical MVP command surface."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from loop_pilot.adapters.doctor import diagnose_adapters
from loop_pilot.adapters.factory import list_adapters
from loop_pilot.adapters.registry import is_real_adapter_kind
from loop_pilot.app import App
from loop_pilot.cli_db import db
from loop_pilot.config import load_config
from loop_pilot.domain.models import RunRequest
from loop_pilot.runtime.recovery_scan import scan_recovery
from loop_pilot.runtime.run_ids import new_run_id
from loop_pilot.storage.db_ops import sqlite_doctor_checks


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
        except Exception as exc:
            issues.append(str(exc))

    fixture_roots = [
        Path("tests/fixtures/intern/simple_python_bug"),
        Path("tests/fixtures/paper/unsupported_claim"),
        Path("tests/fixtures/daily_news/github_star_snapshots"),
    ]
    demo_roots = [
        Path("examples/intern_demo"),
        Path("examples/paper_demo"),
        Path("examples/daily_news_demo/items.json"),
    ]
    for path in fixture_roots + demo_roots:
        if not path.exists():
            issues.append(f"Missing path: {path}")

    if issues:
        click.echo("Doctor: FAIL")
        for issue in issues:
            click.echo(f"  - {issue}")
        sys.exit(1)

    cfg = load_config(config_dir)
    backend = str(cfg.runtime.get("state_backend", "json")).lower()
    if backend == "sqlite":
        sqlite_issues = sqlite_doctor_checks(cfg.sqlite_path, cfg.lock_dir)
        hard_failures = [item for item in sqlite_issues if not item.startswith("Warning:")]
        warnings.extend(item.replace("Warning: ", "") for item in sqlite_issues if item.startswith("Warning:"))
        if hard_failures:
            click.echo("Doctor: FAIL")
            for issue in hard_failures:
                click.echo(f"  - {issue}")
            sys.exit(1)
    else:
        warnings.append("state_backend=json (0.4 db commands require sqlite)")

    click.echo("Doctor: OK")
    click.echo("  Config loaded")
    click.echo("  Fixtures and demo workspaces present")
    click.echo("  State directories ready")
    click.echo("  MockAdapter default (allow_real_adapters=false)")
    for warning in warnings:
        click.echo(f"  Warning: {warning}")


@app.group()
@click.pass_context
def adapters(ctx: click.Context) -> None:
    """Inspect configured adapters."""
    ctx.ensure_object(dict)


@adapters.command("list")
@click.pass_context
def adapters_list(ctx: click.Context) -> None:
    """List mock and configured real adapters."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    allow_real = cfg.allow_real_adapters
    for entry in list_adapters(cfg.models):
        adapter_id = str(entry["id"])
        kind = str(entry["kind"])
        is_real = is_real_adapter_kind(kind)
        if is_real and not allow_real:
            state = "disabled (allow_real_adapters=false)"
        elif is_real:
            state = "enabled (real)"
        else:
            state = "enabled (mock)"
        click.echo(f"{adapter_id:24} {kind:18} {state}")


@adapters.command("doctor")
@click.option("--verbose", is_flag=True, default=False, help="Show blocked reason details per adapter")
@click.pass_context
def adapters_doctor(ctx: click.Context, verbose: bool) -> None:
    """Check adapter readiness (mock OK; real adapters WARN/BLOCKED)."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    diagnoses = diagnose_adapters(cfg.models, allow_real_adapters=cfg.allow_real_adapters)
    has_blocked = False
    expected_gate = not cfg.allow_real_adapters
    for item in diagnoses:
        click.echo(f"{item.adapter_id:24} {item.status:8} {item.message}")
        if verbose and item.status in {"blocked", "warn"}:
            click.echo(f"  blocked_reason: {item.message}")
        if item.status == "blocked" and not (
            expected_gate and "allow_real_adapters=false" in item.message
        ):
            has_blocked = True
    if has_blocked:
        sys.exit(1)
    if expected_gate:
        click.echo("Adapters doctor: OK (real adapters blocked by default)")
    else:
        click.echo("Adapters doctor: OK")


@app.group()
def run() -> None:
    """Run a Loop."""


@run.command("intern")
@click.option("--fixture", default=None, help="0.1 fixture name (default: simple_python_bug)")
@click.option("--workspace", default=None, help="Demo workspace id or path")
@click.option("--adapter", "adapter_override", default=None, help="Adapter id override (e.g. cursor_cli)")
@click.option("--allow-real-adapters", is_flag=True, default=False, help="Opt-in real adapters for this run")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--review-only", is_flag=True, default=False, help="Read-only analysis; no writes")
@click.pass_context
def run_intern(
    ctx: click.Context,
    fixture: str | None,
    workspace: str | None,
    adapter_override: str | None,
    allow_real_adapters: bool,
    dry_run: bool,
    review_only: bool,
) -> None:
    if workspace and fixture:
        raise click.ClickException("Use either --workspace or --fixture, not both")
    _run_single(
        ctx,
        "intern",
        fixture=fixture or (None if workspace else "simple_python_bug"),
        workspace=workspace,
        adapter_override=adapter_override,
        allow_real_adapters=allow_real_adapters or None,
        dry_run=dry_run,
        review_only=review_only,
    )


@run.command("paper")
@click.option("--fixture", default=None, help="0.1 fixture name (default: unsupported_claim)")
@click.option("--workspace", default=None, help="Demo workspace id or path")
@click.option("--adapter", "adapter_override", default=None, help="Adapter id override (e.g. deepseek)")
@click.option("--allow-real-adapters", is_flag=True, default=False, help="Opt-in real adapters for this run")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--review-only", is_flag=True, default=False, help="Read-only analysis; no writes")
@click.pass_context
def run_paper(
    ctx: click.Context,
    fixture: str | None,
    workspace: str | None,
    adapter_override: str | None,
    allow_real_adapters: bool,
    dry_run: bool,
    review_only: bool,
) -> None:
    if workspace and fixture:
        raise click.ClickException("Use either --workspace or --fixture, not both")
    _run_single(
        ctx,
        "paper",
        fixture=fixture or (None if workspace else "unsupported_claim"),
        workspace=workspace,
        adapter_override=adapter_override,
        allow_real_adapters=allow_real_adapters or None,
        dry_run=dry_run,
        review_only=review_only,
    )


@run.command("daily-news")
@click.option("--fixture", default=None, help="0.1 fixture name (default: github_star_snapshots)")
@click.option("--source-profile", default=None, help="Configured local source profile (e.g. demo)")
@click.option("--adapter", "adapter_override", default=None, help="Adapter id override")
@click.option("--allow-real-adapters", is_flag=True, default=False, help="Opt-in real adapters for this run")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--review-only", is_flag=True, default=False, help="Read-only analysis")
@click.pass_context
def run_daily_news(
    ctx: click.Context,
    fixture: str | None,
    source_profile: str | None,
    adapter_override: str | None,
    allow_real_adapters: bool,
    dry_run: bool,
    review_only: bool,
) -> None:
    if source_profile and fixture:
        raise click.ClickException("Use either --source-profile or --fixture, not both")
    _run_single(
        ctx,
        "daily_news",
        fixture=fixture or (None if source_profile else "github_star_snapshots"),
        source_profile=source_profile,
        adapter_override=adapter_override,
        allow_real_adapters=allow_real_adapters or None,
        dry_run=dry_run,
        review_only=review_only,
    )


@run.command("all")
@click.option("--fixture-set", default="mini", help="0.1 fixture bundle (default: mini)")
@click.option("--profile", default=None, help="Practical MVP profile (e.g. demo)")
@click.option("--dry-run", is_flag=True, default=False)
@click.pass_context
def run_all(ctx: click.Context, fixture_set: str, profile: str | None, dry_run: bool) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    results = application.orchestrator.run_all(
        fixture_set=fixture_set,
        profile=profile,
        dry_run=dry_run,
    )
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


def _get_app(config_dir: Path) -> App:
    if not config_dir.exists():
        raise click.ClickException(f"Config directory not found: {config_dir}")
    return App.from_config_dir(config_dir)


def _run_single(
    ctx: click.Context,
    loop_type: str,
    *,
    fixture: str | None,
    workspace: str | None = None,
    source_profile: str | None = None,
    adapter_override: str | None = None,
    allow_real_adapters: bool | None = None,
    dry_run: bool,
    review_only: bool = False,
) -> None:
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    request = RunRequest(
        run_id=new_run_id(loop_type),
        loop_type=loop_type,
        fixture=fixture,
        workspace=workspace,
        source_profile=source_profile,
        adapter_override=adapter_override,
        allow_real_adapters=allow_real_adapters,
        review_only=review_only,
        dry_run=dry_run,
        config_snapshot_hash=application.config.snapshot_hash(),
    )
    record = application.orchestrator.run_loop(request)
    outcome = record.outcome.value if record.outcome else "unknown"
    click.echo(f"Run {record.run_id} completed: {outcome}")
    if record.terminal_reason:
        click.echo(f"Reason: {record.terminal_reason}")


app.add_command(db)


@app.command("recovery-scan")
@click.pass_context
def recovery_scan(ctx: click.Context) -> None:
    """Scan for stale, interrupted, and blocked runs."""
    config_dir: Path = ctx.obj["config_dir"]
    application = _get_app(config_dir)
    backend = str(application.config.runtime.get("state_backend", "json")).lower()

    if backend != "sqlite":
        click.echo("recovery-scan requires runtime.state_backend=sqlite")
        sys.exit(1)

    findings = scan_recovery(
        application.state_store,
        lock_dir=application.config.lock_dir,
    )
    if not findings:
        click.echo("Recovery scan: OK (no issues)")
        return

    click.echo(f"Recovery scan: {len(findings)} finding(s)")
    for item in findings:
        outcome = item.outcome or "-"
        click.echo(
            f"  {item.run_id}  {item.category:20}  {item.phase:18}  "
            f"{outcome:10}  -> {item.recommended_action}"
        )
        click.echo(f"    {item.reason}")


if __name__ == "__main__":
    app()
