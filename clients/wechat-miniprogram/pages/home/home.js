const api = require("../../utils/api");

Page({
  data: {
    summary: {},
    latestRuns: [],
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
        latestRuns: summary.latestRuns || [],
        loading: false
      });
    });
  },

  openRuns() {
    wx.switchTab({ url: "/pages/runs/runs" });
  },

  openReview() {
    wx.switchTab({ url: "/pages/review/review" });
  }
});
