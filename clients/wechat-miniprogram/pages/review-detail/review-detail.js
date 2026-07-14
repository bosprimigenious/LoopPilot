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

function normalizeRunSummary(data) {
  if (!data) return null;
  const runId = pick(data, "runId", "run_id") || "";
  const loopType = pick(data, "loopType", "loop_type") || "";
  const phase = data.phase || "-";
  const outcome = data.outcome || "unknown";
  const gate = data.gate || "-";
  const reportPath = data.reportPath || "";
  return {
    runId,
    title: data.title || `${loopType} run`,
    loopType,
    phase,
    outcome,
    gate,
    reportPath,
    badgeClass: badgeClass(outcome),
    rows: [
      { label: "Loop", value: loopType || "-" },
      { label: "Phase", value: phase },
      { label: "Outcome", value: outcome },
      { label: "Gate", value: gate },
      { label: "Report", value: reportPath || "-" }
    ]
  };
}

function normalizeReview(data) {
  const runId = pick(data, "runId", "run_id") || "";
  const loopType = pick(data, "loopType", "loop_type") || "";
  const deferredUntil = pick(data, "deferredUntil", "deferred_until") || "";
  const artifactPath = pick(data, "artifactPath", "artifact_path") || "";
  const createdAt = pick(data, "createdAt", "created_at") || "";
  const decidedAt = pick(data, "decidedAt", "decided_at") || "";
  const status = data.status || "needs_review";
  const reason = data.reason || data.title || "";
  const run = data.run || null;
  const runSummary = normalizeRunSummary(run);
  return {
    runId,
    loopType,
    status,
    title: data.title || `${loopType} review`,
    reason,
    artifactPath,
    deferredUntil,
    createdAt,
    decidedAt,
    run,
    runSummary,
    rows: [
      { label: "Run", value: runId },
      { label: "Loop", value: loopType || "-" },
      { label: "Status", value: status },
      { label: "Deferred", value: deferredUntil || "-" },
      { label: "Created", value: createdAt || "-" },
      { label: "Decided", value: decidedAt || "-" }
    ]
  };
}

Page({
  data: {
    runId: "",
    review: null,
    connection: {},
    loading: true,
    error: ""
  },

  onLoad(options) {
    const runId = decodeURIComponent(options.runId || "");
    this.setData({ runId });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  load() {
    const runId = this.data.runId;
    if (!runId) {
      this.setData({ loading: false, error: "missing run id" });
      return Promise.resolve();
    }
    this.setData({ loading: true, error: "" });
    return api.getReview(runId).then((review) => {
      if (!review) {
        this.setData({
          review: null,
          connection: api.connectionState(),
          loading: false,
          error: "review not found"
        });
        return;
      }
      this.setData({
        review: normalizeReview(review),
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  copyValue(event) {
    wx.setClipboardData({ data: event.currentTarget.dataset.value || "" });
  },

  openRun() {
    wx.navigateTo({
      url: `/pages/run-detail/run-detail?runId=${encodeURIComponent(this.data.review.runId)}`
    });
  }
});
