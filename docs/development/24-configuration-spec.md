# 24 配置规范

## 1. 配置文件

```text
config/
├── looppilot.yaml
├── intern.yaml
├── paper.yaml
├── daily_news.yaml
├── policies.yaml
├── sources.yaml
└── models.yaml
```

每份配置有 JSON Schema。启动时一次性校验并生成不可变配置快照；Run 中途修改配置只影响下一个 Run。

## 2. 全局配置

```yaml
runtime:
  timezone: Asia/Shanghai
  state_dir: var/state
  artifact_dir: var/artifacts
  checkpoint_dir: var/checkpoints
  execution_mode: sequential
  dry_run: false
  max_concurrent_runs: 1

reporting:
  format: markdown
  include_evidence_links: true
  redact_sensitive_values: true
```

## 3. InternLoop

```yaml
enabled: true
workspace: /absolute/path/to/repository
default_branch: main
use_worktree: true
allowed_paths: ["src/**", "tests/**", "docs/**"]
forbidden_paths: [".env*", "secrets/**", "deploy/**"]
validation:
  test: ["pytest", "-q"]
  lint: ["ruff", "check", "."]
  typecheck: null
  build: null
budget:
  max_duration_minutes: 30
  max_rounds: 3
  max_changed_files: 5
permissions:
  allow_commit: false
  allow_push: false
  allow_dependency_changes: false
```

命令必须是参数数组，不允许未经解析的 shell 字符串。

## 4. PaperLoop

```yaml
enabled: true
workspace: /absolute/path/to/paper
main_document: paper.md
bibliography: references.bib
read_only_paths: ["experiments/raw/**"]
modifiable_sections: ["related-work", "method", "experiments"]
verification_level_for_citation: fulltext
research_topics: []
required_evaluators:
  - structure
  - claim_evidence
  - experiment
  - related_work
  - consistency
budget:
  max_duration_minutes: 30
  max_rounds: 3
  max_new_sources: 10
```

具体研究关键词放 `research_topics`，不写死在框架。

## 5. DailyNewsLoop

```yaml
enabled: true
categories:
  github: {max_items: 3}
  research: {max_items: 3}
  politics: {max_items: 2}
  finance: {max_items: 2}
minimum_confidence: medium
route_to_inbox_requires: high
lookback_hours: 36
candidate_expiry_days: 7
budget:
  max_duration_minutes: 30
  max_kept_items: 10
```

## 6. Sources

每个 source 配置 `id`、`type`、`tier`、`enabled`、`endpoint`、`categories`、`rate_limit`、`cache_ttl`、`auth_env`、`parser` 和 `terms_checked`。密钥只引用环境变量名称。

## 7. Models

```yaml
roles:
  planning: {adapter: primary_reasoning}
  coding: {adapter: coding_cli}
  research: {adapter: primary_reasoning}
  writing: {adapter: primary_reasoning}
  screening: {adapter: economical}
  evaluation: {adapter: independent_reasoning}

adapters:
  coding_cli:
    kind: cli
    command: ["configured-cli"]
    timeout_seconds: 900
```

具体模型名、endpoint 和 auth_env 只存在 Adapter 配置。

## 8. 配置优先级与禁止项

优先级：Schema 默认值 < 文件配置 < 显式 CLI 非敏感覆盖。环境变量只用于密钥和机器路径，不允许隐藏覆盖安全策略。

禁止：未知字段、相对越界路径、明文密钥、shell 拼接命令、负预算、DailyNews 无限条目、关闭强制 Policy Gate。
