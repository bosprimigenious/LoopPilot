"""Database CLI commands for 0.4-a state reliability."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from loop_pilot.config import LoopPilotConfig, load_config
from loop_pilot.storage.db_ops import (
    execute_backup,
    get_db_status,
    migrate_database,
    plan_backup,
    verify_database,
)


def _require_sqlite(cfg: LoopPilotConfig) -> tuple[Path, Path]:
    backend = str(cfg.runtime.get("state_backend", "json")).lower()
    if backend != "sqlite":
        raise click.ClickException(
            "db commands require runtime.state_backend=sqlite "
            f"(current: {backend!r}). See docs/development/40-personal-daily-loop-0.4-spec.md"
        )
    return cfg.sqlite_path, cfg.lock_dir


@click.group()
def db() -> None:
    """SQLite state management (requires state_backend=sqlite)."""


@db.command("status")
@click.pass_context
def db_status(ctx: click.Context) -> None:
    """Show backend, schema version, run counts, and lock state."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    status = get_db_status(
        backend=str(cfg.runtime.get("state_backend", "json")).lower(),
        db_path=cfg.sqlite_path if str(cfg.runtime.get("state_backend", "json")).lower() == "sqlite" else None,
        lock_dir=cfg.lock_dir,
    )

    click.echo(f"backend: {status.backend}")
    if status.backend != "sqlite":
        click.echo("sqlite: not configured (0.1 json backend)")
        click.echo(f"lock_dir: {status.lock_dir}")
        if status.lock_files:
            click.echo(f"locks: {', '.join(status.lock_files)}")
        else:
            click.echo("locks: none")
        return

    click.echo(f"sqlite_path: {status.db_path}")
    click.echo(f"exists: {status.exists}")
    click.echo(f"schema_version: {status.schema_version}")
    click.echo(f"target_schema_version: {status.target_schema_version}")
    if status.pending_migrations:
        click.echo(f"pending_migrations: {', '.join(str(v) for v in status.pending_migrations)}")
    else:
        click.echo("pending_migrations: none")
    click.echo(f"run_count: {status.run_count}")
    click.echo(f"active_run_count: {status.active_run_count}")
    click.echo(f"lock_dir: {status.lock_dir}")
    if status.lock_files:
        click.echo(f"locks: {', '.join(status.lock_files)}")
    else:
        click.echo("locks: none")


@db.command("migrate")
@click.option("--dry-run", is_flag=True, default=False, help="Preview pending migrations")
@click.pass_context
def db_migrate(ctx: click.Context, dry_run: bool) -> None:
    """Apply or preview SQLite schema migrations."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    db_path, _ = _require_sqlite(cfg)

    applied = migrate_database(db_path, dry_run=dry_run)
    if dry_run:
        if applied:
            click.echo(f"Would apply migrations: {', '.join(str(v) for v in applied)}")
        else:
            click.echo("No pending migrations")
        return

    if applied:
        click.echo(f"Applied migrations: {', '.join(str(v) for v in applied)}")
    else:
        click.echo("Database schema up to date")


@db.command("backup")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--dest", type=click.Path(path_type=Path), default=None, help="Backup root directory")
@click.pass_context
def db_backup(ctx: click.Context, dry_run: bool, dest: Path | None) -> None:
    """Back up SQLite database, state dir, and config."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    db_path, _ = _require_sqlite(cfg)

    backup_dir = dest or Path(cfg.runtime.get("backup_dir", "var/backups"))
    plan = plan_backup(
        db_path=db_path,
        state_dir=cfg.state_dir,
        config_dir=config_dir,
        backup_dir=backup_dir,
        dry_run=dry_run,
    )

    if not plan.sources:
        click.echo("Nothing to back up (database and directories missing)")
        return

    prefix = "Would back up" if dry_run else "Backed up"
    for source, destination in plan.sources:
        click.echo(f"{prefix}: {source} -> {destination}")

    if not dry_run:
        execute_backup(plan)
        click.echo(f"Backup complete: {plan.sources[0][1].parent}")


@db.command("verify")
@click.pass_context
def db_verify(ctx: click.Context) -> None:
    """Verify SQLite integrity and artifact consistency."""
    config_dir: Path = ctx.obj["config_dir"]
    cfg = load_config(config_dir)
    db_path, _ = _require_sqlite(cfg)

    report = verify_database(db_path, cfg.artifact_dir)
    if not report.issues:
        click.echo("Verify: OK")
        return

    for issue in report.issues:
        click.echo(f"{issue.severity.upper()}: [{issue.code}] {issue.message}")

    if not report.ok:
        sys.exit(1)
    click.echo("Verify: OK (warnings only)")
