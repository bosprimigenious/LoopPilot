const api = require("../../utils/api");

function badgeClass(outcome) {
  if (outcome === "succeeded") return "badge-pass";
  if (outcome === "blocked" || outcome === "failed") return "badge-blocked";
  if (outcome === "partial" || outcome === "exhausted") return "badge-review";
  return "badge-neutral";
}

function pick(data, camel, snake) {
  return data[camel] !== undefined ? data[camel] : data[snake];
}

function normalizeRun(data) {
  const outcome = data.outcome || "unknown";
  const startedAt = pick(data, "startedAt", "started_at") || "";
  const finishedAt = pick(data, "finishedAt", "finished_at") || "";
  const updatedAt = pick(data, "updatedAt", "updated_at") || finishedAt || startedAt;
  const reviewStatus = pick(data, "reviewStatus", "review_status") || "";
  const reportStatus = pick(data, "reportStatus", "report_status") || "";
  return {
    ...data,
    outcome,
    startedAt,
    finishedAt,
    updatedAt,
    reviewStatus,
    reportStatus,
    reportPath: data.reportPath || "",
    gate: data.gate || "",
    badgeClass: badgeClass(outcome)
  };
}

Page({
  data: {
    runs: [],
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
    return api.listRuns().then((runs) => {
      this.setData({
        runs: runs.map(normalizeRun),
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  copyPath(event) {
    const path = event.currentTarget.dataset.path;
    wx.setClipboardData({ data: path || "" });
  },

  openRun(event) {
    const runId = event.currentTarget.dataset.runId;
    wx.navigateTo({
      url: `/pages/run-detail/run-detail?runId=${encodeURIComponent(runId)}`
    });
  }
});
