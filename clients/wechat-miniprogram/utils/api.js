const mock = require("./mock");

function getAppConfig() {
  const app = getApp();
  return {
    apiBaseUrl: wx.getStorageSync("apiBaseUrl") || app.globalData.apiBaseUrl || "",
    useMock: wx.getStorageSync("useMock") === "" ? app.globalData.useMock : Boolean(wx.getStorageSync("useMock"))
  };
}

function request(path) {
  const { apiBaseUrl, useMock } = getAppConfig();
  if (useMock || !apiBaseUrl) {
    return Promise.reject(new Error("mock mode"));
  }
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${apiBaseUrl}${path}`,
      method: "GET",
      timeout: 8000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      },
      fail: reject
    });
  });
}

function fallback(promise, value) {
  return promise.catch(() => value);
}

function getTodaySummary() {
  return fallback(request("/api/summary/today"), mock.summary);
}

function listRuns() {
  return fallback(request("/api/runs"), { items: mock.runs }).then((data) => data.items || data);
}

function listReviews() {
  return fallback(request("/api/reviews"), { items: mock.reviews }).then((data) => data.items || data);
}

function checkHealth() {
  return request("/api/health");
}

module.exports = {
  getTodaySummary,
  listRuns,
  listReviews,
  checkHealth
};
