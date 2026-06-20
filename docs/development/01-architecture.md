# 01 总体架构

## 1. 逻辑架构

```text
L0 Trigger
   CLI / OS Scheduler / Manual Resume（V1）
        ↓
L1 Control Plane
   Orchestrator / State Machine / Budget / Policy / Lock
        ↓
L2 Loop Definitions
   InternLoop / PaperLoop / DailyNewsLoop
        ↓
L3 Runtime Pipeline
   Observe / Select / Plan / Gate / Act / Evaluate / Reflect / Persist
        ↓
L4 Capabilities
   Agents / Skills / Tools / Connectors / Model Router
        ↓
L5 State & Evidence
   JSON/JSONL（Mini）/ SQLite + Checkpoints（V1）/ Artifacts / Markdown
```

六层表示依赖方向，不表示八个运行阶段。Evaluator 内部检查项也不是系统层级。

## 2. 运行组件

| 组件 | 唯一职责 |
|---|---|
| CLI | Mini 接收 doctor/run/status/inspect；V1 增加 resume/approve/reject/cancel |
| Scheduler Adapter | 把定时事件转换成标准 RunRequest |
| Orchestrator | 驱动流程，不负责自由推理 |
| State Machine | 只允许合法状态转换 |
| Lock Manager | 防止同一工作区重复写入 |
| Budget Manager | 限制时间、轮次、调用和费用 |
| Policy Engine | 在执行前检查路径、命令、diff 和外部操作 |
| Checkpoint Manager | V1 保存与恢复事务检查点；Mini 不实现 resume |
| Context Builder | 构建任务所需的最小上下文 |
| Planner | 选择一个任务并生成计划 |
| Worker | 执行代码或论文修改 |
| Evaluator | 依据客观证据判断结果 |
| Reflector | 把失败转化为下一轮差异化计划 |
| Artifact Manager | 管理运行产物和链接 |
| Reporter | 从事实记录渲染 Markdown |

## 3. 三条 Loop 的数据关系

```text
                         ┌──────────────────┐
                         │  DailyNewsLoop   │
                         └────────┬─────────┘
                                  │ proposed candidates
                     ┌────────────┴────────────┐
                     ▼                         ▼
             intern-inbox.md            paper-inbox.md
                     │                         │
              ┌──────▼──────┐           ┌─────▼───────┐
              │ InternLoop  │           │  PaperLoop  │
              └──────┬──────┘           └─────┬───────┘
                     │                         │
                     └────────────┬────────────┘
                                  ▼
                        Daily Summary Report
```

DailyNewsLoop 不能直接调用两个主 Loop 的 Worker。Inbox 是唯一信息桥梁。

## 4. 控制面与能力面分离

- 控制面决定现在处于哪个状态、是否可以继续、还剩多少预算。
- 能力面执行规划、代码生成、研究查询和诊断。
- 模型属于能力面，不能直接修改状态、延长预算或跳过 Policy Gate。
- Orchestrator 只接受结构化结果，不接受模型随意指定下一状态。

## 5. 默认执行策略

- 单机、单用户、顺序运行。
- 同一个 Loop 同一时刻最多一个 Run。
- InternLoop 使用 Git worktree。
- PaperLoop 使用论文工作副本或专属分支。
- DailyNewsLoop 只写自身状态、日报和 Inbox。
- `run all` 顺序为 DailyNewsLoop → InternLoop → PaperLoop。

## 6. 推荐代码结构

```text
src/loop_pilot/
├── cli.py
├── domain/        # 状态、事件、领域对象、错误
├── runtime/       # 编排、预算、锁、检查点、恢复
├── policy/        # 路径、命令、diff、外部写策略
├── loops/
│   ├── intern/
│   ├── paper/
│   └── daily_news/
├── agents/
├── skills/
├── tools/
├── connectors/
├── models/
├── storage/
└── reporting/
```

## 7. 架构不可破坏约束

1. Loop 不直接访问模型 SDK、数据库或任意 HTTP 客户端，只访问适配接口。
2. Worker 不得为自己的结果直接宣布通过。
3. 所有写动作都必须发生在计划与 Policy Gate 之后。
4. 所有重试必须有新证据或新计划。
5. 所有终态都必须能生成 Markdown 报告。
6. 任何外部写操作默认禁止。
