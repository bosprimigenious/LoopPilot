App({
  globalData: {
    apiBaseUrl: "",
    useMock: true
  },

  onLaunch() {
    const apiBaseUrl = wx.getStorageSync("apiBaseUrl") || "";
    const storedUseMock = wx.getStorageSync("useMock");
    this.globalData.apiBaseUrl = apiBaseUrl;
    this.globalData.useMock = storedUseMock === "" ? true : Boolean(storedUseMock);
  }
});
