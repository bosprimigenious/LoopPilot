# 04 PaperLoop 论文推进闭环

## 1. 实际目标

PaperLoop 每天约 30 分钟，只推进论文最重要的一个缺口。它必须产生以下至少一种可靠结果：

- 修订一个有明确边界的论证单元；
- 补齐并核验一组相关引用；
- 发现并定位 claim 与 evidence 的断裂；
- 给出下一项最值得做的实验及理由；
- 把模糊研究方向收束成可执行任务。

它不以字数增长为目标。

## 2. 输入

- 当前论文草稿与章节结构；
- BibTeX、文献矩阵和已核验论文；
- 原始实验表、图、指标和生成脚本；
- 导师、合作者或审稿意见；
- 昨日 `next-actions.md`；
- `paper-inbox.md` 中已核验的最新论文和研究信号。

## 3. 今日方向选择

选择优先级：

1. 会导致核心结论不成立的证据或实验问题。
2. 会被审稿人直接指出的主要缺口。
3. 论文主贡献表达不清或方法不可复现。
4. 缺失的重要 baseline、ablation、泛化或鲁棒性实验。
5. Related Work 的关键类别或引用缺失。
6. 普通语言、格式和局部表达问题。

前五类未处理时，不应把时间花在普通润色上。

## 4. 完整流程

```text
读取昨日报告、草稿、文献和实验事实
  ↓
建立只读事实索引与可写论文副本
  ↓
诊断当前最重要缺口
  ↓
必要时查询正式论文、作者页面、代码与数据集
  ↓
核验候选引用是否真的支持当前论点
  ↓
生成 revision-plan.md
  ↓
修改一个章节或一个 claim-evidence 单元
  ↓
结构检查 → Claim-Evidence → 实验充分性
  → Related Work → 数字/引用一致性 → Reviewer Simulation
  ↓
可修复：生成下一轮最小计划并重写
缺证据/实验/决策：停止，明确下一研究方向
  ↓
生成 paper-development-report.md
```

## 5. 引用查询与核验

引用处理必须经历：

```text
发现候选 → 获取元数据 → 去重 → 阅读摘要
→ 必要时阅读正文 → 定位支持语句 → 判断支持强度
→ 记录可引用位置 → 写入文献矩阵 → 才允许进入正文
```

每条引用至少记录：

- 标题、作者、年份、venue/状态；
- DOI、arXiv ID 或稳定 URL；
- 查询日期；
- 支持的论文 claim；
- 证据来自摘要还是正文；
- 支持程度与限制；
- 推荐引用位置。

无法核验的引用写 `[SOURCE REQUIRED]`，不得补造。

## 6. Research Evaluation Pipeline

### E1 结构完整性

检查章节目标、方法复现信息、实验与结论闭合。

### E2 Claim–Evidence

为强主张建立：

```text
Claim → Evidence → Location → SUPPORTED/PARTIAL/UNSUPPORTED/CONTRADICTED
```

### E3 实验充分性

根据论文任务检查主结果、强 baseline、ablation、泛化、鲁棒性、效率、误差分析和统计可靠性。清单必须可配置，不能机械套用。

### E4 Related Work Coverage

检查主题类别、关键工作、差异描述和引文真实性。

### E5 一致性

检查摘要、正文、表格、结论、实验文件、术语和 citation key。

### E6 Reviewer Simulation

只基于 E1–E5 的证据提出主要质疑、对应位置、修复类型和优先级。模拟 verdict 只是风险信号，不决定完成。

### E7 Revision Planning

它位于评价之后，消费诊断结果并选择下一轮最小修订，不算评价器本身。

## 7. 事实保护

- 原始实验数据只读。
- 新数字必须能追溯到输入、脚本、命令和输出。
- 新闻和社区讨论只能发现方向，不能直接支撑论文结论。
- “最新、首次、显著优于、普遍有效”必须单独核验。
- 不确定时降低措辞强度，不能用流畅语言掩盖不确定性。
- 修订不得悄悄改变论文核心假设或实验设定。

## 8. 30 分钟内应输出的研究判断

报告开头必须回答：

1. 今天推进了论文哪一个关键点？
2. 哪个 claim 得到加强、削弱或仍无证据？
3. 当前最缺的是写作、引用、实验还是研究决策？
4. 下一次最值得推进的方向是什么？
5. 为什么它比其他候选方向更重要？

## 9. 完成验收

- 选定缺口已实际处理。
- 相关强制评价通过。
- 没有新增 unsupported claim。
- 没有新增不可核验引用和数字。
- 修改与其他章节一致。
- 下一方向基于诊断证据，而非模型随口建议。

## 10. Markdown 产物

```text
artifacts/paper/<run_id>/
├── paper-state.md
├── source-dossier.md
├── gap-diagnosis.md
├── revision-plan.md
├── claim-evidence-report.md
├── experiment-gap-report.md
├── related-work-report.md
├── consistency-report.md
├── reviewer-simulation.md
├── paper-development-report.md
└── next-actions.md
```
