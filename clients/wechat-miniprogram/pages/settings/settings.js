const api = require("../../utils/api");

function boolText(value, trueText, falseText) {
  return value ? trueText : falseText;
}

function normalizeHealth(data) {
  const endpoints = Array.isArray(data.endpoints) ? data.endpoints : [];
  return [
    { label: "Status", value: data.status || "ok" },
    { label: "Version", value: data.version || "-" },
    { label: "State", value: data.stateBackend || "-" },
    { label: "Read-only", value: boolText(data.readOnly, "yes", "no") },
    { label: "Mutations", value: boolText(data.mutationsEnabled, "enabled", "disabled") },
    { label: "Adapters", value: boolText(data.allowRealAdapters, "real enabled", "blocked") },
    { label: "Endpoints", value: endpoints.length ? String(endpoints.length) : "-" }
  ];
}

Page({
  data: {
    apiBaseUrl: "",
    useMock: true,
    connection: {},
    healthText: "",
    healthRows: []
  },

  onShow() {
    this.setData({
      apiBaseUrl: wx.getStorageSync("apiBaseUrl") || "",
      useMock: wx.getStorageSync("useMock") === "" ? true : Boolean(wx.getStorageSync("useMock")),
      connection: api.connectionState(),
      healthText: "",
      healthRows: []
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
      this.setData({ healthText: "mock mode", healthRows: [], connection: api.connectionState() });
      return;
    }
    api.checkHealth()
      .then((data) => {
        this.setData({
          healthText: data.status || "ok",
          healthRows: normalizeHealth(data),
          connection: api.connectionState()
        });
      })
      .catch((error) => {
        this.setData({
          healthText: error.message || "failed",
          healthRows: [],
          connection: api.connectionState()
        });
      });
  }
});
