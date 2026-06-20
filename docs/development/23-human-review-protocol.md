# 23 人工 Review 协议

## 1. Review 决策

```text
ACCEPT             接受结果并关闭本轮任务
REJECT             拒绝结果，必须给原因
NEEDS_MORE_INFO    要求补充证据，不批准新写操作
RUN_NEXT_ROUND     在明确范围和预算下继续一轮
MANUAL_FIX         用户接管，Loop 停止自动修改
ARCHIVE            结果仅留档，不转成任务
```

决策必须写入 RunRecord，并更新相关 Task/Inbox 状态。

## 2. 通用 Review 页面

Review 报告首屏只显示：

- 目标与最终状态；
- 改动/结论摘要；
- 强制验证；
- 未通过与未运行检查；
- 风险；
- 需要批准的确切动作；
- 推荐决策及其理由。

## 3. InternLoop Review

用户依次判断：

1. Patch 是否真的对应昨日问题？
2. 改动范围是否合理？
3. 定向测试和必要回归是否通过？
4. 是否需要额外人工测试？
5. 是否接受 patch 并自行 commit？
6. 任务是否关闭，还是生成新的 next action？

`ACCEPT` 不自动 commit/push。它只把 Run 标为用户接受并把任务标记完成。

## 4. PaperLoop Review

用户依次判断：

1. 修订是否保持原意和事实？
2. 引用是否值得采纳且已核验？
3. Claim–Evidence 状态是否合理？
4. 缺实验是否应加入研究计划？
5. Reviewer concern 是否真实重要？
6. 下一方向是否进入 next-actions？

引用只有在 EvidenceItem 达到配置的 verification level 后才能接受进入正式文稿。

## 5. DailyNews Review

每个条目只能选择：

- `ROUTE_INTERN`
- `ROUTE_PAPER`
- `WATCH`
- `IGNORE`
- `ARCHIVE`

路由会创建候选任务，不会立即运行主 Loop。用户反馈应记录过滤原因，用于调整规则，而不是未经控制地训练模型。

## 6. RUN_NEXT_ROUND 限制

- 必须说明新证据、新目标或计划差异。
- 重新经过 Policy Gate。
- 使用新 attempt/round 记录。
- 不得突破单日硬成本；必要时排到下一次运行。

## 7. Review 超时

审批请求默认有过期时间。过期后 Run 转为 BLOCKED，释放工作区锁并保留检查点。系统不得把“用户没有回复”解释为同意。
