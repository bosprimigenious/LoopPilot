# 15 Ideas 迁移与决策追踪

本文记录原始 `ideas.md` 中的内容如何进入正式开发文档。正式规范采用重构和纠错后的版本，不追求逐字复制。

## 1. 总体迁移结论

| Ideas 内容 | 正式去向 | 处理 |
|---|---|---|
| Automation、Worktree、Skill、Connector、Sub-agent、Memory | 01、02、06、07、08 | 保留，但从“同级六层”改为跨层能力 |
| 统一 LoopCore | 01、02 | 保留并改成确定性 Runtime |
| InternLoop | 03、14 | 完整保留并增加文件级实现 |
| PaperLoop | 04、14 | 完整保留并强化引用、一致性和事实保护 |
| DailyScout | 05、13、14 | 改名 DailyNewsLoop，成为第三个小 Loop |
| 七层架构 | 01 | 重构成六层依赖架构，避免混合阶段和组件 |
| Agent 列表 | 03、04、06 | 按逻辑职责合并，不按进程数量照搬 |
| Skill 列表 | 06 | 统一命名并消除与 Agent/Tool 重叠 |
| 信息源与关键词 | 05、13 | 信息源进入 Connector 计划；具体论文关键词进入项目配置 |
| 模型建议 | 06 | 具体品牌改为逻辑模型角色，供应商放配置 |
| 三轮/30 分钟 | 02、03、04、05、11 | 保留，并增加 25+5 分钟收尾机制 |
| Markdown 报告与 trace | 07 | 保留；Mini 使用 JSON/JSONL，V1 使用 SQLite + JSONL |
| 简单 rubric 的问题 | 04 | 保留，正式改成证据驱动评价管线 |
| 五层 Paper Evaluator | 04、14 | 扩展为 E1–E6，Revision Planner 独立为 E7 |
| agentic-rubric-runner 结合 | 本文第 5 节 | 保留为可选集成，不作为核心依赖 |

## 2. Agent 名称映射

| Ideas 名称 | 正式名称/归属 | 理由 |
|---|---|---|
| CodeContextAgent | CodeContextAgent / observer | 保留职责 |
| DevAgent | DevAgent / worker | 保留职责 |
| TestAgent | test_runner + TestDiagnoser + evaluator | 拆开执行、诊断、判定，避免一个 Agent 自证 |
| ReportAgent | Reporter 模板系统 | 报告事实应程序化渲染，不需自由 Agent |
| ResearchContextAgent | PaperStateReader | 名称更准确 |
| LiteratureScoutAgent | ResearchScout / literature_query | 保留查询职责 |
| WritingAgent | WritingAgent / writer | 保留职责 |
| CriticAgent | ResearchCritic / evaluator pipeline | 从泛化批评升级为证据管线 |

## 3. Skill 名称映射

| Ideas Skill | 正式 Skill/模块 |
|---|---|
| repo-map-skill | repository-mapping |
| issue-triage-skill | task-selection + Intern task_selector |
| minimal-patch-skill | minimal-patch |
| test-debug-skill | test-debugging + diagnoser |
| risk-gate-skill | risk-gate + Policy Engine |
| daily-report-skill | markdown-reporting + Reporter |
| paper-scout-skill | literature-query + Research Connector |
| paper-screening-skill | source-screening |
| structured-summary-skill | evidence-citation + source dossier |
| literature-matrix-skill | citation-verification + literature matrix artifact |
| claim-evidence-check-skill | claim-evidence-analysis |
| rubric-review-skill | 被 Research Evaluation Pipeline 替代 |
| experiment-gap-skill | experiment-sufficiency |
| paper-report-skill | markdown-reporting + paper template |

## 4. 来源迁移

Ideas 中的 arXiv、ACL Anthology、OpenReview、Papers with Code、Semantic Scholar、Hugging Face、会议官网和 GitHub 均属于 Research Connector 候选。

GitHub Trending、Hacker News、Reddit、知乎、X 等只属于信号源，不作为正式事实来源。是否接入由 `sources.yaml` 控制，不要求 Mini/V1 全部实现。

与 AI-generated text detection、Chinese AI text detection、watermarking、robustness、OOD generalization、authorship attribution 等有关的关键词不是 LoopPilot 核心架构，应写入具体论文项目的 `paper.yaml`，避免把系统锁死在单一论文主题。

## 5. 模型与外部项目处理

Ideas 中出现的 Cursor、Codex、DeepSeek 等是当时的候选实现，不应写死在架构。正式设计通过 `models.yaml` 将 planning、coding、research、writing、screening、evaluation 映射到实际模型。

`agentic-rubric-runner` 可作为 PaperLoop 评价能力的外部实现或试验场，但 LoopPilot 不依赖它才能运行。只有当它能输出结构化 Claim–Evidence、实验充分性、Reviewer concern 和 Revision Plan 时才接入；简单 1–5 分接口不进入核心评价链。

## 6. 未逐字搬运的内容

以下内容有意不逐字保留：

- 对具体产品能力和模型优先级的时效性判断；
- “很狠、很高级”等探索性措辞；
- 相互冲突的 6 层、7 层、5 层叫法；
- 将 Agent 直接等同为进程或 Prompt 函数的表达；
- 未经验证的具体价格、产品支持和自动化能力描述；
- 重复出现的总结、建议和对话衔接语。

它们要么已被结构化替代，要么不适合作为长期开发规范。

## 7. 删除 Ideas 的条件

`ideas.md` 目前不应删除，原因是当前目录没有 Git 历史，删除后会失去原始决策上下文。满足以下任一条件后可以移入归档而非直接删除：

1. 项目纳入版本控制并提交原稿；或
2. 将原稿原样移动到 `docs/archive/ideas-original.md`；或
3. 用户明确确认不再需要原始对话。

推荐最终状态：保留归档原稿，正式开发只从 `docs/development/README.md` 进入。

## 8. 覆盖结论

Ideas 的有效工程内容已经进入正式分册；没有逐字复制，但已建立保留、重命名、替代、可选或淘汰的明确关系。以后 Ideas 中出现新内容，必须先更新本追踪表，再进入正式规范。
