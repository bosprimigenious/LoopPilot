# Adapter Safety Policy (0.3)

> 从 0.3 Adapter MVP 规格提炼的安全策略。实现与验收必须以本文 + [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md) 为准。

## 1. 设计原则

| 原则 | 含义 |
|------|------|
| **Safe by default** | `allow_real_adapters=false`；dry-run 默认；shell/network/write 默认 deny |
| **Explicit opt-in** | 真实 Adapter 需 **配置 + CLI 双重确认** |
| **No bypass** | Loop/Agent 不得绕过 ToolBroker 或 PolicyEngine |
| **Audit everything** | Adapter 与 Tool 调用写入 trace；原始输出 artifact；密钥脱敏 |
| **Fail closed** | 策略不明或冲突 → BLOCKED，不静默降级到危险路径 |
| **Personal tool boundary** | 永不 auto push / PR / deploy |

## 2. 门控层级

```text
User intent (CLI flags)
        ↓
config/runtime.allow_real_adapters
        ↓
AdapterRegistry (reject cli/api types if false)
        ↓
ModelRouter (capability + data class + budget)
        ↓
PolicyEngine (paths, commands, diffs)
        ↓
ToolBroker (file / git / subprocess / http)
        ↓
Adapter.execute (timeout + cancellation)
```

每一层必须可独立测试；下层不得假设上层已「大概安全」。

## 3. `allow_real_adapters` 策略

### 默认值

- `config/loop-pilot.yaml`: `runtime.allow_real_adapters: false`
- 新用户 / init 产物（0.5）同样默认 false

### 启用条件（全部满足）

1. 配置文件中 `allow_real_adapters: true`
2. CLI 显式传递 `--allow-real-adapters`（或 documented equivalent）
3. 目标 Adapter 凭证已配置（env 或 secrets file，不入库）
4. workspace 在 allowlist 内
5. 非 dry-run 的写入还需 `--allow-write`（Intern/Paper）

### 禁止行为

- 不得在测试中默认开启 real adapters
- 不得在 CI 主矩阵调用真实 CLI/API（除非 opt-in job + secrets）
- 不得在 Router 中「为了方便」静默回退 mock 而隐藏 real 请求

## 4. 数据等级 (Data Class)

| 等级 | 规则 |
|------|------|
| **PUBLIC** | 可发往任何已启用 Adapter |
| **INTERNAL** | 仅 mock + 本地 CLI（无外传 API）除非配置允许 |
| **SENSITIVE** | 仅 allowlisted Adapter；API 需加密传输 + 脱敏 artifact |
| **SECRET** | **禁止**离开本机；Router 直接 BLOCKED |

Agent 必须在请求中声明 data class；Router 过滤违规候选。

## 5. Workspace 与路径

- 所有文件操作路径必须 resolve 到 allowlisted workspace 或 approved worktree
- `forbidden_paths` 优先于 allow（deny wins）
- diff review：任何修改落在 forbidden 或 allowlist 外 → BLOCKED
- Paper `modifiable_sections` 外改动 → BLOCKED 或 PARTIAL

## 6. 命令执行

- **Argv 数组 only** — 禁止 `shell=True` 与用户字符串拼接
- 命令白名单 per loop + per workspace config
- 超时硬杀 + 进程组终止
- 环境变量 allowlist；不继承完整用户环境
- 禁止： `git push`, `git reset --hard`, `rm -rf /`, 任意 deploy 脚本

## 7. CodingCLIAdapter 约束

- `cwd` = 批准的 worktree 根
- dry-run：只读 + 计划 artifact，**零写入**
- 执行前后 git status / 文件 hash snapshot
- stdout/stderr/transcript 全量 artifact（敏感行 redact）
- 退出码非零或 schema 失败 → 不得 PASS
- CLI 不得自行 push / 访问禁止路径

## 8. APIModelAdapter 约束

- 请求/响应 artifact 脱敏（API key, cookie, PII）
- 结构化输出失败：最多一次 repair；仍失败 → error
- 429/5xx 有限退避；401/403 不重试
- Provider fallback 仅限同 `model_role` 且满足 data class
- 记录 request id、model id、token、cost、latency

## 9. ToolBroker 与 Adapter 边界

| 操作 | 负责组件 |
|------|----------|
| 模型推理 / CLI agent | Adapter |
| 读文件、写文件、git、pytest、curl | ToolBroker |
| 策略判定 | PolicyEngine（Broker 调用前） |

Adapter **不得**内嵌任意 shell 执行绕过 Broker；CodingCLIAdapter 仅运行**配置模板化**的编码 CLI。

## 10. 网络

- MockAdapter：无网络
- HTTP/RSS/GitHub connector：rate limit、timeout、单源失败隔离
- 响应中 cookie/token/个人字段不得进入 Markdown 报告
- robots / ToS 禁止时 → SOURCE DISABLED

## 11. 人工审阅（0.3）

- 0.3 **无** `approve`/`reject` CLI（归属 0.4）
- 人类通过 Markdown：`review-required.md`, `next-actions.md`
- Real run 后必须生成 review artifact 说明建议动作

## 12. 错误与降级

- Adapter timeout → 可重试（Policy 允许时）；记录 attempt
- 单 Connector 失败 → DailyNews 继续其他源
- Router 无合格 Adapter → BLOCKED + 明确原因（非 crash）
- 不得用搜索摘要替代 Paper 正式证据

## 13. 测试与安全 CI

- 单元测试覆盖：registry 拒绝、router 过滤、broker deny
- 集成测试默认 mock；real adapter 测试 gated
- `ruff` + `pytest` + `doctor` 在 PR 必须绿
- 禁止提交 `.env`、密钥、私有 workspace 路径

## 14. 违规响应

| 违规类型 | 系统响应 |
|----------|----------|
| 越界路径 | BLOCKED + policy artifact |
| 未授权 real adapter | BLOCKED at registry/router |
| SECRET 数据外传 | BLOCKED before execute |
| 命令不在白名单 | BLOCKED |
| Schema/exit code 失败 | FAIL / partial，不 PASS |

## 15. 相关文档

- [08-security-and-recovery.md](08-security-and-recovery.md)
- [29-model-routing-and-runtime-policy.md](29-model-routing-and-runtime-policy.md)
- [19-adapter-specifications.md](19-adapter-specifications.md)
- [38-toolbroker-design.md](38-toolbroker-design.md)
- [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)
- [34-version-roadmap-0x.md](34-version-roadmap-0x.md)
