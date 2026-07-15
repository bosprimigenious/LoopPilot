const summary = {
  date: "2026-07-15",
  plannedCount: 3,
  pendingReviewCount: 2,
  blockedCount: 0,
  outcomeCounts: {
    succeeded: 1,
    partial: 2,
    blocked: 0,
    failed: 0,
    other: 0
  },
  latestRuns: [
    {
      runId: "20260715T090000Z-daily_news-demo",
      loopType: "daily_news",
      outcome: "succeeded",
      phase: "TERMINATED",
      title: "DailyNews 信号筛选",
      updatedAt: "09:05",
      reviewStatus: "not_required",
      reportStatus: "ready",
      gate: "pass",
      reportPath: "var/artifacts/daily_news/20260715T090000Z-daily_news-demo/daily-news-report.md"
    },
    {
      runId: "20260715T091000Z-intern-demo",
      loopType: "intern",
      outcome: "partial",
      phase: "WAITING_APPROVAL",
      title: "InternLoop 修复建议",
      updatedAt: "09:18",
      reviewStatus: "needs_review",
      reportStatus: "ready",
      gate: "needs_review",
      reportPath: "var/artifacts/intern/20260715T091000Z-intern-demo/development-report.md",
      artifacts: [
        {
          artifactId: "intern-demo-report",
          kind: "report",
          path: "development-report.md",
          absolutePath: "var/artifacts/intern/20260715T091000Z-intern-demo/development-report.md",
          mediaType: "text/markdown",
          sizeBytes: 4096,
          humanReadable: true,
          exists: true
        }
      ]
    }
  ],
  needsReview: []
};

const runs = [
  ...summary.latestRuns,
  {
    runId: "20260715T092000Z-paper-demo",
    loopType: "paper",
    outcome: "partial",
    phase: "WAITING_APPROVAL",
    title: "PaperLoop 证据修订",
    updatedAt: "09:28",
    reviewStatus: "needs_review",
    reportStatus: "ready",
    gate: "needs_review",
    reportPath: "var/artifacts/paper/20260715T092000Z-paper-demo/paper-development-report.md"
  }
];

const reviews = [
  {
    runId: "20260715T091000Z-intern-demo",
    loopType: "intern",
    title: "检查 patch.diff 与 pytest 证据",
    status: "needs_review",
    artifactPath: "var/artifacts/intern/...",
    run: runs.find((item) => item.runId === "20260715T091000Z-intern-demo")
  },
  {
    runId: "20260715T092000Z-paper-demo",
    loopType: "paper",
    title: "确认 SOURCE REQUIRED 标记",
    status: "needs_review",
    artifactPath: "var/artifacts/paper/...",
    run: runs.find((item) => item.runId === "20260715T092000Z-paper-demo")
  }
];

summary.needsReview = reviews;

module.exports = {
  summary,
  runs,
  reviews
};
