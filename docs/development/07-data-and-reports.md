# 07 数据、状态与 Markdown 报告

## 1. 存储分工

| 数据 | 格式 | 原因 |
|---|---|---|
| Run、Round、状态、锁 | SQLite | 事务、查询和恢复 |
| 追加事件 | JSONL/SQLite | 审计与重放 |
| 配置 | YAML | 易读、可版本化 |
| 用户报告 | Markdown | 统一阅读与长期保存 |
| Patch/测试原始输出 | 原格式 + Markdown 摘要 | 保留证据 |

用户可见结论必须有 Markdown；内部机器状态不能只靠 Markdown 解析。

## 2. 关键对象

```text
RunRequest / RunRecord / RoundRecord / TaskCandidate / TaskPlan
PolicyDecision / ToolExecution / ModelExecution / EvaluationResult
Checkpoint / ArtifactReference / ApprovalRequest / SourceRecord
```

每个对象包含稳定 ID、Schema 版本、时间、来源和内容哈希。

## 3. 运行目录

```text
var/
├── state/
├── locks/
├── checkpoints/
├── inbox/
│   ├── intern-inbox.md
│   └── paper-inbox.md
├── artifacts/
│   ├── intern/
│   ├── paper/
│   ├── daily-news/
│   └── daily/
└── logs/
```

`var/` 不进入版本控制；配置、Schema、模板和 Skill 进入版本控制。

## 4. 报告真实性

- 状态、时间、命令、路径和测试结果由程序渲染。
- “通过”必须链接实际验证证据。
- “完成”只用于 `SUCCEEDED`。
- 未执行检查写“未执行”，不能写“无问题”。
- 模型内容标为“诊断”“推断”或“建议”。
- 外部事实链接原始来源并记录查询时间。

## 5. 每日总报告

`development-daily-report.md` 固定结构：

1. 今日最重要的结论，最多三条。
2. InternLoop：昨日问题是否解决、验证和待 Review 点。
3. PaperLoop：今日推进、证据状态和下一方向。
4. DailyNews：少量重大 GitHub、研究、政治和财经信息。
5. 等待人工处理事项。
6. 明日优先任务。
7. 时间、模型调用和费用摘要。

## 6. 保留策略

- 正式报告永久保留。
- 检查点保留最近成功 Run 和所有未关闭 Run。
- 原始抓取正文按来源许可和配置期限保存。
- 重复缓存可定期清理，但来源 URL、哈希和摘要记录保留。
- 清理操作先生成 Markdown 预览，默认不自动删除重要产物。

## 7. Artifact 命名规范

运行目录固定为：

```text
var/artifacts/YYYY-MM-DD/<loop_type>/<run_id>/
```

文件使用小写 kebab-case；轮次使用两位数字；同一 Artifact 不允许通过覆盖更新，重建时增加 `attempt-XX`。

必备文件：

```text
manifest.json
trace.jsonl
run-report.md
rounds/round-01.md
evidence/
raw/
```

Loop 专有名称以对应分册为准，如 `development-report.md`、`paper-development-report.md`、`daily-news-report.md`。Manifest 是目录真相来源，文件名不能替代 Artifact 类型。

## 8. 保留等级

| 等级 | 内容 | 默认保留 |
|---|---|---|
| permanent | 最终报告、用户 Review、接受的 patch/修订、来源索引 | 永久 |
| active | 未关闭 Run、检查点、审批 | 关闭后再判断 |
| audit | trace、调用元数据、验证日志 | 90 天后可压缩 |
| cache | 可重新抓取内容、临时解析结果 | 30 天 |
| sensitive | 可能含敏感内容的 raw transcript | 最短必要期限 |

删除前必须检查 Manifest 引用；被正式报告引用的证据不得作为孤立缓存删除。日志和原始响应进入存储前完成密钥、cookie、Authorization 和个人字段脱敏。
