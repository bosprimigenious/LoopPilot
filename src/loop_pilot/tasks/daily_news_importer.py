"""Import DailyNews candidate-actions.json into Inbox."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from loop_pilot.tasks.inbox_service import InboxService


@dataclass
class ImportResult:
    imported: list[str] = field(default_factory=list)
    skipped_duplicates: list[str] = field(default_factory=list)
    preview: list[dict[str, str]] = field(default_factory=list)
    dry_run: bool = False


class DailyNewsImporter:
    PRIORITY_MAP = {"high": 2, "normal": 3, "low": 4}

    def __init__(self, inbox_service: InboxService) -> None:
        self.inbox = inbox_service

    def import_from_file(self, path: Path, *, dry_run: bool = False) -> ImportResult:
        if not path.exists():
            raise FileNotFoundError(f"candidate-actions file not found: {path}")

        payload = json.loads(path.read_text(encoding="utf-8"))
        candidates = payload.get("candidates", [])
        if not isinstance(candidates, list):
            raise ValueError("candidate-actions.json must contain a candidates list")

        source_ref = str(path.parent.name)
        result = ImportResult(dry_run=dry_run)

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            normalized = self._normalize_candidate(candidate, source_ref=source_ref)
            dedupe_key = normalized["dedupe_key"]

            if self.inbox.store.inbox_dedupe_exists(dedupe_key):
                result.skipped_duplicates.append(dedupe_key)
                continue

            if dry_run:
                result.preview.append(normalized)
                result.imported.append(normalized["title"])
                continue

            add_result = self.inbox.add(
                normalized["title"],
                body=normalized["body"],
                source="daily-news",
                source_ref=normalized["source_ref"],
                loop_hint=normalized["loop_hint"],
                priority=normalized["priority"],
                dedupe_key=dedupe_key,
            )
            if add_result.created:
                result.imported.append(add_result.item.id)
                self.inbox.store.record_event(
                    entity_type="inbox",
                    entity_id=add_result.item.id,
                    event_type="daily_news_imported",
                    payload={
                        "source_ref": source_ref,
                        "dedupe_key": dedupe_key,
                        "from": str(path),
                    },
                )
            else:
                result.skipped_duplicates.append(dedupe_key)

        return result

    def _normalize_candidate(self, candidate: dict, *, source_ref: str) -> dict[str, str | int]:
        target_loop = str(candidate.get("target_loop", "intern"))
        if target_loop == "daily_news":
            target_loop = "daily-news"
        source_item_id = str(candidate.get("source_item_id", "unknown"))
        recommended = str(candidate.get("recommended_action", "review"))
        priority_label = str(candidate.get("priority", "normal"))
        priority = self.PRIORITY_MAP.get(priority_label, 3)

        title = str(candidate.get("title") or f"{recommended}: {source_item_id}")
        body = json.dumps(candidate, sort_keys=True, ensure_ascii=False)
        dedupe_key = hashlib.sha256(
            f"daily-news:{source_ref}:{source_item_id}:{target_loop}".encode()
        ).hexdigest()

        return {
            "title": title,
            "body": body,
            "source_ref": source_item_id,
            "loop_hint": target_loop if target_loop in {"intern", "paper", "daily-news"} else "unknown",
            "priority": priority,
            "dedupe_key": dedupe_key,
        }
