"""Render daily and weekly summary Markdown."""

from __future__ import annotations

from loop_pilot.domain.models import rfc3339
from loop_pilot.summary.models import DailySummaryData, WeeklySummaryData


def render_daily_summary(data: DailySummaryData) -> str:
    lines = [
        "# Daily Summary",
        "",
        f"Date: {data.date}",
        f"Timezone: {data.timezone}",
        f"Generated: {rfc3339()}",
        "",
        "## 1. 今日最重要结论",
        "",
    ]
    if data.highlights:
        lines.extend(f"- {item}" for item in data.highlights)
    else:
        lines.append("- 无")

    lines.extend(["", "## 2. Today", ""])
    if data.today_items:
        lines.append("| Priority | Loop | Status | Title |")
        lines.append("|---|---|---|---|")
        for item in data.today_items:
            lines.append(
                f"| {item.priority} | {item.loop_type} | {item.status} | {item.title} |"
            )
    else:
        lines.append("_No tasks scheduled for today._")

    lines.extend(["", "## 3. Runs", ""])
    if data.runs:
        lines.append("| Run | Loop | Outcome | Gate | Report |")
        lines.append("|---|---|---|---|---|")
        for row in data.runs:
            report = row.report_path or "-"
            gate = row.gate or "-"
            outcome = row.outcome or row.phase
            lines.append(f"| {row.run_id} | {row.loop_type} | {outcome} | {gate} | {report} |")
    else:
        lines.append("_No runs recorded today._")

    lines.extend(["", "## 4. Needs Review", ""])
    if data.needs_review:
        lines.append("| Run | Loop | Reason | Suggested Command |")
        lines.append("|---|---|---|---|")
        for row in data.needs_review:
            lines.append(
                f"| {row.run_id} | {row.loop_type} | {row.reason} | `{row.suggested_command}` |"
            )
    else:
        lines.append("_None._")

    lines.extend(["", "## 5. Inbox Updates", ""])
    manual_new = [item for item in data.inbox_new if item.source not in {"daily-news", "daily_news"}]
    if data.inbox_daily_news:
        lines.append(f"- DailyNews candidate tasks: {len(data.inbox_daily_news)}")
    if manual_new:
        lines.append(f"- Manual / other new tasks: {len(manual_new)}")
    if not data.inbox_new:
        lines.append("- 无新增")

    lines.extend(["", "## 6. Blocked", ""])
    if data.blocked:
        for row in data.blocked:
            lines.append(f"- `{row.run_id}` ({row.loop_type}): {row.reason}")
    else:
        lines.append("- 无")
    if data.recovery_findings:
        lines.append("")
        lines.append("Recovery scan notes:")
        for note in data.recovery_findings[:5]:
            lines.append(f"- {note}")

    lines.extend(["", "## 7. Tomorrow", ""])
    for index, item in enumerate(data.tomorrow, start=1):
        lines.append(f"{index}. {item}")

    lines.append("")
    return "\n".join(lines)


def render_weekly_summary(data: WeeklySummaryData) -> str:
    lines = [
        "# Weekly Summary",
        "",
        f"Week: {data.week}",
        f"Range: {data.start_date} → {data.end_date}",
        f"Generated: {rfc3339()}",
        "",
        "## Highlights",
        "",
    ]
    if data.highlights:
        lines.extend(f"- {item}" for item in data.highlights)
    else:
        lines.append("- 无")

    lines.extend(["", "## Completed", ""])
    if data.completed:
        lines.extend(f"- {item}" for item in data.completed)
    else:
        lines.append("- 无")

    lines.extend(["", "## Needs Review", ""])
    if data.needs_review:
        lines.extend(f"- {item}" for item in data.needs_review)
    else:
        lines.append("- 无")

    lines.extend(["", "## Blocked", ""])
    if data.blocked:
        lines.extend(f"- {item}" for item in data.blocked)
    else:
        lines.append("- 无")

    lines.extend(["", "## Loop Statistics", ""])
    if data.loop_stats:
        lines.append("| Loop | Runs | Succeeded | Blocked |")
        lines.append("|---|---|---|---|")
        for loop_type, stats in sorted(data.loop_stats.items()):
            lines.append(
                f"| {loop_type} | {stats.get('runs', 0)} | "
                f"{stats.get('succeeded', 0)} | {stats.get('blocked', 0)} |"
            )
    else:
        lines.append("_No runs this week._")

    lines.extend(["", "## Recommended Next Week", ""])
    for index, item in enumerate(data.recommended, start=1):
        lines.append(f"{index}. {item}")

    if data.daily_paths:
        lines.extend(["", "## Daily Summary Links", ""])
        for path in data.daily_paths:
            lines.append(f"- {path}")

    lines.append("")
    return "\n".join(lines)


def render_schedule_preview(
    *,
    target: str,
    command: str,
    schedule_time: str,
    cwd: str,
) -> str:
    return "\n".join(
        [
            "# Schedule Preview",
            "",
            "## Target",
            "",
            target,
            "",
            "## Command",
            "",
            command,
            "",
            "## Time",
            "",
            f"{schedule_time} every day",
            "",
            "## Working Directory",
            "",
            cwd,
            "",
            "## Safety",
            "",
            "- dry-run enabled",
            "- no auto approve",
            "- no real adapter by default",
            "- no write unless explicitly enabled",
            "- schedule install --yes deferred to 0.5",
            "",
        ]
    )
