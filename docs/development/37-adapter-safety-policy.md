# 37 Adapter 安全策略

## 默认关闭真实 Adapter

0.3 起，`runtime.allow_real_adapters` 默认为 `false`。在此模式下：

- `ModelRouter` 将 `cli`、`cursor_cli`、`api`、`openai_compatible` 类 adapter 标记为 **BLOCKED**
- `create_adapter()` 在 `allow_real_adapters=false` 时始终返回 `MockAdapter`，除非显式 `--adapter` 覆盖且该 adapter 为真实类型——此时抛出 `AdapterBlockedError`，Run  outcome 为 **BLOCKED**
- CI 与本地验收默认不携带 API key 或真实 CLI 凭证

## 数据等级

| 等级 | 路由规则 |
|------|----------|
| PUBLIC | 可路由至 mock 与经济 API adapter |
| PROJECT | 默认 Intern/Paper 工作区等级 |
| SENSITIVE | 仅允许 cursor_cli 等显式声明的 CLI adapter |
| SECRET | **永不**进入任何模型或 CLI adapter |

## Cursor CLI 边界

- `cwd` 必须为批准的 worktree 或其子目录
- 命令禁止含 `push`、`commit`、`deploy`、`.env` 路径
- 环境变量通过 `env_allowlist` 注入；禁止继承完整用户环境
- dry-run 只写 transcript artifact，不启动子进程

## OpenAI Compatible 边界

- 认证仅通过 `auth_env` 从环境读取
- trace/artifact 中密钥以 `<redacted>` 替代
- 结构化输出解析失败映射为 `MODEL_OUTPUT_INVALID`
- 429/5xx 有限重试；401/403 不重试

## 启用真实 Adapter（手动）

1. 在 `config/loop-pilot.yaml` 设置 `runtime.allow_real_adapters: true`
2. 配置 `config/adapters.yaml` 中对应 adapter 的 command/endpoint/auth_env
3. 运行 `loop-pilot adapters doctor` 确认 WARN 项可接受
4. 先在 `--dry-run` 与 fixture 上验证，再接触真实 worktree

## 相关文档

- [36-adapter-mvp-0.3-acceptance.md](36-adapter-mvp-0.3-acceptance.md)
- [38-toolbroker-design.md](38-toolbroker-design.md)
- [30-adapter-and-model-router-roadmap.md](30-adapter-and-model-router-roadmap.md)
