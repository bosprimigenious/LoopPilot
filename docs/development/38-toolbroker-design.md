# ToolBroker Design (0.3)

> ToolBroker 是 LoopPilot 0.3 的**确定性能力层**：所有文件、Git、子进程、HTTP 读取必须经过 Broker，由 PolicyEngine 裁决，并写入审计 trace。

## 1. 动机

当前 0.2 中 Loop 可直接调用 helpers / subprocess 进行有限操作。0.3 接入真实 Adapter 后，模型与 CLI 的输出可能请求危险操作；必须：

1. 统一入口，便于测试与审计
2. 强制 PolicyEngine 检查
3. 支持 dry-run（读允许、写禁止）
4. 与 Adapter 层清晰分工（Adapter 不替代 Broker）

**Agent 与 Loop 不得绕过 ToolBroker** 直接调用 `open()`, `subprocess`, `requests` 等。

## 2. 架构位置

```text
Loop state machine
    │
    ├── ModelRouter ──► Adapter (LLM / Coding CLI)
    │
    └── ToolBroker ──► PolicyEngine
              │
              ├── FileTool      (read / write / list)
              ├── GitTool       (status, diff, worktree)
              ├── CommandTool   (allowlisted argv)
              └── HttpTool      (GET, limited connectors)
              │
              └── TraceWriter + ArtifactStore
```

## 3. 公共 API（草案）

```python
class ToolBroker:
    def read_file(self, ctx: ToolContext, path: Path) -> ToolResult: ...
    def write_file(self, ctx: ToolContext, path: Path, content: bytes) -> ToolResult: ...
    def run_command(self, ctx: ToolContext, argv: list[str], cwd: Path) -> ToolResult: ...
    def git(self, ctx: ToolContext, argv: list[str], cwd: Path) -> ToolResult: ...
    def http_get(self, ctx: ToolContext, url: str, headers: dict | None) -> ToolResult: ...
    def create_worktree(self, ctx: ToolContext, spec: WorktreeSpec) -> ToolResult: ...
```

### ToolContext

| 字段 | 说明 |
|------|------|
| `run_id` | 当前 run |
| `loop` | intern / paper / daily_news |
| `workspace_id` | 配置中的 workspace 键 |
| `dry_run` | 若为 true，写操作返回 planned artifact 不落地 |
| `data_class` | PUBLIC / INTERNAL / SENSITIVE / SECRET |
| `trace` | TraceWriter 引用 |

### ToolResult

| 字段 | 说明 |
|------|------|
| `status` | success / blocked / error / dry_run_skipped |
| `stdout` / `stderr` | 可选，大输出 → artifact 引用 |
| `artifact_refs` | 列表 |
| `policy_decision` | allow / deny + reason code |
| `duration_ms` | 计时 |

## 4. Policy 集成

每次调用流程：

1. Resolve path → absolute; check workspace allowlist + forbidden_paths
2. `PolicyEngine.evaluate(tool_request)` → ALLOW | DENY
3. DENY → 立即返回 `blocked`，写 trace，不执行
4. ALLOW + dry_run + write → skip execution，写 `dry_run_skipped` + plan artifact
5. ALLOW + execute → run with timeout; capture output; redact secrets

Policy 规则来源：`config/loop-pilot.yaml` workspace 段 + loop 专用 config + [37-adapter-safety-policy.md](37-adapter-safety-policy.md)。

## 5. 工具分面

### 5.1 FileTool

- **read**: allowlisted path only; size cap; binary/text mode
- **write**: requires `--allow-write` at run level + policy allow; atomic write where possible
- **list**: directory listing within workspace root

### 5.2 GitTool

- Allowed subcommands: `status`, `diff`, `rev-parse`, `worktree add/remove`, `checkout` (scoped)
- Forbidden: `push`, `fetch` to arbitrary remotes, `reset --hard`, `clean -fdx` without explicit policy
- Worktree lifecycle: create → use as CodingCLI `cwd` → remove on success/finally

### 5.3 CommandTool

- Input: `argv: list[str]` — **never** a shell string
- cwd must be approved worktree or workspace root
- env: allowlist merge only
- timeout + kill process group
- Intern validation commands (pytest, ruff) from config arrays

