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

function formatBytes(value) {
  if (value === undefined || value === null || value === "") return "";
  const bytes = Number(value);
  if (!Number.isFinite(bytes)) return "";
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function normalizeArtifact(data) {
  const path = data.path || "";
  const absolutePath = pick(data, "absolutePath", "absolute_path") || "";
  const mediaType = pick(data, "mediaType", "media_type") || "";
  const sizeLabel = formatBytes(pick(data, "sizeBytes", "size_bytes"));
  const meta = [mediaType, sizeLabel].filter(Boolean).join(" · ");
  return {
    artifactId: pick(data, "artifactId", "artifact_id") || path,
    kind: data.kind || "artifact",
    path,
    absolutePath,
    copyValue: absolutePath || path,
    mediaType,
    sizeLabel,
    meta,
    humanReadable: Boolean(pick(data, "humanReadable", "human_readable")),
    readableLabel: pick(data, "humanReadable", "human_readable") ? "可读" : "机器",
    readableBadgeClass: pick(data, "humanReadable", "human_readable") ? "badge-pass" : "badge-neutral",
    exists: data.exists !== false
  };
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
  const artifacts = Array.isArray(data.artifacts) ? data.artifacts.map(normalizeArtifact) : [];
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
    artifacts,
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
