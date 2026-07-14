const mock = require("./mock");

const SOURCE_KEY = "apiDataSource";
const ERROR_KEY = "apiLastError";

function getAppConfig() {
  const app = getApp();
  return {
    apiBaseUrl: wx.getStorageSync("apiBaseUrl") || app.globalData.apiBaseUrl || "",
    useMock: wx.getStorageSync("useMock") === "" ? app.globalData.useMock : Boolean(wx.getStorageSync("useMock"))
  };
}

function setConnectionState(source, error) {
  wx.setStorageSync(SOURCE_KEY, source);
  wx.setStorageSync(ERROR_KEY, error || "");
}

function connectionState() {
  const { apiBaseUrl, useMock } = getAppConfig();
  if (useMock || !apiBaseUrl) {
    return {
      apiBaseUrl,
      useMock,
      source: "mock",
      error: ""
    };
  }
  return {
    apiBaseUrl,
    useMock,
    source: wx.getStorageSync(SOURCE_KEY) || (useMock ? "mock" : "unknown"),
    error: wx.getStorageSync(ERROR_KEY) || ""
  };
}

function request(path) {
  const { apiBaseUrl, useMock } = getAppConfig();
  if (useMock || !apiBaseUrl) {
    setConnectionState("mock", "");
    return Promise.reject(new Error("mock mode"));
  }
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${apiBaseUrl}${path}`,
      method: "GET",
      timeout: 8000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          setConnectionState("live", "");
          resolve(res.data);
        } else {
          const error = new Error(`HTTP ${res.statusCode}`);
          setConnectionState("mock", error.message);
          reject(error);
        }
      },
      fail(error) {
        const message = error.errMsg || "request failed";
        setConnectionState("mock", message);
        reject(new Error(message));
      }
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

function getRun(runId) {
  const local = mock.runs.find((item) => item.runId === runId) || null;
  return fallback(request(`/api/runs/${encodeURIComponent(runId)}`), local);
}

function listReviews() {
  return fallback(request("/api/reviews"), { items: mock.reviews }).then((data) => data.items || data);
}

function getReview(runId) {
  const local = mock.reviews.find((item) => item.runId === runId) || null;
  return fallback(request(`/api/reviews/${encodeURIComponent(runId)}`), local);
}

function checkHealth() {
  return request("/api/health");
}

module.exports = {
  getTodaySummary,
  listRuns,
  getRun,
  listReviews,
  getReview,
  checkHealth,
  connectionState
};
