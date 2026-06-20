# 05 DailyNewsLoop 高价值日报

## 1. 实际目标

DailyNewsLoop 每天约 30 分钟读取工程、研究、GitHub、重大政治和财经信息，只留下少量真正影响当前工作、研究或判断的内容。

日报默认上限：

- GitHub/开发：3 条；
- 论文/研究：3 条；
- 重大政治：2 条；
- 重大财经：2 条；
- 今日行动建议：最多 3 条。

没有足够重要的内容时可以输出 0 条，不允许为了填满数量降低标准。

## 2. 信息类别

### GitHub 与开发

- 新增 Star 加速度明显的仓库；
- 与当前技术栈直接相关的 release、breaking change 和安全公告；
- 当前项目 Issue/PR/CI 的重要变化；
- 新工具、Agent 框架或开发方法，但必须能说明实际价值。

### 论文与研究

- 与当前论文主题强相关的新论文；
- 新 benchmark、数据集、baseline 或复现实验；
- 可能削弱当前论文 novelty 或 claim 的新结果；
- 对下一步实验有直接启发的方法。

### 政治与财经

- 重大政策、选举、冲突、制裁、外交和监管变化；
- 央行、通胀、就业、利率、市场制度和系统性风险事件；
- 对个人工作、研究方向、行业或资产环境可能产生明显影响的事件。

政治财经部分只做事实摘要和影响情景，不做交易指令。

## 3. 来源等级

| 等级 | 示例类型 | 用法 |
|---|---|---|
| A | 政府/监管/央行/交易所公告、官方发布、正式论文 | 事实依据 |
| B | GitHub、作者主页、会议页、权威通讯社 | 交叉核验与背景 |
| C | 社区、论坛、社交媒体 | 发现候选，不单独成稿 |

C 级信号应追溯到 A/B 级来源。无法追溯时进入 `unresolved-signals.md`，不进入正式 Top News。

## 4. 完整流程

```text
读取上次游标、历史快照、当前项目与论文主题
  ↓
按来源增量抓取
  ↓
标准化 URL、标题、作者、发布时间、事件日期和来源
  ↓
内容哈希 + 规范 URL + 标题相似度去重
  ↓
初筛相关性
  ↓
核验原始来源与发生日期
  ↓
计算重要性、行动性、可信度和新颖度
  ↓
每类只保留超过阈值的少量条目
  ↓
生成 daily-news-report.md
  ↓
向 Intern/Paper Inbox 写候选任务
```

## 5. GitHub“今日最火”正确计算

GitHub 仓库的总 Star 不等于“今天新增最多”。系统必须每日保存候选仓库快照：

```text
star_delta_24h = stars_now - stars_previous_snapshot
fork_delta_24h = forks_now - forks_previous_snapshot
issue_velocity = meaningful_issue_events / time_window
```

排名至少结合：

- 24 小时新增 Star；
- 总 Star 与仓库年龄，防止老项目天然占优；
- 真实提交、release、Issue 活跃度；
- 是否存在异常刷 Star 信号；
- 与用户当前开发或研究的相关性。

第一次运行没有历史快照时，只能输出“候选热门仓库”，不得声称“今日新增 Star 最多”。

## 6. 重大新闻门槛

一条政治财经新闻进入正式日报，至少满足一个条件：

- 改变法律、政策、利率、监管或国际关系；
- 涉及显著经济体或行业并具有可验证影响；
- 多个独立可靠来源报道；
- 直接影响用户的技术行业、研究主题或生活决策；
- 属于明确突发风险。

普通评论、价格小波动、名人表态和没有后续行动的争论默认过滤。

## 7. 每条新闻格式

```markdown
### 标题

- 分类：GitHub / Research / Politics / Finance
- 发生时间：
- 发布时间：
- 原始来源：
- 交叉来源：
- 已确认事实：
- 为什么重要：
- 对我的影响：
- 仍不确定：
- 建议动作：忽略 / 观察 / 加入 Intern / 加入 Paper / 人工处理
- 置信度：high / medium
```

必须区分“已确认事实”和“影响推断”。

## 8. 候选任务规则

- 只有 `high` 置信度且可执行的条目才能写入 Inbox。
- 候选默认 `proposed`，主 Loop 自主判断是否接受。
- 相同候选在过期前不得重复创建。
- 安全公告可以提升紧急度，但仍不得自动升级依赖。
- 新闻不能覆盖用户明确任务和昨日未关闭的高优先级问题。

## 9. Markdown 产物

```text
artifacts/daily-news/<run_id>/
├── source-log.md
├── github-trending-report.md
├── research-news.md
├── politics-finance-news.md
├── verification-report.md
├── unresolved-signals.md
├── intern-candidates.md
├── paper-candidates.md
└── daily-news-report.md
```
