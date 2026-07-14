const api = require("../../utils/api");

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
        reviews,
        connection: api.connectionState(),
        loading: false
      });
    });
  },

  copyPath(event) {
    const path = event.currentTarget.dataset.path;
    wx.setClipboardData({ data: path || "" });
  }
});
