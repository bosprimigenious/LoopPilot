# 21 Test Fixtures 与 Golden Cases

## 1. 原则

Fixture 必须小、确定、可离线重放，不依赖当天网络和真实私人仓库。Golden Case 固定输入、允许变化字段和必须成立的断言。

## 2. 目录

```text
tests/fixtures/
├── intern/
│   ├── simple_python_bug/
│   ├── second_round_fix/
│   ├── lint_failure/
│   ├── unsafe_path_change/
│   ├── dirty_workspace/
│   └── missing_dependency/
├── paper/
│   ├── unsupported_claim/
│   ├── fake_citation/
│   ├── numeric_mismatch/
│   ├── missing_experiment/
│   ├── related_work_gap/
│   └── contradictory_evidence/
├── daily_news/
│   ├── duplicate_event/
│   ├── publish_vs_event_date/
│   ├── low_quality_signal/
│   ├── github_star_snapshots/
│   ├── no_major_news/
│   └── source_schema_changed/
└── runtime/
    ├── timeout/
    ├── interrupted_action/
    ├── stale_lock/
    ├── invalid_schema/
    └── report_failure/
```

## 3. 每个 Fixture 必须包含

```text
README.md              场景和预期
input/                 原始输入
config/                最小配置
mock_responses/        模型/网络固定响应
expected/              结构化关键结果
assertions.yaml        必须/禁止断言
```

不得对完整 Markdown 措辞做脆弱字符串比较；应验证 front matter、章节、状态、证据链接和关键事实。

## 4. Intern Golden 断言示例

`simple_python_bug`：

- 最终状态 SUCCEEDED；
- 指定测试由 fail 变 pass；
- 只修改允许文件；
- 没有 push/commit；
- development-report 链接测试证据。

`unsafe_path_change`：

- 进入 WAITING_APPROVAL 或 BLOCKED；
- 禁止路径未变化；
- 报告包含命中规则 ID。

## 5. Paper Golden 断言示例

`fake_citation`：

- 不生成伪造元数据；
- claim 标为 unsupported 或 SOURCE REQUIRED；
- 终态不是 SUCCEEDED，除非删除/降低该 claim；
- 报告保留查询和核验失败证据。

`numeric_mismatch`：

- 定位正文与表格的具体冲突；
- 不改原始实验数据；
- 请求修正文稿或人工确认。

## 6. DailyNews Golden 断言示例

`github_star_snapshots`：

- 第一天不声称 24 小时增量排名；
- 第二天正确计算差值；
- 缺失快照不按 0 处理；
- 相同仓库只生成一个候选。

`no_major_news`：

- 类别允许为空；
- 不降低阈值凑数；
- 报告说明已检查来源范围。

## 7. Golden 更新规则

Golden 变化必须说明：需求变化、Schema migration、错误修复还是模型非确定性。不得仅为了让失败测试通过而更新 expected。模型相关 Golden 使用结构化语义断言和固定 MockAdapter。
