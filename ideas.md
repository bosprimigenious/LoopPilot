# LoopPilot 原始构想记录（历史原稿）

> 状态：已由正式开发分册取代，请勿将本文作为实现规范。
> 正式入口：[`docs/development/README.md`](docs/development/README.md)
> 迁移说明：[`docs/development/15-ideas-traceability.md`](docs/development/15-ideas-traceability.md)
> 本文保留未经整理的探索对话，用于追溯设计来源；其中的层级、模型、Agent 和产品判断可能已被修正。

---

ChatGPT




里面是怎么写的？这六个是必须的吗？对于我，两个很重要的loop，又应该如何设计更好？

你这张图其实是在讲 Loop Engineering 的“六个基础设施组件”，但重点是：
❗它们不是“必须全部具备”，而是“成熟系统才会逐步补齐的能力层”。
我给你拆清楚 + 再帮你降维成你现在真正该用的两条 loop 设计。
一、这六个东西到底是什么？必须吗？
图里的六个：
Automations
Worktrees
Skills
Connectors
Sub-agents
Memory
本质上不是“流程”，而是 Agent 系统的六种能力插件层。
1. Automations（调度层）
定时跑 loop
✔ 作用：每天自动启动
✔ 类比：cron / 任务计划程序
✔ 对你来说：非常重要
2. Worktrees（隔离工作区）
每个任务一个独立代码环境
✔ 作用：避免互相污染
✔ 类比：git worktree / docker workspace
✔ 对你来说：建议后期再加
3. Skills（能力封装）
把“提示词能力”变成可复用模块
✔ 作用：比如“写日报 skill / debug skill / paper review skill”
✔ 对你来说：很重要（但可以先不用做系统化）
4. Connectors（外部系统接入）
MCP / GitHub / Notion / DB
✔ 作用：让 loop 不局限本地文件
✔ 对你来说：后期增强项
5. Sub-agents（子智能体）
分工：写 + 查 + 评估 分离
✔ 作用：提高可靠性
✔ 对你来说：核心，但不用做很多
6. Memory（长期记忆）
上下文持久化
✔ 作用：不每次重来
✔ 对你来说：非常重要
二、结论（很重要）
这六个不是必须的：
❌ 不是“必须全部实现才能叫 Loop Engineering”
✅ 是“完整工业级系统的能力拼图”
三、对你现在最关键的问题
你现在真正关心的是：
“我只有两个 loop（Intern + Paper），应该怎么设计才是最优？”
我给你一个最适合你当前阶段的结构（极简但工程级）
四、你现在最优设计（强烈推荐）
1. 一个统一 Loop Core（必须）
Observe → Plan → Act → Check → Reflect → Report → Persist
这是唯一底座。
2. 两个 loop = 两套“配置”，不是两套系统
InternLoop（工程开发）
Observe:
  - Git diff
  - TASKS.md
  - BUGS.md
  - test logs

Plan:
  - 选 1 个 bug / feature

Act:
  - 修改代码

Check:
  - pytest / lint / build

Reflect:
  - 为什么失败 / 是否扩大问题

Report:
  - patch + dev report
👉 循环核心：
Code → Test → Debug → Code
PaperLoop（论文）
Observe:
  - draft.md
  - notes/
  - experiments.csv

Plan:
  - 选一个模块（related / method / exp）

Act:
  - 改论文

Check:
  - 逻辑 / rubric / 数据一致性

Reflect:
  - 哪里虚了 / 哪里缺证据

Report:
  - paper diff + gap report
👉 循环核心：
Write → Critique → Revise → Write
五、你真正要做的“Loop结构”（重点）
不是6个组件，而是：
⭐ 1个调度器 + 2个循环 + 3类Agent
结构图（文字版）
                Orchestrator（主控）
                         |
        -----------------------------------
        |                                 |
   InternLoop                       PaperLoop
        |                                 |
 Code Context Agent              Research Context Agent
 Dev Agent                       Writing Agent
 Test Agent                      Critic Agent
 Reporter Agent                  Reporter Agent
        |                                 |
        ----------- Memory / Logs ----------
