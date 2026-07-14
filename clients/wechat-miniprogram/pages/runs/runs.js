const api = require("../../utils/api");

function badgeClass(outcome) {
  if (outcome === "succeeded") return "badge-pass";
  if (outcome === "blocked" || outcome === "failed") return "badge-blocked";
  if (outcome === "partial" || outcome === "exhausted") return "badge-review";
  return "badge-neutral";
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
        runs: runs.map((run) => ({
          ...run,
          badgeClass: badgeClass(run.outcome)
        })),
        connection: api.connectionState(),
        loading: false
      });
    });
  }
});
