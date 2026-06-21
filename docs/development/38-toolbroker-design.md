# 38 ToolBroker 设计

## 职责

ToolBroker 是 LoopPilot 中**唯一**允许执行 shell、读写文件、Git 只读操作的网关。Agent 与 Adapter 不得绕过 Broker 直接调用 OS 能力。

## 组件

| 模块 | 职责 |
|------|------|
| `tools/policy.py` | ToolPolicy：allowlist、forbidden tokens/paths、timeout、cwd roots |
| `tools/command.py` | 受控 subprocess 执行与 CommandResult |
| `tools/file_ops.py` | 路径策略下的 read/write |
| `tools/git_ops.py` | 只读 git diff/status |
| `tools/broker.py` | 统一入口，策略校验后委派 |

## 策略字段

```yaml
allowed_commands: [python, pytest, git]
forbidden_tokens: [push, deploy, release, publish]
forbidden_paths: [.env, secrets/**]
max_timeout_seconds: 300
cwd_roots: [/path/to/approved/worktree]
```

## InternLoop 集成

- pytest 经 ToolBroker 或等价的受控 subprocess（现有 InternLoop 路径）
- `tool-results.json` 记录 round 数、adapter 调用次数、dry_run 标志
- `patch.diff` / `diff-summary.md` 来自 git diff，不来自模型自证

## 与 Adapter 的分工

| 能力 | Adapter | ToolBroker |
|------|---------|------------|
| 模型推理 / CLI 编码 | ✓ | ✗ |
| pytest / git diff | ✗ | ✓ |
| 文件读写（worktree 内） | 经 Adapter 计划 | ✓ 执行 |
| push / deploy | ✗ | ✗（策略拒绝） |

## 测试

- `tests/unit/test_tool_broker_policy.py` — 白名单、cwd、forbidden path

## 相关文档

- [37-adapter-safety-policy.md](37-adapter-safety-policy.md)
- [06-agents-skills-tools.md](06-agents-skills-tools.md)
