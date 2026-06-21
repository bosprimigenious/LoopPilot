"""Connectors for github, arxiv, and rss sources (offline fixture mode in 0.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loop_pilot.connectors.local_json import fetch_source as fetch_local_json


def fetch_github(source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(source_cfg["path"])
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    repos = data.get("repositories") or data.get("items") or []
    for item in repos:
        item.setdefault("category", "github")
        item.setdefault("source_id", source_cfg.get("id", "github"))
    return repos


def fetch_arxiv(source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(source_cfg["path"])
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    papers = data.get("papers") or data.get("items") or [data]
    for item in papers:
        item.setdefault("category", "paper")
        item.setdefault("source_id", source_cfg.get("id", "arxiv"))
    return papers


def fetch_rss(source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    return fetch_local_json({**source_cfg, "kind": "local_json"})


def fetch_source(source_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    kind = str(source_cfg.get("kind", "local_json")).lower()
    if kind == "local_json":
        return fetch_local_json(source_cfg)
    if kind == "github":
        return fetch_github(source_cfg)
    if kind == "arxiv":
        return fetch_arxiv(source_cfg)
    if kind == "rss":
        return fetch_rss(source_cfg)
    raise ValueError(f"Unsupported source kind: {kind}")