六、你现在不需要做什么（很关键）
❌ 不要现在做：
Worktrees系统
MCP connectors全接
复杂sub-agent 10个以上
完整memory数据库系统
这些都是：
工业级 scaling 阶段才需要
七、你现在必须做什么（真正关键）
你现在只需要三件事：
✅ 1. Loop必须“能循环”
不是：
执行一次 → 输出结果
而是：
失败 → 修正 → 再执行 → 再检查 → 直到收敛
✅ 2. 必须有“停止条件”
最多 3 轮
或测试通过
或 rubric 达标
或时间超时（30min）
✅ 3. 必须有“可审计输出”
每一轮必须输出：
loop_trace.json
diff
report.md
八、给你一个非常重要的判断标准
你可以用这个判断你是不是“真正 Loop Engineering”：
❌ 不是 Loop Engineering：
AI帮你做了一次任务
你看结果
结束
✅ 是 Loop Engineering：
AI做任务
→ 失败
→ 自动修复
→ 再做
→ 再失败
→ 再修
→ 收敛
→ 输出报告
九、给你一个最终建议（非常重要）
你现在最好的路径不是：
研究6大组件
而是：
⭐ 先做这个最小系统
LoopCore（单文件）
  ↓
InternLoop（能修bug循环）
  ↓
PaperLoop（能改论文循环）
  ↓
加日志 + trace
  ↓
再扩展组件
十、一句话总结
这六个组件：
是“未来系统的能力地图”，不是“入门必须实现的模块”。
而你现在最重要的是：
先把“Code → Test → Fix” 和 “Write → Critique → Revise” 两个闭环真正跑起来。
如果你下一步想升级，我可以帮你做一件更关键的事：
👉 把你这个 LoopPilot 直接设计成 可发表论文级 system（含ablation + architecture + eval指标）

这个比单纯 demo 更狠。

我先继续探索一下，你继想想，我的两个LOOP应该如何设计，哪些层级？哪些智能体，哪些skill，查询哪些网页，如何看每日最新的问题和新闻，新的思路？如何跑通？用哪个模型作为底座？

已思考 16s
你这两个 Loop 我建议不要设计成“两个小脚本”，而是设计成一个 Daily Work Loop System：
LoopPilot
├── InternLoop：每天推进工程开发 / 实习任务
└── PaperLoop：每天推进论文调研 / 写作 / 实验缺口
两者共用同一个底座，但输入、智能体、检查标准、网页来源不同。
一、总架构：分 7 层设计
你可以把它设计成 7 层。
L0 Automation 调度层
L1 Workspace 工作区层
L2 Context 上下文层
L3 Planner 规划层
L4 Agent 执行层
L5 Evaluator 检查层
L6 Memory & Report 持久化层
L0：Automation 调度层
作用：每天自动启动。
对你来说就是：

Windows 定时唤醒
        ↓
WSL / PowerShell 启动脚本
        ↓
运行 InternLoop + PaperLoop
        ↓
半小时后你看结果
Cursor 官方 CLI 页面明确把 Cursor CLI 定位为可以用于 scripts 和 automations，例如自动更新文档、触发安全审查、构建自定义 coding agents。这个正好适合你的自动化 Loop 场景。
L1：Workspace 工作区层
作用：不要污染主项目。
第一版可以简单点：

workspace/
├── intern_project/
└── paper_project/
进阶版再做：
git worktree
临时分支
sandbox 目录
Docker 容器
InternLoop 尤其需要隔离，因为它会改代码。
PaperLoop 可以轻一点，因为它主要改 markdown、论文草稿、实验记录。

L2：Context 上下文层
作用：每轮开始前，让 Agent 知道当前状态。
InternLoop 读：

README.md
TASKS.md
BUGS.md
PROGRESS.md
git status
git diff
tests logs
CI logs
最近 Issue / PR
PaperLoop 读：
draft.md
outline.md
related_work.md
experiments.csv
notes/
paper_matrix.csv
review_comments.md
next_research_tasks.md
这一层非常重要。很多 Agent 不是不会干活，而是读错资料、漏了上下文、每天从零开始。
L3：Planner 规划层
作用：每天只选一个主任务。
InternLoop 不要让它“优化整个项目”，只让它选一个：

修一个 bug
补一个测试
改一个接口
整理一个模块
写一个 README 小节
PaperLoop 也不要让它“重写整篇论文”，只让它选一个：
Related Work
Method
Experiments
Limitations
Abstract
Introduction
每天只推进一个主目标，Loop 才能收敛。
L4：Agent 执行层
这层是你最关心的“多少个智能体”。
我的建议：

