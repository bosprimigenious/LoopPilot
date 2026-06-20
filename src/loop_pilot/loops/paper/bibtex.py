"""Minimal BibTeX parser and claim-evidence verification for Mini."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class BibEntry:
    key: str
    entry_type: str
    fields: dict[str, str]


def parse_bibtex(content: str) -> dict[str, BibEntry]:
    entries: dict[str, BibEntry] = {}
    pattern = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,([^@]*)", re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(content):
        entry_type, key, body = match.group(1), match.group(2).strip(), match.group(3)
        fields: dict[str, str] = {}
        for field_match in re.finditer(
            r"(\w+)\s*=\s*(\{([^}]*)\}|\"([^\"]*)\"|(\d+))",
            body,
            re.DOTALL,
        ):
            name = field_match.group(1).lower()
            value = field_match.group(3) or field_match.group(4) or field_match.group(5) or ""
            fields[name] = " ".join(value.split())
        entries[key] = BibEntry(key=key, entry_type=entry_type.lower(), fields=fields)
    return entries


def extract_citation_keys_in_text(text: str, known_keys: set[str]) -> list[str]:
    found: list[str] = []
    for key in known_keys:
        if re.search(rf"\({re.escape(key)}\)|\\cite\{{{re.escape(key)}\}}|{re.escape(key)}", text):
            found.append(key)
    return found


def assess_citation_support(claim_text: str, entry: BibEntry) -> str:
    """Return supported | partial | unsupported based on BibTeX content only."""
    blob = " ".join(entry.fields.values()).lower()
    claim = claim_text.lower()

    performance_markers = (
        "outperform",
        "state-of-the-art",
        "every benchmark",
        "significantly",
        "superior",
    )
    is_performance_claim = any(m in claim for m in performance_markers)

    if is_performance_claim:
        support_markers = ("outperform", "baseline", "comparison", "sota", "state-of-the-art", "accuracy", "f1")
        if any(m in blob for m in support_markers):
            return "partial"
        return "unsupported"

    background_markers = ("foundation", "method", "framework", "survey", "overview")
    if any(m in blob for m in background_markers):
        return "partial"
    return "unsupported"
