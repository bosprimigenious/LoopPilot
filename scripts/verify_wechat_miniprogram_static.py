#!/usr/bin/env python3
"""Static guard for the LoopPilot WeChat mini program scaffold."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT_ROOT = ROOT / "clients" / "wechat-miniprogram"
REQUIRED_PAGES = {
    "pages/home/home",
    "pages/runs/runs",
    "pages/run-detail/run-detail",
    "pages/review/review",
    "pages/review-detail/review-detail",
    "pages/settings/settings",
}
REQUIRED_API_MARKERS = {
    "/api/health",
    "/api/summary/today",
    "/api/runs",
    "/api/runs/",
    "/api/reviews",
    "/api/reviews/",
}
FORBIDDEN_API_MARKERS = {
    "/approve",
    "/reject",
    'method: "POST"',
    "method: 'POST'",
}


def _check(name: str, fn) -> tuple[str, bool, str]:
    try:
        detail = fn()
    except Exception as exc:  # noqa: BLE001
        return name, False, str(exc)
    return name, True, detail or "PASS"


def _read_app_json() -> dict:
    path = CLIENT_ROOT / "app.json"
    if not path.is_file():
        raise AssertionError("clients/wechat-miniprogram/app.json is missing")
    return json.loads(path.read_text(encoding="utf-8"))


def check_app_json() -> str:
    app = _read_app_json()
    pages = app.get("pages")
    if not isinstance(pages, list):
        raise AssertionError("app.json pages must be a list")
    missing = sorted(REQUIRED_PAGES - set(pages))
    if missing:
        raise AssertionError(f"missing required pages: {', '.join(missing)}")
    return f"{len(pages)} pages"


def check_page_files() -> str:
    app = _read_app_json()
    missing: list[str] = []
    for page in app["pages"]:
        for suffix in (".js", ".json", ".wxml", ".wxss"):
            candidate = CLIENT_ROOT / f"{page}{suffix}"
            if not candidate.is_file():
                missing.append(str(candidate.relative_to(ROOT)))
    if missing:
        raise AssertionError(f"missing page files: {', '.join(missing)}")
    return "page files complete"


def check_tabbar_pages() -> str:
    app = _read_app_json()
    pages = set(app.get("pages", []))
    tab_items = app.get("tabBar", {}).get("list", [])
    if not isinstance(tab_items, list) or not tab_items:
        raise AssertionError("app.json tabBar.list must be a non-empty list")
    unknown = sorted(
        item.get("pagePath", "")
        for item in tab_items
        if item.get("pagePath", "") not in pages
    )
    if unknown:
        raise AssertionError(f"tabBar points to unknown pages: {', '.join(unknown)}")
    return f"{len(tab_items)} tab pages"


def check_api_adapter_is_read_only() -> str:
    path = CLIENT_ROOT / "utils" / "api.js"
    if not path.is_file():
        raise AssertionError("clients/wechat-miniprogram/utils/api.js is missing")
    source = path.read_text(encoding="utf-8")
    missing = sorted(marker for marker in REQUIRED_API_MARKERS if marker not in source)
    if missing:
        raise AssertionError(f"api.js missing endpoint markers: {', '.join(missing)}")
    forbidden = sorted(marker for marker in FORBIDDEN_API_MARKERS if marker in source)
    if forbidden:
        raise AssertionError(f"api.js contains mutation markers: {', '.join(forbidden)}")
    return "read-only API markers"


def check_mock_run_detail_shape() -> str:
    path = CLIENT_ROOT / "utils" / "mock.js"
    if not path.is_file():
        raise AssertionError("clients/wechat-miniprogram/utils/mock.js is missing")
    source = path.read_text(encoding="utf-8")
    for marker in ("reportPath", "artifacts", "humanReadable"):
        if marker not in source:
            raise AssertionError(f"mock.js missing run detail marker: {marker}")
    return "mock detail includes artifact preview"


def check_home_run_detail_navigation() -> str:
    js_path = CLIENT_ROOT / "pages" / "home" / "home.js"
    wxml_path = CLIENT_ROOT / "pages" / "home" / "home.wxml"
    js_source = js_path.read_text(encoding="utf-8")
    wxml_source = wxml_path.read_text(encoding="utf-8")
    for marker in ("openRunDetail", "/pages/run-detail/run-detail", "badgeClass"):
        if marker not in js_source:
            raise AssertionError(f"home.js missing run detail marker: {marker}")
    for marker in ("bindtap=\"openRunDetail\"", "data-run-id", "item.badgeClass"):
        if marker not in wxml_source:
            raise AssertionError(f"home.wxml missing run detail marker: {marker}")
    return "home latest runs link to detail"


def check_settings_health_shape() -> str:
    js_path = CLIENT_ROOT / "pages" / "settings" / "settings.js"
    wxml_path = CLIENT_ROOT / "pages" / "settings" / "settings.wxml"
    js_source = js_path.read_text(encoding="utf-8")
    wxml_source = wxml_path.read_text(encoding="utf-8")
    for marker in (
        "healthRows",
        "endpointRows",
        "normalizeEndpoints",
        "Read-only",
        "Mutations",
        "Methods",
        "Preflight",
        "Endpoints",
    ):
        if marker not in js_source:
            raise AssertionError(f"settings.js missing health marker: {marker}")
    for marker in ("healthRows", "endpointRows", "只读接口", "detail-list"):
        if marker not in wxml_source:
            raise AssertionError(f"settings.wxml missing health marker: {marker}")
    return "settings health detail with endpoint list"


def check_review_detail_run_context() -> str:
    js_path = CLIENT_ROOT / "pages" / "review-detail" / "review-detail.js"
    wxml_path = CLIENT_ROOT / "pages" / "review-detail" / "review-detail.wxml"
    mock_path = CLIENT_ROOT / "utils" / "mock.js"
    js_source = js_path.read_text(encoding="utf-8")
    wxml_source = wxml_path.read_text(encoding="utf-8")
    mock_source = mock_path.read_text(encoding="utf-8")
    for marker in ("runSummary", "normalizeRunSummary", "reportPath"):
        if marker not in js_source:
            raise AssertionError(f"review-detail.js missing run context marker: {marker}")
    for marker in ("关联运行", "review.runSummary", "复制报告路径"):
        if marker not in wxml_source:
            raise AssertionError(f"review-detail.wxml missing run context marker: {marker}")
    if "run: runs.find" not in mock_source:
        raise AssertionError("mock.js missing review run context")
    return "review detail run context"


def check_review_list_run_context() -> str:
    js_path = CLIENT_ROOT / "pages" / "review" / "review.js"
    wxml_path = CLIENT_ROOT / "pages" / "review" / "review.wxml"
    js_source = js_path.read_text(encoding="utf-8")
    wxml_source = wxml_path.read_text(encoding="utf-8")
    for marker in ("runSummary", "normalizeReview", "badgeClass", "reportPath"):
        if marker not in js_source:
            raise AssertionError(f"review.js missing run context marker: {marker}")
    for marker in (
        "item.runSummary",
        "item.runSummary.phase",
        "item.runSummary.badgeClass",
        "item.runSummary.reportPath",
        "复制报告路径",
    ):
        if marker not in wxml_source:
            raise AssertionError(f"review.wxml missing run context marker: {marker}")
    return "review list run context with report copy"


def main() -> int:
    checks = [
        _check("app_json", check_app_json),
        _check("page_files", check_page_files),
        _check("tabbar_pages", check_tabbar_pages),
        _check("api_adapter_read_only", check_api_adapter_is_read_only),
        _check("mock_run_detail_shape", check_mock_run_detail_shape),
        _check("home_run_detail_navigation", check_home_run_detail_navigation),
        _check("settings_health_shape", check_settings_health_shape),
        _check("review_detail_run_context", check_review_detail_run_context),
        _check("review_list_run_context", check_review_list_run_context),
    ]
    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print(f"wechat-miniprogram static: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks)")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
