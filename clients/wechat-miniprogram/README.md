# LoopPilot WeChat Mini Program

This is a lightweight mobile client for LoopPilot. The first milestone is a read-only dashboard with mock data and a configurable API base URL.

## Open

1. Open WeChat DevTools.
2. Import this folder: `clients/wechat-miniprogram`.
3. Use test app id or your own app id.
4. Run with mock mode enabled by default.

## Pages

- `pages/home/home`: daily overview with latest run and review detail links.
- `pages/runs/runs`: recent run records.
- `pages/run-detail/run-detail`: read-only run detail.
- `pages/review/review`: pending review items with linked run context and report path copy.
- `pages/review-detail/review-detail`: read-only review detail with linked run context.
- `pages/settings/settings`: API base URL and mock/live toggle.

## API Boundary

Run the local read-only LoopPilot API bridge:

```bash
loop-pilot api serve --host 127.0.0.1 --port 7860
```

Then set API Base URL in the settings tab:

```text
http://127.0.0.1:7860
```

The first bridge exposes:

```text
GET /api/health
GET /api/summary/today
GET /api/runs
GET /api/runs/{run_id}
GET /api/reviews
GET /api/reviews/{run_id}
```

The settings health check displays bridge version, state backend, read-only status, mutation status, allowed methods, preflight status, adapter mode, endpoint count, and the read-only endpoint list returned by `/api/health`.

Run detail responses include `reportPath` and a read-only `artifacts` preview from `artifact-manifest.json`, so the client can copy report or artifact paths without executing local actions.

Review mutations are intentionally not wired in the first client milestone.
When live API requests fail, pages fall back to mock data and show a visible source/status notice.

The API bridge contract can be validated without binding a local port, including health, today summary, run detail with artifact preview, review detail, POST rejection, and OPTIONS preflight:

```bash
python scripts/verify_api_bridge_contract.py
```

Static scaffold validation is available without Node.js:

```bash
python scripts/verify_wechat_miniprogram_static.py
```