每个 Loop 4 个 Agent 就够了，再多容易乱。
InternLoop：
CodeContextAgent
DevAgent
TestAgent
ReportAgent
PaperLoop：
ResearchContextAgent
WritingAgent
CriticAgent
ReportAgent
中间再共用一个：
Orchestrator
总结构是：
Orchestrator
├── InternLoop
│   ├── CodeContextAgent
│   ├── DevAgent
│   ├── TestAgent
│   └── ReportAgent
│
└── PaperLoop
    ├── ResearchContextAgent
    ├── WritingAgent
    ├── CriticAgent
    └── ReportAgent
实现上不一定真开 9 个进程。第一版可以是 9 个 prompt 模块 / Python 函数。
L5：Evaluator 检查层
这是 Loop 是否成立的关键。
InternLoop 检查：

pytest
npm test
npm run lint
npm run build
git diff 是否过大
是否改了危险文件
PaperLoop 检查：
rubric 分数
是否编造引用
实验数据是否一致
论证是否空泛
是否真的补了缺口
是否需要人工提供数据
只要能用确定性工具检查，就不要交给模型凭感觉。
比如代码测试，优先用 pytest，而不是让模型说“看起来没问题”。

L6：Memory & Report 持久化层
每天必须留下：
daily_summary.md
intern_report.md
paper_report.md
loop_trace.json
patch.diff
next_tasks.md
Memory 不要一开始搞复杂数据库。
第一版直接用文件：

MEMORY.md
PROGRESS.md
BUGS.md
NEXT_TASKS.md
loop_trace.json
这就够了。
二、InternLoop 应该怎么设计
InternLoop 的核心循环是：
Code → Test → Debug → Code
完整流程：
启动 InternLoop
        ↓
读取工程状态
        ↓
选择今日 1 个工程主任务
        ↓
制定修改计划
        ↓
进入循环
循环内部：
DevAgent 修改代码
        ↓
TestAgent 跑测试 / lint / build
        ↓
判断是否通过
        ↓
通过：跳出循环
失败：分析错误 → 调整计划 → 再次修改代码
停止条件：
测试通过
或最多 3 轮
或超过 30 分钟
或修改范围过大
或发现需要人工确认
最终输出：
patch.diff
test_result.md
intern_report.md
next_tasks.md
loop_trace.json
InternLoop 的 Agent
1. CodeContextAgent
职责：
读项目结构
读 TASKS / BUGS / README
读 git diff
找相关代码文件
总结当前工程状态
输出：
{
  "current_status": "",
  "main_task_candidates": [],
  "relevant_files": [],
  "risks": []
}
2. DevAgent
职责：
根据计划修改代码
只做最小变更
补必要测试
生成 patch
限制：
不 push
不 commit
不部署
不删文件
不改 .env
不碰密钥
3. TestAgent
职责：
运行测试
读取报错
判断失败类型
输出错误归因
错误类型可以分：
语法错误
测试断言失败
依赖缺失
环境问题
逻辑问题
任务范围过大
4. ReportAgent
职责：
写工程日报
写修改摘要
写剩余风险
写明天建议
三、InternLoop 需要哪些 Skill
第一版做 6 个 Skill 就够。
repo-map-skill
issue-triage-skill
minimal-patch-skill
test-debug-skill
risk-gate-skill
daily-report-skill
1. repo-map-skill
输入项目目录，输出：
项目结构
核心模块
测试目录
配置文件
入口文件
2. issue-triage-skill
输入 TASKS / BUGS / Issue，输出：
最值得做的任务
任务优先级
预计文件范围
3. minimal-patch-skill
约束 DevAgent：
只做最小可验证改动
不顺手重构
不扩大范围
4. test-debug-skill
根据测试失败日志，判断：
失败原因
是否能继续修
下一轮修改方向
5. risk-gate-skill
检测危险操作：
删除文件
改密钥
改生产配置
大范围重构
超过 diff 行数限制
6. daily-report-skill
输出固定格式日报：
今日任务
完成内容
测试结果
风险
明日建议
人工确认项
四、InternLoop 每天查哪些网页 / 信息源
InternLoop 不要乱搜全网，主要查这些：
GitHub Issues / PR
GitHub Actions / CI 日志
依赖库官方 changelog
框架官方文档
GitHub Security Advisories
Stack Overflow / GitHub Discussions
项目技术栈相关 release notes
如果是你自己的项目，比如 WitWay / agentic-rubric-runner，则重点查：
GitHub 仓库 Issue
依赖库更新
FastAPI / React / Vite / pytest / LangChain / MCP / A2A 相关文档
OpenAI / Cursor / Anthropic 工具更新
Cursor CLI 现在已经明确支持 headless 脚本和自动化工作流，也支持 shell mode 和 GitHub Actions 集成这类方向，所以它很适合作为 InternLoop 的执行底座。
五、PaperLoop 应该怎么设计
PaperLoop 的核心循环是：
Write → Critique → Revise → Write
完整流程：
启动 PaperLoop
        ↓
