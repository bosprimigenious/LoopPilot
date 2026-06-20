# 25 Mini 最小可运行路径

Mini 的目的不是展示功能数量，而是用 Mock 和小型 fixture 证明三条 Loop 共用 Runtime 后可以循环、停止、恢复、验收和报告。

## 1. 前置完成

- 领域对象和 JSON Schema；
- 状态机、预算、锁和 Artifact；
- MockAdapter；
- 三组最小 fixture；
- Markdown 报告模板；
- CLI `run/status/inspect`。

## 2. Step 1：初始化

```bash
python scripts/bootstrap_local.py --dry-run
python scripts/bootstrap_local.py
looppilot doctor
```

验收：目录和示例配置生成；重复运行不覆盖用户修改；doctor 无阻塞错误。

## 3. Step 2：Runtime Mock Run

运行一个固定失败一次、第二轮成功的 Mock Loop。

验收：状态序列合法；Round=2；第一次 Evaluation=retryable_fail；第二次 pass；Trace 与报告一致。

## 4. Step 3：Intern Mini

```bash
looppilot run intern --fixture simple_python_bug
```

验收：创建隔离 worktree；修复预置 Bug；真实 pytest 通过；diff 不越界；生成 development-report。

## 5. Step 4：Paper Mini

```bash
looppilot run paper --fixture unsupported_claim
```

验收：提取 claim；发现证据不足；使用固定可信来源修订或降低措辞；不编造引用；重新评价；生成 paper-development-report。

## 6. Step 5：DailyNews Mini

```bash
looppilot run daily-news --fixture github_star_snapshots
```

验收：离线读取两日快照；正确计算增量；去重；生成不超过上限的日报和候选任务。

## 7. Step 6：失败与恢复

- 在 ACTING 中注入中断；
- 运行 `looppilot inspect`；
- 校验工作区和检查点；
- 运行 `looppilot resume`。

验收：不重复不确定写操作；恢复生成新 attempt；最终报告包含中断历史。

## 8. Step 7：顺序运行

```bash
looppilot run all --fixture-set mini
```

验收：DailyNews → Intern → Paper 顺序正确；单 Loop 失败不污染另两个；生成每日总报告。

## 9. Step 8：替换真实 Adapter

顺序只允许：

1. Mock 模型 → 一个真实模型 Adapter；
2. Mock Git → 本地测试仓库；
3. Mock 论文源 → 一个真实元数据 Connector；
4. Mock 新闻 → 一个 RSS/API Connector；
5. 每替换一个组件，重新运行全部 Mini 回归。

禁止同时替换所有 Mock，否则失败无法归因。

## 10. Mini 通过标准

- 三条 Loop 都能运行、停止、失败和报告；
- 至少一个场景发生有效重试；
- 超时和预算能终止；
- 所有 Artifact 可追溯；
- Intern 有真实测试证据；
- Paper 有真实 Schema 和引用保护；
- DailyNews 有真实去重和快照计算；
- 任意失败不产生未解释副作用。
