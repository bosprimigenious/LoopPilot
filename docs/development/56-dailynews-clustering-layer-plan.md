# DailyNews 聚簇层计划（0.6）

## 结论

DailyNews 必须加聚簇层。真实新闻/热点不是一条条独立 item，而是同一事件被不同媒体、GitHub repo、论文、博客、社媒反复描述。没有聚簇，系统会出现三类问题：

1. 同一事件重复进入日报；
2. 单源假消息被误当成多个独立信号；
3. 无法判断“哪个事件正在升温，哪个只是噪声”。

建议把聚簇层放在 DailyNews 的 `dedup` 和 `verification` 之间：

```text
collect sources
  ↓
normalize items
  ↓
exact dedup
  ↓
event clustering
  ↓
cross-source verification
  ↓
rank clusters
  ↓
write report / unresolved / candidate-actions
```

## 不建议一上来重型全自动

不要一开始就把 BERTopic 当主路径。BERTopic 很强，但依赖重，参数多，短文本新闻容易不稳定，且对小样本每日运行可能有过度工程问题。

推荐分层：

```text
Level 0: deterministic dedup
Level 1: lightweight embedding cluster
Level 2: optional BERTopic topic model
Level 3: long-term trend memory
```

## 推荐开源方案

### 1. sentence-transformers + HDBSCAN（推荐主路径）

用途：

- 同事件聚簇；
- 新闻标题/摘要聚类；
- GitHub repo 与文章语义相似聚类；
- 自动识别 outlier。

推荐原因：

- HDBSCAN 不需要预先指定 cluster 数量；
- 能把噪声标为 `-1`；
- 比 KMeans 更适合每天不知道会有多少热点的场景；
- sentence-transformers 可以本地跑，也可换模型。

开源链接：

- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- [hdbscan](https://github.com/scikit-learn-contrib/hdbscan)
- [HDBSCAN docs](https://hdbscan.readthedocs.io/)

可选 embedding 模型：

- `all-MiniLM-L6-v2`：轻、快、英文够用；
- `all-mpnet-base-v2`：更准但慢；
- `BAAI/bge-small-en-v1.5`：检索场景强；
- `intfloat/multilingual-e5-small`：中英混合更合适；
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`：多语言轻量可用。

DailyNews 默认建议：

```text
embedding_model = sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
clusterer = hdbscan
min_cluster_size = 2
min_samples = 1
metric = cosine
```

注意：HDBSCAN 对 cosine 的支持可能需要预计算距离，或归一化向量后用 euclidean。实现时要写测试固定行为。

### 2. BERTopic（推荐 optional analysis 层）

用途：

- 给 cluster 自动命名；
- 生成主题关键词；
- 做周报/月报；
- 分析长期趋势。

不建议作为每日主路径的原因：

- 依赖重；
- 对每日几十条新闻可能不稳定；
- 输出 topic 不等于事实事件；
- 更适合“本周/本月聚类解释”，不是“今天是否可信”。

开源链接：

- [BERTopic GitHub](https://github.com/MaartenGr/BERTopic)
- [BERTopic paper](https://arxiv.org/abs/2203.05794)

DailyNews 用法：

```text
Daily event clusters -> BERTopic labeler -> cluster title / keywords
```

即 BERTopic 只负责“命名/解释”，不负责最终可信判断。

### 3. Top2Vec（候选，不作为默认）

用途：

- 自动发现 topic 数量；
- 做长期语义主题空间；
- 周/月级别趋势。

风险：

- 对小规模每日新闻不一定稳定；
- 依赖与运行成本高；
- 不如 sentence-transformers + HDBSCAN 可控。

链接：

- [Top2Vec GitHub](https://github.com/ddangelov/Top2Vec)
- [Top2Vec paper](https://arxiv.org/abs/2008.09470)

### 4. scikit-learn Agglomerative / DBSCAN（轻量 fallback）

用途：

- 没装 `hdbscan` 时 fallback；
- 小规模数据；
- CI fixture 测试。

推荐 fallback：

```text
TF-IDF char/word ngram
  ↓
cosine similarity
  ↓
connected components or agglomerative clustering
```

优点：

- 依赖轻；
- 完全 deterministic；
- 适合 CI。

缺点：

- 语义能力弱；
- 跨语言差；
- 对 paraphrase 不敏感。

链接：

- [scikit-learn clustering](https://scikit-learn.org/stable/modules/clustering.html)

### 5. GDELT（外部事件源，不是聚类库）

GDELT 可以作为政治/国际事件的外部参考源。它不是 DailyNews 内部聚类算法，但可以提供：

- 已聚合/结构化事件；
- 地点、组织、主题、情绪；
- 全球事件背景。

适合后续作为 source connector，而不是 0.6 第一版核心依赖。

链接：

- [GDELT Project](https://www.gdeltproject.org/)
- [GDELT overview](https://en.wikipedia.org/wiki/GDELT_Project)

## DailyNews 聚簇数据结构

新增 `NewsCluster`：

```yaml
cluster_id: cl_20260623_001
title: Fed communication shift and market volatility
category: finance
confidence: medium-high
status: confirmed | candidate | unresolved
items:
  - source_item_id: ap_...
  - source_item_id: marketwatch_...
canonical_event_time: 2026-06-23T...
first_seen_at: ...
last_seen_at: ...
source_count: 3
source_tiers:
  A: 1
  B: 2
  C: 0
confirmed_facts:
  - ...
inferences:
  - ...
uncertainties:
  - ...
why_it_matters: ...
recommended_action: ignore | watch | import_to_intern | import_to_paper | human_review
```

新增 artifact：

```text
artifacts/daily-news/<run_id>/
├── source-items.json
├── exact-dedup.json
├── clusters.json
├── cluster-report.md
├── verification-report.md
├── unresolved-signals.md
├── daily-news-report.md
├── candidate-actions.json
└── artifact-manifest.json
```

## 聚簇判定规则

一条 item 进入 cluster 需要同时考虑：

1. canonical URL / domain；
2. normalized title；
3. entity overlap；
4. event date proximity；
5. embedding similarity；
6. source tier；
7. category compatibility。

禁止只靠 embedding。原因是：

- “Fed rate cut” 和 “Fed communication shift” 语义接近，但可能是不同事件；
- 同一个 GitHub repo 的 release、security advisory、funding news 不一定是同一个事件；
- 政治财经新闻必须避免把观点文章和事实报道混成同一证据。

## Cluster status 规则

```text
confirmed:
  至少一个 A/B 高可信来源，或两个以上独立 B 来源；
  有明确 event time / original source；
  confirmed_facts 与 inferences 分开。

candidate:
  来源可信但交叉不足；
  或 GitHub/Paper 技术信号可行动但仍需人工检查。

unresolved:
  单 C 来源；
  单社媒/论坛；
  标题相似但事实冲突；
  无原始来源；
  疑似刷星/PR 宣传/营销稿。
```

## 推荐实现路线

### 0.6-a：Deterministic Cluster Baseline

不引入重依赖，只做：

- URL canonicalization；
- title normalization；
- entity overlap；
- same-day event grouping；
- TF-IDF cosine fallback；
- `clusters.json`；
- `unresolved-signals.md`。

验收：

```bash
pytest tests/unit/test_dailynews_clustering.py -q
loop-pilot run daily-news --fixture clustered_news --dry-run
```

### 0.6-b：Optional embedding cluster

新增 optional dependency：

```toml
[project.optional-dependencies]
news = [
  "sentence-transformers>=3",
  "hdbscan>=0.8",
  "numpy>=1.26",
  "scikit-learn>=1.4",
]
```

如果没装 extra：

```text
DailyNews falls back to deterministic clustering.
```

验收：

- 未安装 `news` extra 时所有测试仍绿；
- 安装 `news` extra 时 embedding clustering 可用；
- 聚类结果写入 `clusters.json`，但不会自动提高 confidence。

### 0.6-c：BERTopic labels

新增 optional dependency：

```toml
news-topic = [
  "bertopic>=0.16",
]
```

只做 cluster label，不做事实判断。

### 0.6-d：Cluster memory

SQLite 增加：

```text
news_clusters
cluster_items
cluster_observations
```

用于：

- 跨日追踪同一事件；
- 判断事件升温/降温；
- 避免重复导入 Inbox；
- 支持“昨天未核验，今天补证据”。

## DailyNews 报告怎么变

以前：

```text
Items kept: 4
Intern candidates: 2
Paper candidates: 1
```

以后：

```text
Top clusters today:

1. Fed communication shift and market volatility
   status: confirmed
   sources: AP, MarketWatch, Kiplinger
   action: watch

2. GitHub codebase-memory MCP trend
   status: candidate
   sources: GitHub Trending only
   action: import_to_intern? human review required

3. Starmer resignation and UK policy uncertainty
   status: candidate
   sources: Axios, Guardian
   action: watch; needs AP/Reuters/government confirmation

Unresolved:
  - single-source claims
  - social-only signals
  - suspicious GitHub star spikes
```

## 对 LoopPilot 的实际收益

加聚簇后，DailyNews 才能真正做到：

- 不重复；
- 不被刷屏；
- 多源核验；
- 识别同一事件的不同报道；
- 把 GitHub / paper / finance / politics 放进同一个事件框架；
- 根据 cluster status 决定是否进入 Intern/Paper。

## 最终建议

0.6 Real DailyNews 必须包含 cluster layer，但版本上分两步：

```text
0.6-a deterministic clusters
0.6-b optional embeddings + HDBSCAN
```

不要一上来引入 BERTopic 作为必需依赖。BERTopic 应该是 0.6-c 或 0.7 的可选 topic-labeling 能力。

