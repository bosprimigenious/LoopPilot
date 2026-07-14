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
  const runId = pick(data, "runId", "run_id") || "";
  const loopType = pick(data, "loopType", "loop_type") || "";
  const terminalReason = pick(data, "terminalReason", "terminal_reason") || "";
  const reviewStatus = pick(data, "reviewStatus", "review_status") || "";
  const reportStatus = pick(data, "reportStatus", "report_status") || "";
  const startedAt = pick(data, "startedAt", "started_at") || "";
  const finishedAt = pick(data, "finishedAt", "finished_at") || "";
  const reportPath = data.reportPath || "";
  const outcome = data.outcome || "unknown";
  const phase = data.phase || "unknown";
  return {
    runId,
    title: data.title || `${loopType} run`,
    loopType,
    outcome,
    phase,
    badgeClass: badgeClass(outcome),
    terminalReason,
    reviewStatus,
    reportStatus,
    startedAt,
    finishedAt,
    gate: data.gate || "",
    reportPath,
    rows: [
      { label: "Loop", value: loopType },
      { label: "Phase", value: phase },
      { label: "Outcome", value: outcome },
      { label: "Gate", value: data.gate || "-" },
      { label: "Review", value: reviewStatus || "-" },
      { label: "Report", value: reportStatus || "-" },
      { label: "Started", value: startedAt || "-" },
      { label: "Finished", value: finishedAt || "-" }
    ]
  };
}

Page({
  data: {
    runId: "",
    run: null,
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
    return api.getRun(runId).then((run) => {
      if (!run) {
        this.setData({
          run: null,
          connection: api.connectionState(),
          loading: false,
          error: "run not found"
        });
        return;
      }
      this.setData({
        run: normalizeRun(run),
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  copyValue(event) {
    wx.setClipboardData({ data: event.currentTarget.dataset.value || "" });
  }
});
