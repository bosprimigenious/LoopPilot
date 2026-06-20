"""Golden assertion loader for fixtures."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_assertions(fixture_path: Path) -> dict:
    path = fixture_path / "assertions.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def test_intern_simple_python_bug_golden() -> None:
    assertions = load_assertions(Path("tests/fixtures/intern/simple_python_bug"))
    assert assertions["must"][0]["outcome"] == "succeeded"
    assert assertions["must_not"][0]["modify_forbidden_paths"] is True


def test_daily_news_golden_no_false_winner() -> None:
    assertions = load_assertions(Path("tests/fixtures/daily_news/github_star_snapshots"))
    assert assertions["must"][0]["day1_no_24h_winner_claim"] is True
    assert assertions["must"][1]["day2_correct_delta"] is True


def test_paper_no_fake_citation_golden() -> None:
    assertions = load_assertions(Path("tests/fixtures/paper/unsupported_claim"))
    assert assertions["must"][0]["no_fabricated_citation"] is True


def test_fixtures_contain_no_secret_patterns() -> None:
    forbidden = ("password:", "api_key:", "BEGIN RSA", "foxmail.com")
    root = Path("tests/fixtures")
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".md", ".yaml", ".json", ".bib"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                assert token not in text, f"{token} found in {path}"
