# LoopPilot 中文文档（认知层）

这里是用**中文**理解 LoopPilot 的入口。代码、CLI、配置、验收文件名保持英文——见 [英文接口规格](../en-core.md)。

文档维护规则见 [10-中英文文档管理.md](10-中英文文档管理.md)。

## 推荐阅读顺序

1. [00-快速开始](00-快速开始.md) — 安装、跑通、30 秒命令
2. [01-系统是什么](01-系统是什么.md) — 目标、边界、产出
3. [02-三条循环](02-三条循环.md) — Intern / Paper / DailyNews 各自做什么
4. [03-版本路线图](03-版本路线图.md) — 0.1→1.3 当前进度
5. [04-如何跑验收](04-如何跑验收.md) — 各版本验收命令
6. [05-文档体系说明](05-文档体系说明.md) — 三层文档架构
7. [06-仓库目录说明](06-仓库目录说明.md) — 代码 / 文档 / var 分工
8. [07-0.3-Adapter验收说明](07-0.3-Adapter验收说明.md) — 0.3 三层验收与 MANUAL 项
9. [08-0.4-个人日用闭环](08-0.4-个人日用闭环.md) — 0.4 四子阶段与范围
10. [09-1.x-个人到协作](09-1.x-个人到协作.md) — 1.0→1.3 个人到协作
11. [10-中英文文档管理](10-中英文文档管理.md) — 中英文放哪、谁维护、链接规则
12. [11-0.4a-SQLite与恢复扫描](11-0.4a-SQLite与恢复扫描.md) — 0.4-a SQLite 与 recovery-scan
13. [12-0.4c-审阅与决策层](12-0.4c-审阅与决策层.md) — 0.4-c 审阅 CLI 与产物
14. [13-输出接口-人看MD机器看JSON](13-输出接口-人看MD机器看JSON.md) — 人看 MD、机器看 JSON

## 按场景跳转

| 场景 | 文档 |
|------|------|
| 第一次 clone | [00-快速开始](00-快速开始.md) |
| 理解架构 | [01-系统是什么](01-系统是什么.md) + [development/01-architecture.md](../development/01-architecture.md) |
| 0.3 状态与验收 | [07-0.3-Adapter验收说明](07-0.3-Adapter验收说明.md) + [development/36-adapter-mvp-0.3-acceptance.md](../development/36-adapter-mvp-0.3-acceptance.md) |
| 规划 0.4 | [08-0.4-个人日用闭环](08-0.4-个人日用闭环.md) + [development/40-personal-daily-loop-0.4-spec.md](../development/40-personal-daily-loop-0.4-spec.md) |
| 0.4-a SQLite 验收 | [11-0.4a-SQLite与恢复扫描](11-0.4a-SQLite与恢复扫描.md) + [development/43-personal-daily-loop-0.4a-acceptance.md](../development/43-personal-daily-loop-0.4a-acceptance.md) |
| 0.4-c 审阅与输出接口 | [12-0.4c-审阅与决策层](12-0.4c-审阅与决策层.md) + [13-输出接口-人看MD机器看JSON](13-输出接口-人看MD机器看JSON.md) + [development/47-output-interface-spec.md](../development/47-output-interface-spec.md) |
| 理解 1.x / Team 后移 | [09-1.x-个人到协作](09-1.x-个人到协作.md) + [development/42-1x-roadmap-personal-to-collaboration.md](../development/42-1x-roadmap-personal-to-collaboration.md) |
| 文档怎么维护 | [10-中英文文档管理](10-中英文文档管理.md) |
| 给 AI 的英文规格 | [en-core.md](../en-core.md) |
| 完整开发索引 | [development/README.md](../development/README.md) |
| 仓库目录结构 | [06-仓库目录说明.md](06-仓库目录说明.md) |

## 与英文规格的关系

- **中文（本目录）**：帮你快速理解「为什么、做什么、怎么跑」
- **英文（development/*.md）**：接口层权威规格，AI 实施与 CI 对齐用
- **不追求逐句双语**：缺细节时查英文编号文档，不必两份全文同步
