# 2026-06-22 — main 同步、Truthful 0.4 合入与 README 重写

**日期：** 2026-06-22  
**分支：** `main`  
**相关提交：** `f073353`（PR #8 merge）、`7620534`（stabilize 合入 main）、`a821367`（main 远程同步）

## 背景

`stabilize/0.4-truthful-acceptance` 经 Codex 多轮审查（P0 patch review gate、P1 manifest、P2 review guards / manifest DB sync）后，通过聚合验收 **11/11 READY**，并以 [PR #8](https://github.com/bosprimigenious/LoopPilot/pull/8) 合入 `main`。此前根目录 `README.md` 仍标注「0.4 NOT READY / 0.4-c 阻塞」，与主线事实不符，需要同步文档与视觉呈现。

## 主线事实（验收基准）

| 检查项 | 结果 | 备注 |
|--------|------|------|
| PR #8 merge into `main` | ✅ | `f073353` — stabilize/0.4-truthful-acceptance |
| `verify_0_4_acceptance.py` | ✅ **11/11 READY** | 唯一可宣告 Full 0.4 的聚合脚本 |
| `pytest -q` | ✅ **254 passed** | 2026-06-22 本地全量 |
| `ruff check .` | ✅ PASS | 文档变更前 spot check |
| `verify_0_5_prep.py` | ✅ `0.5-prep: PASS` | `0.5-ready: NOT READY`（预期） |
| 包版本 | `0.4.0b1` | `pyproject.toml` |

### 聚合 11 步清单（`verify_0_4_acceptance.py`）

1. `ruff check .`
2. `pytest` 全量
3. `verify_0_3_acceptance.py`（20/20）
4. `verify_0_4b_acceptance.py`（READY）
5. `verify_0_4c_acceptance.py`（READY）
6. `verify_0_4d_acceptance.py`（READY，含前置链）
7. migration matrix tests
8. failure-artifact contract tests
9. recovery/resume suite
10. truthful-acceptance anti-cheat
11. 0.4-c review CLI integration

## README 重写动机

1. **状态过时：** 旧 README 写「0.4 NOT READY / 157 pytest」，与 PR #8 合入后的主线不一致。
2. **视觉密度不足：** 参考 [agentic-rubric-runner](https://github.com/bosprimigenious/agentic-rubric-runner) README 的徽章 + 架构图风格，为 LoopPilot 增加 inline SVG（状态徽章、0.3→0.4→0.5 里程碑条、Loop 状态机 + review gate 分支）。
3. **验收入口分散：** 将 `verify_0_3` / `0_4b` / `0_4c` / `0_4d` / `0_4` / `0_5_prep` 汇总为表格，明确「只有聚合脚本可宣告 Full 0.4 READY」。

## README 内容摘要

- 一句话定位 + Runtime / Evaluation 双层价值主张
- **SVG #1：** 项目徽章行（0.4 READY · 254 tests · Python ≥3.11 · v0.4.0b1 · Apache-2.0）
- **SVG #2：** 版本里程碑条（0.3 Mini → 0.4 Full READY → 0.5-prep）
- **SVG #3：** Loop 状态机（OBSERVING → … → WAITING_APPROVAL → TERMINATED，含 patch review 分支）
- Mermaid 架构模块图
- Quick start、验收门禁表、SafetyGate 0.5-prep 边界、文档索引

## 未纳入本次 commit 的内容

- `paper/` 目录（论文草稿，非产品文档）
- `scripts/verify_0_5_prep.py.wip`
- `var/artifacts/` 运行产物

## 后续

- `feat/0.5-safe-autonomy` 上继续 0.5-a SafetyGate 正式实现（当前仅 prep fail-closed）
- Ideas Acceptance（真实 Intern/Paper/DailyNews 闭环、7 天 dogfooding）仍待单独验收
- 考虑同步更新 `docs/zh/README.md` 与 Layer 1 认知层（本次优先根 README + 开发索引）
