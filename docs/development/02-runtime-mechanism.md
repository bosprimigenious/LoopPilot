# 02 统一运行机制

## 1. 状态机

```text
CREATED
  ↓
LOCKING ──冲突──> DEFERRED
  ↓
OBSERVING ──输入缺失──> BLOCKED
  ↓
SELECTING ──无合适任务──> NO_ACTION
  ↓
PLANNING
  ↓
POLICY_CHECK
  ├── 需确认──> WAITING_APPROVAL
  ├── 禁止────> BLOCKED
  └── 允许
        ↓
ACTING
  ↓
EVALUATING
  ├── PASS ─────────> FINALIZING
  ├── RETRYABLE ────> DIAGNOSING → REFLECTING → REPLANNING
  ├── NEEDS_HUMAN ──> WAITING_APPROVAL
  └── FATAL ────────> FAILED

预算耗尽 ───────────> EXHAUSTED
用户取消 ───────────> CANCELLED

FINALIZING → PERSISTING → REPORTING → TERMINATED（携带 outcome）
```

流程阶段使用 `phase`；`SUCCEEDED`、`PARTIAL`、`BLOCKED` 等使用独立的 `outcome`。两者不得混为同一枚举。
图中的 DEFERRED、NO_ACTION、BLOCKED、FAILED、EXHAUSTED 和 CANCELLED 是终止意图的简写；实现时都先设置 outcome，再经过 FINALIZING、PERSISTING 和 REPORTING。

## 2. 每次 Run 的固定步骤

1. 创建 `run_id` 并校验配置。
2. 获取 Loop 锁和目标工作区锁。
3. 读取最近检查点、昨日报告和当前真实状态。
4. 建立本次隔离工作区。
5. 观察并生成带来源的上下文。
6. 从明确任务、昨日遗留和 DailyNews Inbox 选择一个任务。
7. 生成目标、范围、动作、验证和风险计划。
8. Policy Engine 检查计划。
9. 执行一个有限动作。
10. 运行确定性验证和必要的独立诊断。
11. 失败时分类原因并判断是否值得重试。
12. 有预算且有新策略时进入下一轮。
13. 固化产物、写检查点、生成 Markdown 报告并释放锁。

## 3. 30 分钟预算模型

默认配置：

```yaml
max_duration_minutes: 30
max_rounds: 3
max_model_calls: 12  # 全局回退值；各 Loop 可使用更严格配置
soft_deadline_minutes: 25
finalization_reserve_minutes: 5
```

运行到第 25 分钟后不得开启新的大动作，剩余 5 分钟用于完成当前验证、保存状态和写报告。无论任务是否完成，都必须在硬截止时间前进入可解释终态。

## 4. Round 规则

一个 Round 必须包含：

```text
计划差异 → 执行动作 → 验证证据 → 失败分类/通过结论
```

以下情况不得重试：

- 输入没有变化，计划也没有变化；
- 缺少用户决策；
- 需要越权操作；
- 预计下一轮超过剩余时间；
- 相同错误连续出现两次且没有新根因假设；
- 证据不足以判断修改方向。

## 5. 终态语义

| 终态 | 含义 |
|---|---|
| SUCCEEDED | 所有本轮强制验收项通过 |
| PARTIAL | 有有效产物，但目标未完全关闭 |
| NO_ACTION | 当前没有符合范围和预算的任务 |
| BLOCKED | 缺输入、权限、来源或用户决定 |
| FAILED | 不可恢复错误 |
| EXHAUSTED | 时间、轮次、调用或费用耗尽 |
| CANCELLED | 用户主动停止 |

只有 `SUCCEEDED` 可以在报告中写“完成”。

## 6. 锁、幂等与恢复

- 同一工作区不能被两个写 Run 同时占用。
- 相同目标、输入哈希和活动 Run 不得重复启动。
- 恢复沿用原 `run_id`，新增 `attempt_id`。
- 每个阶段完成后提交状态事务，再标记检查点有效。
- 恢复前重新计算工作区哈希；外部已修改时进入人工确认。
- 报告生成失败不撤销已验证结果，可单独重建报告。

## 7. 人工控制

```bash
looppilot status
looppilot inspect <run-id>
looppilot approve <run-id>
looppilot reject <run-id> --reason "..."
looppilot resume <run-id>
looppilot cancel <run-id>
```

审批只批准报告中列明的动作，不构成对后续未知动作的长期授权。