读取论文状态
        ↓
检索最新论文 / 新闻 / 项目
        ↓
判断当前最大缺口
        ↓
选择今日 1 个论文模块
        ↓
进入循环
循环内部：
WritingAgent 修改论文模块
        ↓
CriticAgent 用 rubric 检查
        ↓
判断是否达标
        ↓
达标：跳出循环
不达标：指出问题 → 调整写法 → 再修改
停止条件：
rubric 达到阈值
或最多 3 轮
或发现缺真实引用
或发现缺实验数据
或超过 30 分钟
最终输出：
revised_draft.md
paper_report.md
gap_analysis.md
next_research_tasks.md
literature_matrix.csv
loop_trace.json
六、PaperLoop 的 Agent
1. ResearchContextAgent
职责：
读取论文草稿
读取实验结果
读取已有文献笔记
读取最新论文摘要
更新 research context
输出：
{
  "paper_status": "",
  "weak_sections": [],
  "new_related_papers": [],
  "experiment_gaps": [],
  "today_focus": ""
}
2. LiteratureScoutAgent
这个可以和 ResearchContextAgent 合并，但我建议 PaperLoop 里保留一个轻量 scout。
职责：

每天查最新论文
查新数据集
查新 benchmark
查新 GitHub 项目
查社区争议
3. WritingAgent
职责：
只修改一个论文模块
不编造引用
不编造实验结果
保持和实验数据一致
4. CriticAgent
职责：
模拟审稿人
检查逻辑漏洞
检查证据不足
检查 contribution 是否清楚
检查实验是否支撑 claim
5. ReportAgent
职责：
写科研日报
写缺口清单
写下一步任务
更新 literature matrix
七、PaperLoop 需要哪些 Skill
第一版做 8 个 Skill。
paper-scout-skill
paper-screening-skill
structured-summary-skill
literature-matrix-skill
claim-evidence-check-skill
rubric-review-skill
experiment-gap-skill
paper-report-skill
1. paper-scout-skill
每天搜索：
arXiv
ACL Anthology
OpenReview
Papers with Code
Semantic Scholar
Hugging Face Papers
GitHub trending
相关会议官网
2. paper-screening-skill
过滤掉不相关论文。
输出：

