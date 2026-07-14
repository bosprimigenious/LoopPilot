"""Local API bridge CLI."""

from __future__ import annotations

from pathlib import Path

import click

from loop_pilot.api import serve_api


@click.group()
def api() -> None:
    """Read-only local API bridge for lightweight clients."""


@api.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=7860, show_default=True, type=int)
@click.pass_context
def api_serve(ctx: click.Context, host: str, port: int) -> None:
    """Serve read-only JSON endpoints for the local state store."""
    config_dir: Path = ctx.obj["config_dir"]
    click.echo(f"LoopPilot API bridge listening on http://{host}:{port}")
    click.echo("Read-only endpoints: /api/health /api/summary/today /api/runs /api/reviews")
    serve_api(config_dir=config_dir, host=host, port=port)
