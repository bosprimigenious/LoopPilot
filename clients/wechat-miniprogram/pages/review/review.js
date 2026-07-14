const api = require("../../utils/api");

Page({
  data: {
    reviews: [],
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
        reviews,
        loading: false
      });
    });
  },

  copyPath(event) {
    const path = event.currentTarget.dataset.path;
    wx.setClipboardData({ data: path || "" });
  }
});
