# 12 开发任务分解

以下任务严格按依赖顺序实施。每项完成后更新对应文档和测试。

## 1. 工程骨架

- 建立 `pyproject.toml`、`src/`、`tests/`、`config/`、`templates/`、`schemas/`、`var/`。
- 定义代码规范、错误规范和日志规范。
- 建立配置加载和测试夹具。
- 完成门：空包可安装，测试命令可运行，非法配置启动即失败。

## 2. 领域模型与状态机

- 实现 Run、Round、Task、Policy、Artifact、Source 等对象。
- 实现状态转换表和终态语义。
- 实现 `StateStore` 接口、Mini JSON 快照存储与 JSONL 事件记录。
- 完成门：模拟 Loop 能走通成功、阻塞、失败和耗尽；状态可由 `inspect` 读取。

## 3. 控制机制

- Mini 实现 Orchestrator、预算、本地锁、安全中断和幂等。
- 实现 25 分钟软截止与 30 分钟硬截止。
- 完成门：强制中断后留存可检查状态且不误报成功；重复触发不重复写。

## 4. Tool 与模型基础

- 实现安全文件、命令、Git、HTTP 读取和进程超时工具。
- 实现 Tool Registry、Connector Registry 和 Model Router。
- 实现结构化输出校验和调用记录。
- 完成门：Agent 不能绕过 Registry，模型失败不破坏状态。

## 5. Policy Engine

- 实现路径、命令、diff、依赖、删除和外部写规则。
- 实现审批报告和一次性批准范围。
- 完成门：危险场景全部拦截，合法最小操作可执行。

## 6. Artifact 与 Markdown 报告

- 实现产物目录、索引、模板和证据链接。
- 实现所有终态的报告。
- 实现每日总报告。
- 完成门：报告事实字段可由状态重建，不依赖模型臆造。

## 7. InternLoop

- 仓库观察、昨日问题读取、任务选择。
- worktree 生命周期和用户改动保护。
- 计划、最小补丁、测试链、失败分类和三轮修复。
- diff review、开发报告和 next action。
- 完成门：通过 Mini 与 V1 的 Intern 验收场景。

## 8. PaperLoop

- 论文状态、事实索引、工作副本和任务选择。
- 文献查询、元数据去重和引用核验。
- GapDiagnoser、WritingAgent 和事实保护。
- E1–E6 评价管线与 Revision Planner。
- 论文开发报告和方向建议。
- 完成门：通过 Mini 与 V1 的 Paper 验收场景。

## 9. DailyNewsLoop

- 来源适配器、增量游标、缓存和限速。
- URL/标题/内容去重，事件日期核验。
- GitHub 每日快照和 Star 增量。
- 研究、政治、财经重要性过滤。
- Inbox 路由和日报。
- 完成门：通过 Mini、V1 和 V2 的 DailyNews 验收场景。

## 10. CLI 与调度

- Mini 实现 doctor、run、run all、status、inspect。
- 实现 `run all` 固定顺序。
- 完成门：单独与顺序运行均稳定；未实现命令不注册。

## 11. V1 持久化、审批与调度扩展

- 实现 SQLite StateStore、事务检查点与 migration。
- 实现 resume、approve、reject、cancel 和 report。
- 编写 OS Scheduler 安装说明。
- 完成门：强制中断后可恢复，审批能可靠回写，锁冲突行为正确。

## 12. 可靠性与长期运行

- 故障注入、回归场景和安全扫描。
- 缓存、检查点、日志和 Artifact 保留策略。
- 连续运行测试与健康检查。
- 完成门：达到 `10-testing-and-acceptance.md` 总验收标准。

## 13. 每项任务的完成定义

每个开发任务必须同时具备：

- 实现代码；
- 单元或集成测试；
- 对应场景验证；
- 配置示例；
- 错误处理；
- Markdown 使用说明；
- 文档交叉引用更新。
