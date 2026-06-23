# GitHub 身份、分支、PR 与 Skill 使用模型

## 目标

LoopPilot 未来可以用用户的 GitHub 身份读取仓库、开分支、push、创建 PR，但必须做到：

- 用户显式授权；
- token 不落盘到项目；
- 不直接 push main；
- 不自动 merge；
- 每个远端写动作都有审计记录；
- 分支、commit、PR body 都可追溯到 RunRecord。

## 身份登录模型

### 推荐：GitHub CLI / GitHub App 作为身份代理

不要让 LoopPilot 自己保存 GitHub token。

推荐使用：

```bash
gh auth login
gh auth status
```

然后 LoopPilot 只调用受控命令：

```bash
gh repo view
gh pr view
gh pr list
gh pr checks
gh pr create
gh api ...
```

优点：

- token 由 GitHub CLI / OS keychain 管理；
- LoopPilot 不需要接触明文 token；
- 用户可以随时 `gh auth logout`；
- scopes 由 GitHub CLI 管理。

### 备选：环境变量

仅在 CI 或临时环境使用：

```bash
GH_TOKEN=...
```

约束：

- 不写入 config；
- 不写入 artifacts；
- 不写入 trace；
- report 中必须 redacted。

## 分支策略

### 禁止

```text
main
master
release/*
production/*
protected branches
```

### 推荐命名

InternLoop：

```text
loop-pilot/intern/YYYYMMDD-<issue-or-pr>-<slug>
```

PaperLoop：

```text
loop-pilot/paper/YYYYMMDD-<claim-or-exp>-<slug>
```

DailyNews：

```text
loop-pilot/news/YYYYMMDD-<cluster-id>-<slug>
```

### 分岔修改

不同方向必须开不同分支，不要在同一个 run 里混改：

```text
fix-ci-failure
review-comment-response
paper-claim-update
figure-refresh
news-connector-prototype
```

如果同一个 run 发现多个方向：

```text
RunRecord
  ├── branch_plan.json
  ├── branch A: primary fix
  └── branch candidates: suggested only, not created unless approved
```

## PR 策略

默认创建 draft PR：

```bash
gh pr create --draft --title ... --body-file ...
```

禁止：

- auto merge；
- auto approve；
- force push 到 main；
- 把多个无关任务塞进一个 PR；
- 没测试就写 “all tests pass”。

PR body 必须包含：

```markdown
## Problem

## Changes

## Evidence

## Tests

## Risks

## Unresolved

## LoopPilot Artifacts
```

## 现成能力与可参考开源项目

### 当前 Codex GitHub skills

当前 Codex 环境里已有三类可参考 skill：

1. `github:yeet`
   - 用途：确认 scope、commit、push、开 draft PR。
   - 对 LoopPilot 的启发：publish flow 必须先检查 diff，再 stage 指定文件，最后开 draft PR。

2. `github:gh-address-comments`
   - 用途：读取 PR review comments，聚类 actionable threads，再逐项修复。
   - 对 InternLoop 的启发：PR 评论不是一条条平铺消息，要按文件/行为聚类，再生成修复计划。

3. `github:gh-fix-ci`
   - 用途：读取 GitHub Actions checks/logs，定位失败，再修复。
   - 对 InternLoop 的启发：CI failure 是第一等输入，必须保存 log snippet 和 root cause。

这些 skill 不是 LoopPilot runtime 的内部实现，但可以作为 0.6 InternLoop 的行为模板。

### 开源/外部项目

#### OpenHands

- 链接：[OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands)
- 论文：[OpenHands paper](https://arxiv.org/abs/2407.16741)
- 可借鉴：
  - sandbox；
  - agent 写代码、跑命令、浏览；
  - benchmark/evaluation；
  - 多 agent 协作。
- 不建议直接照搬：
  - LoopPilot 更强调个人本地、branch policy、审计和 human gate。

#### SWE-agent

- 链接：[SWE-agent GitHub](https://github.com/SWE-agent/SWE-agent)
- 可借鉴：
  - issue -> patch 的 agent loop；
  - SWE-bench 风格任务；
  - patch generation。
- 不足：
  - 不是完整个人 morning OS；
  - 不覆盖 Paper/DailyNews 的证据与新闻核验。

#### aider

- 链接：[aider GitHub](https://github.com/Aider-AI/aider)
- 可借鉴：
  - 本地 git-aware coding assistant；
  - 小步 commit；
  - 人机协作体验。
- 不足：
  - 更像 pair programming；
  - PR/review/CI/orchestration 需要 LoopPilot 自己补。

#### GitHub Copilot coding agent / Codex

- 可借鉴：
  - task -> VM/worktree -> branch -> PR -> human review；
  - session logs；
  - review comment follow-up。
- 对 LoopPilot 的边界：
  - LoopPilot 不应该变成云端黑盒；
  - 必须保留本地 artifacts 和 SQLite RunRecord。

## InternLoop 真实 GitHub 流程

```text
resolve repo
  ↓
gh auth status
  ↓
fetch base branch
  ↓
read issue / PR / CI / review comments
  ↓
create branch
  ↓
apply patch
  ↓
run tests
  ↓
write development-report.md
  ↓
commit
  ↓
push branch
  ↓
open draft PR
  ↓
write PR URL to RunRecord
```

## PaperLoop 真实 GitHub 流程

```text
resolve paper repo
  ↓
fetch base branch
  ↓
read claim list / manuscript / data manifest
  ↓
verify new data path + checksum
  ↓
create branch
  ↓
update paper text / figures / tables
  ↓
write claim-evidence-report.md
  ↓
commit
  ↓
push branch
  ↓
open draft PR
```

## 安全验收

0.6 GitHub integration 必须有以下测试：

- main branch write blocked；
- protected branch push blocked；
- missing gh auth -> BLOCKED；
- mixed worktree -> BLOCKED unless scoped；
- unrelated files not staged；
- PR body includes artifacts；
- CI failure logs saved；
- review comments grouped；
- secrets redacted；
- dry-run creates no branch and no PR；
- live mode requires explicit `--allow-remote-write`。

## CLI 草案

Intern:

```bash
loop-pilot run intern \
  --repo bosprimigenious/LoopPilot \
  --pr 8 \
  --fix-ci \
  --dry-run

loop-pilot run intern \
  --repo bosprimigenious/LoopPilot \
  --issue 12 \
  --allow-remote-write \
  --draft-pr
```

Paper:

```bash
loop-pilot run paper \
  --repo bosprimigenious/paper-repo \
  --claim-list claims.yaml \
  --data-manifest data/manifest.json \
  --dry-run
```

DailyNews:

```bash
loop-pilot run daily-news \
  --source-profile live-small \
  --dry-run
```

## 最终原则

真实连接外部世界不是问题，问题是边界。

LoopPilot 可以代表用户：

- 读 repo；
- 读 PR；
- 读 CI；
- 创建分支；
- push；
- 开 draft PR。

但不能：

- 直接改 main；
- 自动 merge；
- 自动 approve；
- 隐藏失败；
- 写入没有证据的论文 claim；
- 把未核验新闻升级成任务。