强相关
中相关
弱相关
不相关
3. structured-summary-skill
每篇论文固定总结：
任务
方法
数据集
指标
优点
缺点
和我论文的关系
可引用位置
4. literature-matrix-skill
更新矩阵：
paper
task
method
dataset
metric
strength
weakness
relation_to_our_work
citation_usage
5. claim-evidence-check-skill
检查论文里每个 claim 有没有证据：
claim
supporting experiment
supporting citation
risk
6. rubric-review-skill
打分：
novelty
clarity
technical soundness
experiment completeness
related work coverage
robustness
limitations
7. experiment-gap-skill
告诉你缺什么实验：
baseline
ablation
OOD
robustness
efficiency
case study
error analysis
human evaluation
8. paper-report-skill
输出：
今日新增论文
今日改了什么
当前最大问题
下一步实验
下一步写作任务
八、PaperLoop 每天查哪些网页
你这个方向如果围绕 TextGuard / AI-generated text detection，可以设置这些关键词：
AI-generated text detection
LLM-generated text detection
Chinese AI-generated text detection
machine-generated text detection
LLM watermarking
text watermarking
adversarial robustness detection
OOD generalization AI text detection
authorship attribution LLM
synthetic text detection
推荐信息源分三类。
A 类：硬信息源，必须看
arXiv cs.CL / cs.AI / cs.LG
ACL Anthology
OpenReview
Papers with Code
Semantic Scholar
Hugging Face Papers
GitHub repositories
NeurIPS / ICLR / ACL / EMNLP 官网
这些适合作为正式论文依据。
B 类：工程信号源，可参考
GitHub Trending
Hugging Face models / datasets
OpenAI / Anthropic / Google DeepMind 官方博客
Cursor / Codex / Claude Code changelog
这些适合发现新工具、新方法、新 benchmark。
C 类：趋势信号源，只能参考
X / Twitter
Hacker News
Reddit
知乎
即刻
公众号
Bilibili
这些适合发现“大家最近在讨论什么”，但不能直接当论文依据。
九、如何看每日最新问题和新闻
我建议不要让 PaperLoop 和 InternLoop 直接乱看新闻，而是加一个单独的：
DailyScout
DailyScout 每天跑一次，输出：
engineering_news.md
research_news.md
tooling_news.md
DailyScout 的流程
搜索最新来源
        ↓
过滤重复内容
        ↓
判断和我的项目是否相关
        ↓
分成工程 / 论文 / 工具三类
        ↓
写入今日简报
        ↓
给 InternLoop / PaperLoop 提供候选任务
DailyScout 输出格式
今日工程相关：
1. Cursor CLI 新功能 / bug
2. Codex 工具更新
3. 某依赖安全问题

今日科研相关：
1. 新论文：xxx
2. 新 benchmark：xxx
3. 新争议：AI text detection 是否可靠

今日可行动建议：
1. InternLoop：检查依赖更新
2. PaperLoop：补一段关于 watermarking 的 related work
这比让两个 Loop 各自乱搜更稳。
十、如何跑通：最小可行版本
不要一开始做复杂系统。第一版这样就行。
目录结构
LoopPilot/
├── loop_core.py
├── run_daily.py
├── loops/
│   ├── intern_loop.py
│   └── paper_loop.py
├── skills/
│   ├── repo_map.py
│   ├── test_debug.py
│   ├── paper_scout.py
│   ├── rubric_review.py
│   └── report_writer.py
├── workspaces/
│   ├── intern_project/
│   └── paper_project/
├── memory/
│   ├── intern_memory.md
│   └── paper_memory.md
└── outputs/
    ├── intern_report.md
    ├── paper_report.md
    ├── daily_summary.md
    └── loop_trace.json
命令
python run_daily.py --mode intern --max-rounds 3
python run_daily.py --mode paper --max-rounds 3
python run_daily.py --mode all --max-rounds 3
每天自动跑
Windows 任务计划程序：
09:00 唤醒
09:05 运行 run_daily.py --mode all
09:35 你 SSH 查看结果
十一、用哪个模型作为底座
这里要分任务，不要一个模型干所有事。
最推荐组合
InternLoop 开发主力：Cursor CLI / Codex
PaperLoop 写作主力：GPT-5.5 / Codex / 高质量模型
DailyScout 批量检索总结：DeepSeek API 或便宜模型
Evaluator：优先用确定性工具，不优先用模型
具体建议
InternLoop 底座
优先级：
1. Cursor CLI（你有 Pro 额度，适合 Windows 自动跑）
2. Codex（Mac 上稳，适合你自己主控）
3. DeepSeek API（不建议第一版做代码主力）
原因：
Cursor CLI 官方就面向终端、自动化脚本、headless 工作流，适合你“Windows 自动启动后跑工程 loop”的目标。

Codex 官方定位是 OpenAI 的 AI coding partner，可用于构建和交付代码，也支持 macOS 和 Windows。

PaperLoop 底座
优先级：
1. GPT-5.5 / ChatGPT / Codex：写作、批判、结构优化
2. DeepSeek reasoner：低成本分析和批量总结
3. DeepSeek chat：普通摘要、格式化、日报
DeepSeek API 官方文档显示它兼容 OpenAI/Anthropic 风格接口，适合接入脚本。 DeepSeek 的 API 价格也比较低，适合做大量论文摘要、日报、结构化提取这类批处理；官方价格页显示 deepseek-chat 和 deepseek-reasoner 都按输入/输出 token 计费。
我的最终模型建议
你现在最现实的选择：
第一阶段：
InternLoop：Cursor CLI
PaperLoop：GPT / Codex 手动或半自动
DailyScout：先不用 API，手动搜索 + 模型总结