### 5.4 HttpTool

- GET only in 0.3 MVP; no arbitrary POST
- Used by DailyNews connectors (RSS, GitHub API, metadata)
- Rate limit per host; cache ETag/Last-Modified where supported
- Response body → artifact; headers stripped of secrets

## 6. dry-run 语义

| 操作 | dry-run 行为 |
|------|--------------|
| read_file | 正常执行 |
| write_file | 不写入；返回 would-write artifact |
| run_command | 若命令只读（policy 标记）可执行；写命令 skip |
| git worktree add | skip；记录 planned path |
| http_get | 可配置：DailyNews 可读快照；默认 respect dry-run flag |

Run-level `--dry-run` 传入 `ToolContext.dry_run=True`。

## 7. 审计

每条 Tool 调用产生 trace 事件：

```json
{
  "event": "tool_call",
  "tool": "command",
  "argv": ["pytest", "-q"],
  "cwd": ".../worktrees/run-abc",
  "status": "success",
  "duration_ms": 1200,
  "policy": "allow"
}
```

- 大输出 → `stdout-*.txt` artifact
- 敏感字段 regex redact before persist
- BLOCKED 调用同样记录（含 deny reason）

## 8. 与 Adapter 的交互

| 场景 | 谁执行 |
|------|--------|
| Cursor CLI 改代码 | CodingCLIAdapter（cwd=worktree） |
| Loop 跑 pytest 验证 | ToolBroker.run_command |
| Adapter 返回 "write file X" | Loop 解析 → Broker.write_file（非 Adapter 直写） |
| Paper 读 draft.md | Broker.read_file |
| DailyNews 拉 RSS | Broker.http_get via connector |

CodingCLIAdapter 内部 subprocess 仅限**启动配置的 CLI 二进制**；其它系统命令走 Broker。

## 9. 错误模型

| Code | 含义 |
|------|------|
| `POLICY_DENIED` | PolicyEngine 拒绝 |
| `PATH_OUT_OF_BOUNDS` | 路径不在 allowlist |
| `COMMAND_NOT_ALLOWLISTED` | argv 不在白名单 |
| `TIMEOUT` | 超时已杀进程 |
| `HTTP_RATE_LIMITED` | 连接器限速 |
| `DRY_RUN_SKIPPED` | 非错误；写被跳过 |

映射到统一 `LoopPilotError` 供 state machine 使用。

## 10. 配置示例

```yaml
# config/loop-pilot.yaml (excerpt)
workspaces:
  intern_demo:
    root: examples/intern_demo
    allowed_paths:
      - "src/**"
      - "tests/**"
    forbidden_paths:
      - ".git/**"
    validation_commands:
      - ["python", "-m", "pytest", "-q"]
tool_broker:
  max_file_read_bytes: 1048576
  command_timeout_seconds: 300
  http_timeout_seconds: 30
```

## 11. 测试策略

| 测试 | 内容 |
|------|------|
| `test_toolbroker_policy_deny` | forbidden path → blocked |
| `test_toolbroker_dry_run_write` | no filesystem change |
| `test_toolbroker_command_argv` | reject shell metachar injection |
| `test_toolbroker_git_worktree` | create/remove lifecycle |
| `test_loop_uses_broker` | monkeypatch: direct subprocess fails CI |

## 12. 实现顺序（within 0.3）

1. `ToolContext` / `ToolResult` models
2. Policy hook + FileTool read
3. CommandTool + Intern validation path
4. dry-run write skip
5. GitTool worktree
6. HttpTool for DailyNews connector
7. Loop refactors (Intern → Paper → DailyNews)

## 13. 非目标（0.3）

- 通用插件 Tool 注册（0.7 Personal Extensions）
- 分布式 / 远程 Broker
- 写 HTTP (POST/PUT)
- 交互式 TUI shell

## 14. 相关文档

- [06-agents-skills-tools.md](06-agents-skills-tools.md)
- [08-security-and-recovery.md](08-security-and-recovery.md)
- [37-adapter-safety-policy.md](37-adapter-safety-policy.md)
- [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)
- [34-version-roadmap-0x.md](34-version-roadmap-0x.md)
