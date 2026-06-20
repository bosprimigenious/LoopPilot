# 03 InternLoop 开发闭环

## 1. 实际目标

InternLoop 在每天约 30 分钟内，优先关闭昨天留下的一个开发问题。它必须给出二选一的可靠结果：

1. 一个经过真实测试的最小修复；
2. 一个证据充分的阻塞诊断，明确今天最应该人工处理什么。

“阅读了仓库”“给出建议”或“生成了代码但没测试”都不算解决问题。

## 2. 输入顺序

1. 用户显式指定的任务。
2. 昨日 `next-actions.md` 中未关闭且最高优先的问题。
3. 当前 CI、test、lint 或 build 的真实失败。
4. `TASKS.md`、`BUGS.md`、Issue 或 PR 中的明确任务。
5. `intern-inbox.md` 中通过核验的 DailyNews 候选。

## 3. 任务选择门槛

所选任务必须：

- 可用一句话描述完成状态；
- 有明确相关文件或可通过搜索定位；
- 有至少一种可执行验证；
- 预计能在三轮和 30 分钟内产生结果；
- 不依赖未获得的业务决策；
- 不要求 push、部署或生产操作。

大任务必须切成一个可独立验证的子问题。

## 4. 完整流程

```text
读取昨日报告和当前任务
  ↓
检查 git status，保护用户未提交改动
  ↓
创建独立 worktree
  ↓
读取仓库说明、相关代码、测试和错误日志
  ↓
运行轻量基线验证
  ↓
选择一个问题并写 plan.md
  ↓
检查允许路径、禁止命令、diff 上限和风险
  ↓
Round 1：最小修改 → 定向测试
  ↓失败
日志归因 → 新根因假设 → Round 2
  ↓失败
缩小问题或修正策略 → Round 3
  ↓
运行受影响模块测试、lint/type/build 和 diff review
  ↓
生成 development-report.md 与 next-actions.md
```

## 5. 逻辑角色

| 角色 | 负责 | 不负责 |
|---|---|---|
| CodeContextAgent | 定位任务、相关文件、基线和风险 | 修改代码 |
| EngineeringPlanner | 选择单任务、拆步骤、定义验证 | 执行动作 |
| DevAgent | 在批准范围内实现最小修改 | 宣布测试通过 |
| TestDiagnoser | 根据真实日志分类失败和根因 | 隐藏失败 |
| EngineeringReflector | 生成不同于上一轮的修正策略 | 无限重试 |

它们是顺序调用的逻辑角色，不要求多个进程。

## 6. 代码修改规则

- 修改前记录基线 commit 和工作区状态。
- 只触碰计划列出的路径；新增路径必须重新过 Policy Gate。
- 优先修根因，不得删除失败测试或吞掉异常来制造通过。
- 行为改变必须补充测试。
- 不做无关格式化、重命名和重构。
- 不覆盖用户已有修改，不改密钥、`.env` 和生产配置。
- 新依赖、迁移、删除文件和大规模 diff 必须人工确认。

## 7. 验证顺序

1. 本问题的最小复现或定向测试。
2. 受影响模块测试。
3. lint/format check。
4. 类型检查。
5. 必要 build。
6. 时间允许时运行扩大范围回归。
7. `git diff --check`、敏感路径和无关 diff 检查。

项目没有配置某项时写 `NOT_CONFIGURED`，不得写“通过”。

## 8. 失败分类与动作

| 分类 | 自动动作 |
|---|---|
| CODE_ERROR | 依据编译/运行日志修正，可重试 |
| TEST_ASSERTION | 比较预期与实际，可重试 |
| REGRESSION | 定位受影响路径，能缩小则重试 |
| DEPENDENCY | 默认停止；安装或升级需确认 |
| ENVIRONMENT | 停止并给出环境修复命令 |
| TOOL_FAILURE | 重试工具一次，仍失败则停止 |
| SCOPE_ERROR | 缩小一次；仍过大则停止 |
| POLICY_VIOLATION | 立即停止或请求审批 |
| AMBIGUOUS_TASK | 请求用户决策 |

## 9. 完成验收

- 任务验收条件全部满足。
- 强制验证命令通过。
- 没有新增未解释失败。
- diff 在批准范围内。
- 用户已有工作没有受损。
- 报告清楚说明修改逻辑、验证证据和剩余风险。

## 10. Markdown 产物

```text
artifacts/intern/<run_id>/
├── context.md
├── plan.md
├── rounds/round-01.md
├── test-report.md
├── diff-summary.md
├── risk-report.md
├── development-report.md
└── next-actions.md
```

`development-report.md` 顶部必须直接回答：

- 昨天哪个问题被处理；
- 是否真的解决；
- 验证证据是什么；
- 今天上班后最需要关注的一件事是什么。