第二阶段：
InternLoop：Cursor CLI 自动跑
PaperLoop：GPT / DeepSeek API 混合
DailyScout：DeepSeek API 批量总结

第三阶段：
统一成 LoopPilot：
Orchestrator 用强模型
Worker 用 Cursor/Codex
Scout 用 DeepSeek
Evaluator 用测试和 rubric
十二、两个 Loop 最终应该长这样
InternLoop 最终版
每天 09:00 自动启动
        ↓
CodeContextAgent 读取项目状态
        ↓
Planner 选 1 个任务
        ↓
DevAgent 修改代码
        ↓
TestAgent 跑测试
        ↓
失败则 Debug → 再修改，最多 3 轮
        ↓
成功或停止
        ↓
ReportAgent 生成日报、patch、trace
        ↓
你人工 Review
核心循环：
Code → Test → Debug → Code
PaperLoop 最终版
每天 09:30 自动启动
        ↓
DailyScout 查新论文、新工具、新讨论
        ↓
ResearchContextAgent 读取草稿和实验
        ↓
Planner 选 1 个论文模块
        ↓
WritingAgent 修改
        ↓
CriticAgent 用 rubric 检查
        ↓
不达标则 Critique → Revise，最多 3 轮
        ↓
成功或停止
        ↓
ReportAgent 生成论文日报、缺口分析、下一步任务
        ↓
你人工 Review
核心循环：
Write → Critique → Revise → Write
十三、我给你的最终设计建议
你不要做成：
InternLoop 一个项目
PaperLoop 一个项目
而是做成：
LoopPilot 一个框架
InternLoop 和 PaperLoop 是两个配置
最小版本：
LoopCore
├── Scheduler
├── ContextLoader
├── Planner
├── Worker
├── Evaluator
├── Reflector
├── Reporter
└── Memory
然后：
InternLoop = LoopCore + Code Skills + Test Evaluator
PaperLoop = LoopCore + Research Skills + Rubric Evaluator
这才是最漂亮的设计。
一句话概括你的项目定位：

LoopPilot 是一个每日自动运行的 AI 工作闭环系统，把工程开发和科研写作拆成可观察、可验证、可恢复的循环任务，并通过报告、日志和人工 Review 保证结果可靠。
这个方向非常适合你。它不是简单“用 AI 写代码/写论文”，而是把你每天的工作变成一个真正能运行、能评估、能积累的系统。

第三阶段：
统一成 LoopPilot：
Orchestrator 用强模型
Worker 用 Cursor/Codex
Scout 用 DeepSeek
Evaluator 用测试和 rubric；你真的觉得我的rubric是可以用的？我感觉还是太低级了

已思考若干秒
你这个直觉是对的。
我前面说的：

Evaluator 用测试和 rubric
这里的 rubric 不能只是“打几个 1-5 分”那种低级 rubric。那种只能做第一版 demo，用来证明流程能跑；但如果你真想把 PaperLoop 做得有研究价值、甚至和 agentic-rubric-runner 结合，普通 rubric 确实太弱。
更准确的说法应该是：

代码 loop 可以用确定性测试做 evaluator；论文 loop 不能只靠普通 rubric，应该用“多层评估器”。
一、普通 rubric 为什么低级？
比如这种：
Novelty: 1-5
Clarity: 1-5
Related Work: 1-5
Experiment: 1-5
Writing: 1-5
它的问题是：
1. 太主观
2. 不可复现
3. 不知道具体哪里错
4. 不知道怎么改
5. 容易被模型自夸骗过去
6. 不能检查实验结果真假
7. 不能判断 claim 是否有 evidence 支撑
它只能回答：
看起来怎么样？
但你真正需要的是：
哪里缺？为什么缺？证据是什么？下一步怎么补？
所以你感觉它低级，是对的。
二、PaperLoop 的 Evaluator 应该升级成 5 层
我建议你不要叫简单 rubric，而是叫：
Paper Evaluation Stack
或者：
Multi-layer Paper Evaluator
它至少分 5 层。
第 1 层：结构完整性检查
检查论文有没有基本结构。
Abstract 是否说明问题、方法、结果、贡献
Introduction 是否说明动机和 gap
Related Work 是否按主题组织
Method 是否可复现
Experiments 是否支撑 claim
Limitations 是否诚实
Conclusion 是否没有夸大
这一层比较机械，可以自动检查。
输出不是分数，而是：

