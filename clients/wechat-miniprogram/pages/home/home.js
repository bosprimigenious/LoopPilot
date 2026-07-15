const api = require("../../utils/api");

function badgeClass(outcome) {
  if (outcome === "succeeded") return "badge-pass";
  if (outcome === "blocked" || outcome === "failed") return "badge-blocked";
  if (outcome === "partial" || outcome === "exhausted") return "badge-review";
  return "badge-neutral";
}

function normalizeReview(data) {
  const run = data.run || null;
  const outcome = run ? run.outcome || "unknown" : "";
  const runSummary = run ? {
    phase: run.phase || "-",
    outcome,
    gate: run.gate || "-",
    badgeClass: badgeClass(outcome)
  } : null;
  return {
    ...data,
    runSummary
  };
}

Page({
  data: {
    summary: {},
    latestRuns: [],
    needsReview: [],
    connection: {},
    loading: true
  },

  onShow() {
    this.load();
  },

  load() {
    this.setData({ loading: true });
    api.getTodaySummary().then((summary) => {
      this.setData({
        summary,
        latestRuns: (summary.latestRuns || []).map((run) => ({
          ...run,
          badgeClass: badgeClass(run.outcome)
        })),
        needsReview: (summary.needsReview || []).map(normalizeReview),
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  openRuns() {
    wx.switchTab({ url: "/pages/runs/runs" });
  },

  openReview() {
    wx.switchTab({ url: "/pages/review/review" });
  },

  openRunDetail(event) {
    const runId = event.currentTarget.dataset.runId;
    wx.navigateTo({
      url: `/pages/run-detail/run-detail?runId=${encodeURIComponent(runId)}`
    });
  },

  openReviewDetail(event) {
    const runId = event.currentTarget.dataset.runId;
    wx.navigateTo({
      url: `/pages/review-detail/review-detail?runId=${encodeURIComponent(runId)}`
    });
  }
});
