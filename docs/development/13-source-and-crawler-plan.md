# 13 数据源与爬取器计划

## 1. 总原则

- API/RSS 优先于 HTML 抓取。
- 原始来源优先于聚合和转述。
- 每个来源使用独立 Connector，不在业务代码里散落爬虫。
- 遵守来源条款、robots、限速和缓存要求。
- 页面结构变化只能导致单源失败，不能使整个 DailyNewsLoop 失败。
- 抓取结果先标准化和核验，再交给模型摘要。

## 2. Connector 接口

```text
fetch(cursor, since, limit) -> RawItem[]
normalize(raw) -> SourceItem
validate(item) -> ValidationResult
checkpoint() -> Cursor
healthcheck() -> HealthStatus
```

`SourceItem` 至少包含来源、规范 URL、标题、作者、发布时间、事件日期、正文摘要、内容哈希、抓取时间和来源等级。

## 3. GitHub 数据

### 获取内容

- Repository Search：发现新创建且获得关注的项目。
- Repository metadata：总 Star、fork、更新时间、语言、license。
- Releases：与当前技术栈相关的版本变化。
- Issues/PR/Actions：目标项目的实际问题。
- Security advisories：高优先级安全信号。

### 今日 Star 增量

GitHub 一次查询通常只能提供当前累计值。系统需要每天对候选仓库保存快照，再计算 24 小时差值。候选池由新仓库、历史热门、当前技术栈和昨日增长较高仓库组成。

### 反噪声

- 排除 fork、镜像、空仓库和缺少有效提交的项目。
- 检查 Star 增长与提交、Issue、访问讨论是否严重失衡。
- 总榜和“与我相关”榜分开；日报优先后者。

## 4. 论文与引用数据

优先接入：

- arXiv 等预印本元数据；
- Crossref 等 DOI 元数据；
- 会议/期刊官方页面；
- Semantic Scholar/OpenAlex 等补充索引；
- 作者主页、代码仓库和数据集页面。

检索分两阶段：

1. 元数据与摘要筛选，降低成本。
2. 对真正相关的候选读取正文并定位支持语句。

引用键以稳定标识去重，标题模糊匹配仅作辅助。正式写入前必须核验题名、作者、年份和来源状态。

## 5. 政治财经来源

### 原始事实

优先使用政府、立法机构、央行、统计机构、监管机构、交易所和国际组织的正式公告或数据发布。

### 事件报道

使用少量稳定的权威通讯社或主流媒体进行交叉核验。单一匿名消息、社交媒体截图和无法访问原文的转载不进入正式日报。

### 处理方式

- 抽取“发生了什么”，不先抽取评论。
- 单独记录事件发生时间、公告时间和报道时间。
- 政策原文与媒体解释分开。
- 对市场影响只列情景与不确定性，不生成买卖建议。

## 6. 抓取脚本结构

```text
src/loop_pilot/connectors/
├── base.py
├── github/
│   ├── repositories.py
│   ├── releases.py
│   ├── issues.py
│   └── snapshots.py
├── research/
│   ├── arxiv.py
│   ├── crossref.py
│   ├── conference.py
│   └── fulltext.py
├── news/
│   ├── rss.py
│   ├── official_release.py
│   └── html_fallback.py
└── market/
    ├── central_bank.py
    ├── statistics.py
    └── regulator.py
```

## 7. 限速、缓存和降级

- 每个来源独立令牌桶限速。
- 使用 ETag、Last-Modified、cursor 和本地内容哈希增量获取。
- 429/5xx 指数退避，不无限重试。
- HTML 解析器使用结构探针；关键 selector 失效即报告源异常。
- 单源失败时使用缓存并标记陈旧时间。
- 超过最大陈旧时间的内容不得标为“今日”。

## 8. 爬虫验收

- 增量抓取不重复下载未变化内容。
- 标准化后同一事件可跨来源聚合。
- 日期、时区和规范 URL 正确。
- 来源失败可隔离和恢复。
- 所有正式日报条目能反查原始来源。
- 未经核验的信息不会进入主 Loop Inbox。

## 9. Source Registry

`sources.yaml` 是唯一启用清单。文档中的名称只是候选，未完成 endpoint、条款、限速和解析器验证前不得标记 `enabled: true`。

### GitHub

- GitHub Search API；
- 指定 topic 查询；
- 用户 repo watchlist；
- repository/release/issue/security 元数据；
- Trending 页面仅作为补充候选，Star 增量仍以本地快照计算。

### 研究

- arXiv；
- ACL Anthology；
- OpenReview；
- Crossref；
- Semantic Scholar/OpenAlex 等补充索引；
- Papers with Code、Hugging Face Papers、会议官网和作者项目页。

正式引用优先 DOI、会议/期刊页面和论文正文；聚合站只帮助发现。

### 开发工具

- 当前项目依赖的官方 changelog 与 release notes；
- GitHub release notes；
- 配置中实际使用的模型/CLI 官方更新页；
- 相关安全公告。

### 政治财经

- 政府、议会、央行、财政、统计、监管、交易所和国际组织原始发布；
- 少量配置批准的权威通讯社或财经媒体用于事件发现与交叉核验；
- 社交媒体默认不启用，启用时只能进入 unresolved signals。

## 10. 来源排序

```text
final_score = relevance × confidence_gate
            + reliability
            + actionability
            + novelty
            + project_relation
            + urgency
```

`confidence_gate` 未达到类别阈值时直接过滤，不允许用其他高分抵消低可信度。权重、阈值和每类上限写入配置，并用 Golden Case 固定预期行为。
