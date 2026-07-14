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
    reportPath: run.reportPath || "",
    badgeClass: badgeClass(outcome)
  } : null;
  return {
    ...data,
    runSummary
  };
}

Page({
  data: {
    reviews: [],
    connection: {},
    loading: true
  },

  onShow() {
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  load() {
    this.setData({ loading: true });
    return api.listReviews().then((reviews) => {
      this.setData({
        reviews: reviews.map(normalizeReview),
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  copyPath(event) {
    const path = event.currentTarget.dataset.path;
    wx.setClipboardData({ data: path || "" });
  },

  openReview(event) {
    const runId = event.currentTarget.dataset.runId;
    wx.navigateTo({
      url: `/pages/review-detail/review-detail?runId=${encodeURIComponent(runId)}`
    });
  }
});
