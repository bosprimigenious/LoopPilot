# LoopPilot WeChat Mini Program

This is a lightweight mobile client for LoopPilot. The first milestone is a read-only dashboard with mock data and a configurable API base URL.

## Open

1. Open WeChat DevTools.
2. Import this folder: `clients/wechat-miniprogram`.
3. Use test app id or your own app id.
4. Run with mock mode enabled by default.

## Pages

- `pages/home/home`: daily overview.
- `pages/runs/runs`: recent run records.
- `pages/review/review`: pending review items.
- `pages/settings/settings`: API base URL and mock/live toggle.

## API Boundary

The client expects a future local LoopPilot API bridge:

```text
GET /api/health
GET /api/summary/today
GET /api/runs
GET /api/reviews
```

Review mutations are intentionally not wired in the first client milestone.