{
  "missing_sections": [],
  "weak_sections": [],
  "overlong_sections": [],
  "underdeveloped_sections": []
}
第 2 层：Claim–Evidence 检查
这是最关键的一层。
论文里每一句强 claim 都要对应证据。

例如：

Claim: Our method improves OOD generalization.
Evidence: OOD benchmark AUC = 0.9179.
Risk: Need comparison with stronger baselines.
你应该让 evaluator 输出：
{
  "claim": "Our method improves OOD generalization.",
  "evidence": "OOD AUC 0.9179 on PKU+M4.",
  "support_level": "partial",
  "risk": "Needs stronger baseline comparison.",
  "action": "Add baseline table and discuss distribution shift."
}
这个比普通 rubric 强很多。
因为它不是打分，而是检查论文的“论证链”。

第 3 层：Experiment Sufficiency 检查
这层专门看实验够不够。
对你的 TextGuard 类论文，可以检查：

主结果有没有
OOD 有没有
鲁棒性有没有
消融实验有没有
跨模型泛化有没有
跨数据集泛化有没有
对抗攻击有没有
效率分析有没有
错误案例有没有
人工分析有没有
和强 baseline 比较有没有
输出：
{
  "required_experiments": [
    "main benchmark",
    "OOD generalization",
    "ablation",
    "robustness",
    "baseline comparison"
  ],
  "present": [
    "main benchmark",
    "OOD generalization",
    "robustness"
  ],
  "missing": [
    "ablation",
    "stronger baseline comparison",
    "error analysis"
  ],
  "priority": "Add ablation first, then stronger baselines."
}
这才是 PaperLoop 真正有用的地方。
第 4 层：Related Work Coverage 检查
普通 rubric 只会说：
Related work is weak.
高级 evaluator 应该说：
缺哪一类相关工作
每类应该引用谁
当前方法和它们的区别是什么
哪些地方容易被审稿人质疑
比如你的方向可以分：
AI-generated text detection
Chinese text detection
Stylometric / linguistic features
Watermarking methods
Robustness and adversarial attacks
OOD generalization
LLM attribution / authorship
输出：
{
  "covered_topics": [
    "AI-generated text detection",
    "Chinese text detection"
  ],
  "missing_topics": [
    "watermarking",
    "adversarial robustness",
    "OOD generalization"
  ],
  "reviewer_risk": "Reviewer may say related work ignores watermarking and robustness literature.",
  "recommended_revision": "Add a subsection comparing detection-based and watermarking-based paradigms."
}
这个就比 1-5 分高级很多。
第 5 层：Reviewer Simulation 检查
最后一层模拟审稿人。
不是打分，而是生成：

Strong Reject / Reject / Borderline / Weak Accept / Accept
并且必须给出：
最可能的 3 条负面 review
最可能的 3 条 rebuttal point
最应该补的 3 个实验
最应该改的 3 个段落
输出类似：
{
  "likely_decision": "Borderline",
  "main_concerns": [
    "OOD improvement is promising but baseline comparison is insufficient.",
    "The contribution of LPP and CDFI is not fully isolated.",
    "Robustness evaluation needs clearer attack settings."
  ],
  "required_fixes": [
    "Add ablation for LPP, CDFI, GA-AT.",
    "Add stronger detector baselines.",
    "Clarify PGD attack configuration."
  ],
  "rebuttal_preparation": [
    "Prepare explanation for Chinese-specific linguistic profiles.",
    "Prepare table comparing with multilingual detectors.",
    "Prepare robustness failure case analysis."
  ]
}
这才是真正对你有价值的 evaluator。
三、所以 PaperLoop 不应该叫 rubric evaluator
我建议改名：
PaperJudge
或者：
ResearchCritic
内部不是一个 rubric，而是：
ResearchCritic
├── StructureChecker
├── ClaimEvidenceChecker
├── ExperimentSufficiencyChecker
├── RelatedWorkCoverageChecker
├── ReviewerSimulator
└── RevisionPlanner
这样就高级很多。
四、PaperLoop 的真实循环应该是这样
不是：
写论文 → rubric 打分 → 修改
而是：
写论文
  ↓
