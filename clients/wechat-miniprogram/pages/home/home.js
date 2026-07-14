const api = require("../../utils/api");

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
        latestRuns: summary.latestRuns || [],
        needsReview: summary.needsReview || [],
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

  openReviewDetail(event) {
    const runId = event.currentTarget.dataset.runId;
    wx.navigateTo({
      url: `/pages/review-detail/review-detail?runId=${encodeURIComponent(runId)}`
    });
  }
});
