"""Daily summary report rendering."""

from __future__ import annotations

from loop_pilot.domain.models import RunRecord, rfc3339
from loop_pilot.reporting.renderer import ReportRenderer


def render_daily_summary(renderer: ReportRenderer, runs: list[RunRecord], sections: list[str]) -> str:
    return renderer.render_daily_summary(runs, sections)


def summary_front_matter() -> dict[str, str]:
    return {
        "schema_version": "1.0",
        "generated_at": rfc3339(),
        "loop_type": "daily_summary",
        "terminal_state": "completed",
        "artifact_manifest": "manifests/daily-summary.json",
    }