结构检查
  ↓
Claim-Evidence 检查
  ↓
实验充分性检查
  ↓
Related Work 覆盖检查
  ↓
Reviewer Simulation
  ↓
生成 Revision Plan
  ↓
WritingAgent 按 Revision Plan 修改
  ↓
再次检查
循环核心是：
Revise → Diagnose → Plan Fixes → Revise
而不是：
Write → Score → Rewrite
这两个水平差很多。
五、你可以把 PaperLoop 设计成这样
PaperLoop
├── ResearchScout
│   └── 查新论文、新 benchmark、新争议
│
├── PaperStateReader
│   └── 读取 draft、notes、experiments、matrix
│
├── GapDiagnoser
│   └── 找结构缺口、实验缺口、引用缺口
│
├── WritingAgent
│   └── 按 gap 修改一个章节
│
├── ResearchCritic
│   ├── StructureChecker
│   ├── ClaimEvidenceChecker
│   ├── ExperimentChecker
│   ├── RelatedWorkChecker
│   └── ReviewerSimulator
│
├── RevisionPlanner
│   └── 生成下一轮修改计划
│
└── ReportAgent
    └── 生成 paper_report、next_tasks、trace
六、这个 evaluator 应该怎么落地？
第一版不用复杂。
你可以先做 3 个文件：

rubrics/
├── structure_check.yaml
├── claim_evidence_check.yaml
├── experiment_sufficiency_check.yaml
然后每次 PaperLoop 跑的时候，输出：
outputs/
├── structure_report.json
├── claim_evidence_report.json
├── experiment_gap_report.json
├── reviewer_simulation.md
└── paper_revision_plan.md
也就是说，先不要追求一个总分，而是追求“诊断报告”。
七、真正高级的评价不是分数，而是诊断
你现在要记住一句：
PaperLoop 的 Evaluator 不应该主要打分，而应该主要诊断。
低级 evaluator：
这篇论文 3.8/5。
高级 evaluator：
你的 OOD claim 只有部分证据支撑；
缺少 LPP/CDFI/GA-AT 的独立消融；
Related Work 忽略 watermarking 和 robustness；
Method 部分没有说明 CDFI 的输入输出；
建议明天优先补 ablation 表格和 robustness 设置说明。
后者才是真正能推进论文的东西。
八、InternLoop 和 PaperLoop 的 Evaluator 不一样
InternLoop 的 evaluator 可以很硬：
测试过了就是过了
build 失败就是失败
lint 报错就是报错
PaperLoop 的 evaluator 不能这么硬，只能做：
证据链检查
结构诊断
实验充分性判断
审稿风险预测
所以两个 Loop 的 evaluator 设计完全不同。
九、你可以把它和 agentic-rubric-runner 结合
你的 agentic-rubric-runner 如果只是：
输入文档 → 按 rubric 打分 → 输出分数
那确实普通。
但如果升级成：

输入文档
  ↓
抽取 claims
  ↓
匹配 evidence
  ↓
检查 experiment sufficiency
  ↓
模拟 reviewer
  ↓
生成 revision plan
  ↓
自动修订
  ↓
再次诊断
那就非常有价值。
它可以叫：

agentic-rubric-runner
但实际上做的是：
Document-grounded diagnostic evaluation and iterative revision loop
这个定位就高级很多。
十、我的结论
你说得对：
简单 rubric 太低级，不能作为 PaperLoop 的核心 evaluator。
正确方案是：
Evaluator = Multi-layer ResearchCritic
包括：
1. 结构完整性检查
2. Claim-Evidence 检查
3. 实验充分性检查
4. Related Work 覆盖检查
5. Reviewer Simulation
6. Revision Plan 生成
最终 PaperLoop 应该不是：
写 → 打分 → 改
而是：
写 → 诊断 → 定位缺口 → 制定修订计划 → 改 → 再诊断
这才是你这个系统真正应该做的东西。
