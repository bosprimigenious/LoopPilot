"""Deterministic Markdown report renderer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loop_pilot.domain.models import RunRecord, rfc3339


class ReportRenderer:
    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or Path("templates")

    def render(
        self,
        template_name: str,
        record: RunRecord,
        body: dict[str, Any],
        manifest_rel_path: str,
    ) -> str:
        template_path = self._resolve_template(template_name)
        template = template_path.read_text(encoding="utf-8") if template_path.exists() else self._fallback_template()

        front_matter = self._front_matter(record, manifest_rel_path)
        rendered_body = self._render_body(template, body, record)
        return f"{front_matter}\n\n{rendered_body}"

    def write_report(
        self,
        output_path: Path,
        template_name: str,
        record: RunRecord,
        body: dict[str, Any],
        manifest_rel_path: str,
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.render(template_name, record, body, manifest_rel_path)
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def _resolve_template(self, template_name: str) -> Path:
        candidates = [
            self.templates_dir / template_name,
            self.templates_dir / f"{template_name}.md",
        ]
        for path in candidates:
            if path.exists():
                return path
        return Path("__missing__")

    def _front_matter(self, record: RunRecord, manifest_rel_path: str) -> str:
        outcome = record.outcome.value if record.outcome else "unknown"
        return (
            "---\n"
            f'schema_version: "1.0"\n'
            f"run_id: {record.run_id}\n"
            f"loop_type: {record.loop_type}\n"
            f"terminal_state: {outcome}\n"
            f"generated_at: {rfc3339()}\n"
            f"artifact_manifest: {manifest_rel_path}\n"
            "---"
        )

    def _render_body(self, template: str, body: dict[str, Any], record: RunRecord) -> str:
        text = template
        replacements = {
            "{{run_id}}": record.run_id,
            "{{outcome}}": record.outcome.value if record.outcome else "unknown",
            "{{terminal_reason}}": record.terminal_reason or "未执行/未知",
            "{{rounds}}": str(record.current_round),
        }
        for key, value in body.items():
            replacements[f"{{{{{key}}}}}"] = str(value)
        for token, value in replacements.items():
            text = text.replace(token, value)
        return text

    def _fallback_template(self) -> str:
        return (
            "# LoopPilot Report\n\n"
            "Run: {{run_id}}\n\n"
            "Outcome: {{outcome}}\n\n"
            "Reason: {{terminal_reason}}\n"
        )

    def render_daily_summary(self, runs: list[RunRecord], sections: list[str]) -> str:
        lines = [
            "---",
            'schema_version: "1.0"',
            f"generated_at: {rfc3339()}",
            "loop_type: daily_summary",
            "terminal_state: completed",
            "artifact_manifest: manifests/daily-summary.json",
            "---",
            "",
            "# Daily Summary",
            "",
        ]
        for record in runs:
            outcome = record.outcome.value if record.outcome else "unknown"
            lines.append(f"- **{record.loop_type}** (`{record.run_id}`): {outcome}")
        lines.append("")
        lines.extend(sections)
        return "\n".join(lines)
