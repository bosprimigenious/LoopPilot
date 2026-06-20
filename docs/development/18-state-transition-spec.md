# 18 状态转换规格

## 1. 决策原则

只有 Orchestrator 可以提交状态转换。Agent、Tool、Connector 和 Evaluator 返回结果，状态机依据转换表决定下一状态。

版本规则：Mini 遇到需要人工批准的动作时不持久等待，直接 `FINALIZING(outcome=blocked)` 并生成报告；`WAITING_APPROVAL`、审批状态回写和批准后恢复从 V1 开始。

## 2. 转换表

| 当前状态 | 进入条件 | 允许动作 | 成功转移 | 异常转移 | 可恢复 | 人工介入 |
|---|---|---|---|---|---:|---:|
| CREATED | RunRequest 已校验 | 创建记录 | LOCKING | FINALIZING(failed) | 是 | 否 |
| LOCKING | Run 存在 | 获取 Loop/工作区锁 | OBSERVING | FINALIZING(deferred/failed) | 是 | 否 |
| OBSERVING | 锁已持有 | 读取工作区和历史 | SELECTING | FINALIZING(blocked/failed) | 是 | 是 |
| SELECTING | Context 已生成 | 选择单任务 | PLANNING | FINALIZING(no_action/blocked) | 是 | 是 |
| PLANNING | Task 已选 | 生成 TaskPlan | POLICY_CHECK | FINALIZING(blocked/failed) | 是 | 是 |
| POLICY_CHECK | Plan 可校验 | 评估规则 | ACTING | WAITING_APPROVAL/FINALIZING(blocked) | 是 | 是 |
| WAITING_APPROVAL | 存在审批请求 | 接受/拒绝/超时 | ACTING | FINALIZING(blocked/cancelled) | 是 | 是 |
| ACTING | Plan 已允许 | 调用 Worker/Tool | EVALUATING | DIAGNOSING/FINALIZING(failed) | 是 | 是 |
| EVALUATING | 有候选结果 | 执行强制检查 | FINALIZING(succeeded) | DIAGNOSING/WAITING_APPROVAL/FINALIZING(failed) | 是 | 是 |
| DIAGNOSING | 有失败证据 | 分类根因 | REFLECTING | FINALIZING(blocked/failed) | 是 | 是 |
| REFLECTING | 根因可处理 | 形成新假设 | REPLANNING | FINALIZING(exhausted/blocked) | 是 | 是 |
| REPLANNING | 有新证据/假设 | 生成计划差异 | POLICY_CHECK | FINALIZING(exhausted/blocked) | 是 | 是 |
| FINALIZING | outcome 已确定 | 固化产物 | PERSISTING | 紧急恢复路径 | 是 | 否 |
| PERSISTING | 产物稳定 | 提交记录/Manifest | REPORTING | 紧急恢复路径 | 是 | 否 |
| REPORTING | 状态已提交 | 渲染 Markdown | TERMINATED | TERMINATED（report_status=failed） | 是 | 否 |

`RunPhase` 描述运行阶段，最终固定为 `TERMINATED`；`RunOutcome` 单独记录 SUCCEEDED、PARTIAL、NO_ACTION、DEFERRED、BLOCKED、FAILED、EXHAUSTED 或 CANCELLED。报告失败不得抹掉已经提交的任务 outcome。

## 3. Evaluation 映射

| Evaluation verdict | 前提 | 下一状态 |
|---|---|---|
| pass | 所有 blocking check 通过 | FINALIZING |
| retryable_fail | 有新失败证据且预算足够 | DIAGNOSING |
| needs_human | 缺决策或需要扩大权限 | WAITING_APPROVAL |
| fatal | 无安全恢复路径 | FINALIZING(outcome=failed) |

## 4. 预算抢占

任何非终态在操作前检查预算：

- 到软截止：禁止新 ACTING，进入 FINALIZING，结果为 PARTIAL/EXHAUSTED。
- 到硬截止：终止可终止子进程，保存最后合法检查点，结果为 EXHAUSTED。
- 模型/费用/轮次耗尽：不允许新的模型调用，进入 FINALIZING。

## 5. 人工等待

`WAITING_APPROVAL` 不占用 30 分钟执行预算；进入该状态前必须释放非必要进程和网络资源，但保持工作区锁或安全冻结。审批过期后转为 BLOCKED 并释放锁。

## 6. 恢复点

可恢复状态必须在进入后写检查点。ACTING 中断时不能假设动作未发生，恢复前必须检查文件、Git、子进程和外部副作用，再决定重做、继续或人工处理。

## 7. 禁止转换

- CREATED 直接到 ACTING；
- PLANNING 绕过 POLICY_CHECK；
- Worker 直接到 SUCCEEDED；
- FAILED 自动回到 ACTING；
- EXHAUSTED 自动延长预算；
- REPORTING 改写已经提交的验证事实。
