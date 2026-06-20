# 11 每日真实运行手册

## 1. 目标时间窗

三个 Loop 默认各有约 30 分钟独立预算。它们可以分时运行，也可通过 `run all` 顺序执行。

```text
07:00–07:30  DailyNewsLoop
07:30–08:00  InternLoop（上班途中查看结果）
08:00–08:30  PaperLoop
```

具体时刻由配置决定；关键约束是每条 Loop 25 分钟工作、5 分钟收尾。

## 2. 前一晚准备

用户只需做最小输入：

- 将开发遗留写入项目任务文件或昨日 `next-actions.md`。
- 确保仓库能够运行基本测试。
- 保存论文草稿、实验结果和待处理意见。
- 可选地指定第二天必须优先的问题。

## 3. 早晨自动执行

### DailyNewsLoop

更新 GitHub 快照、论文与重大新闻，生成少量信息，并向两个 Inbox 提出候选任务。

### InternLoop

先看用户明确任务和昨日遗留，再看真实失败，最后才考虑 DailyNews 候选。尝试关闭一个问题，完成测试和开发报告。

### PaperLoop

先看昨日论文缺口和核心证据风险，再考虑最新论文。推进一个最重要方向，完成核验与论文报告。

## 4. 通勤途中应看到什么

每日总报告顶部只显示：

```text
1. 开发：昨天的问题是否解决？如果没有，卡在哪里？
2. 论文：今天推进了什么？下一方向是什么？
3. 外部：今天真正值得注意的最多三件事是什么？
4. 我需要做的人工决定是什么？
```

用户不需要先翻日志。需要细节时再点击对应 Run 报告和证据。

## 5. 午间或下班反馈

用户可以：

- 接受代码修改并自行 commit；
- 拒绝结果并写明原因；
- 补充缺失环境或业务信息；
- 接受论文修订或调整研究优先级；
- 将报告中的 next action 留给次日；
- 把不重要的新闻候选标记为忽略，帮助后续规则调整。

## 6. 无任务与失败日

- 没有合适任务时输出 `NO_ACTION`，不制造工作。
- 30 分钟不足时输出 `PARTIAL/EXHAUSTED` 和安全检查点。
- 缺少用户决定时输出 `BLOCKED`。
- 任何情况下都必须产生简短报告，说明明天如何继续。

## 7. CLI

```bash
looppilot run daily-news
looppilot run intern
looppilot run paper
looppilot run all
looppilot status
looppilot inspect <run-id>
looppilot resume <run-id>
looppilot approve <run-id>
looppilot reject <run-id> --reason "..."
looppilot cancel <run-id>
looppilot report <run-id>
looppilot doctor
```
