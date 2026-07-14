const api = require("../../utils/api");

Page({
  data: {
    apiBaseUrl: "",
    useMock: true,
    healthText: ""
  },

  onShow() {
    this.setData({
      apiBaseUrl: wx.getStorageSync("apiBaseUrl") || "",
      useMock: wx.getStorageSync("useMock") === "" ? true : Boolean(wx.getStorageSync("useMock")),
      healthText: ""
    });
  },

  onBaseUrlInput(event) {
    this.setData({ apiBaseUrl: event.detail.value });
  },

  onMockChange(event) {
    this.setData({ useMock: event.detail.value });
  },

  save() {
    const app = getApp();
    const apiBaseUrl = this.data.apiBaseUrl.trim().replace(/\/$/, "");
    wx.setStorageSync("apiBaseUrl", apiBaseUrl);
    wx.setStorageSync("useMock", this.data.useMock);
    app.globalData.apiBaseUrl = apiBaseUrl;
    app.globalData.useMock = this.data.useMock;
    wx.showToast({ title: "已保存", icon: "success" });
  },

  testHealth() {
    this.save();
    if (this.data.useMock) {
      this.setData({ healthText: "mock mode" });
      return;
    }
    api.checkHealth()
      .then((data) => {
        this.setData({ healthText: data.status || "ok" });
      })
      .catch((error) => {
        this.setData({ healthText: error.message || "failed" });
      });
  }
});
