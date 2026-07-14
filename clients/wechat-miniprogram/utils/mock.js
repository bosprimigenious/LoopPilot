const summary = {
  date: "2026-07-15",
  plannedCount: 3,
  pendingReviewCount: 2,
  blockedCount: 0,
  latestRuns: [
    {
      runId: "20260715T090000Z-daily_news-demo",
      loopType: "daily_news",
      outcome: "succeeded",
      phase: "TERMINATED",
      title: "DailyNews 信号筛选",
      updatedAt: "09:05"
    },
    {
      runId: "20260715T091000Z-intern-demo",
      loopType: "intern",
      outcome: "partial",
      phase: "WAITING_APPROVAL",
      title: "InternLoop 修复建议",
      updatedAt: "09:18"
    }
  ]
};

const runs = [
  ...summary.latestRuns,
  {
    runId: "20260715T092000Z-paper-demo",
    loopType: "paper",
    outcome: "partial",
    phase: "WAITING_APPROVAL",
    title: "PaperLoop 证据修订",
    updatedAt: "09:28"
  }
];

const reviews = [
  {
    runId: "20260715T091000Z-intern-demo",
    loopType: "intern",
    title: "检查 patch.diff 与 pytest 证据",
    status: "needs_review",
    artifactPath: "var/artifacts/intern/..."
  },
  {
    runId: "20260715T092000Z-paper-demo",
    loopType: "paper",
    title: "确认 SOURCE REQUIRED 标记",
    status: "needs_review",
    artifactPath: "var/artifacts/paper/..."
  }
];

module.exports = {
  summary,
  runs,
  reviews
};
