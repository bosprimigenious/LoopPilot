"""Safety CLI (0.5-a)."""

from __future__ import annotations

import json

import click

from loop_pilot.config import load_config
from loop_pilot.safety.gate import SafetyGate
from loop_pilot.safety.policy import SafeAutonomyPolicy


@click.group()
def safety() -> None:
    """SafetyGate policy summary and audit tail."""


@safety.command("doctor")
@click.pass_context
def safety_doctor(ctx: click.Context) -> None:
    cfg = load_config(ctx.obj["config_dir"])
    policy = SafeAutonomyPolicy.from_config(cfg)
    gate = SafetyGate.from_config(cfg)
    click.echo(
        json.dumps(
            {
                "max_level": policy.max_level.value,
                "allow_schedule_install": policy.allow_schedule_install,
                "audit_path": str(gate.audit.path),
                "recent_decisions": gate.audit.list_recent(limit=5),
            },
            indent=2,
        )
    )
