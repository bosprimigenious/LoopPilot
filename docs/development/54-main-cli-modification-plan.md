# Main CLI Smoke 修改计划（2026-06-23）

## 当前结论

最新 `main` 可以通过自动化质量门禁：

- `ruff check .`：PASS
- `pytest -q`：254 passed
- `scripts/verify_0_3_acceptance.py`：20/20 PASS
- `scripts/verify_0_4_acceptance.py`：11/11 READY
- `scripts/verify_0_5_prep.py`：0.5-prep PASS，0.5-ready NOT READY

但是从“个人真实接入 CLI”的角度看，仍有若干需要修正的产品与运行边界问题。它不是测试不通过的问题，而是“能跑”和“长期可控好用”之间的差距。

## P0：配置隔离与路径解析必须明确

### 发现

使用临时配置目录运行：

```bash
python -m loop_pilot.cli --config-dir /tmp/looppilot-cli-smoke/config status
```

仍然读到了仓库 `var/` 下已有验收运行记录。原因是 `runtime.state_dir`、`runtime.artifact_dir`、`runtime.sqlite_path` 等相对路径按当前工作目录解析，而不是按 `--config-dir` 或某个明确的 runtime root 解析。

### 风险

- 用户以为临时配置隔离，实际污染/读取主仓库状态。
- 多环境、多 profile、本地日用与测试验收容易互相串状态。
- 未来真实 Connector 接入后，这会扩大误操作范围。

### 修改建议

增加统一路径解析策略：

```text
runtime.root_dir:
  default: project cwd
  optional: config-relative / explicit absolute path

relative runtime paths:
  state_dir
  artifact_dir
  checkpoint_dir
  sqlite_path
  lock_dir
```

建议实现：

1. 在 `Config` 里保留 `config_dir` 与 `runtime_root`。
2. 对所有 runtime 路径统一调用 `resolve_runtime_path()`;
3. 文档明确：
   - demo/开发：相对仓库 cwd；
   - 个人日用：建议显式 `runtime.root_dir: ~/.loop-pilot`；
   - 测试：临时目录必须全隔离。
4. 增加测试：
   - `--config-dir /tmp/...` + 相对 `state_dir` 不应读取仓库 `var/`；
   - sqlite fixture 不应复用仓库主库，除非显式配置。

## P1：默认配置与 0.4 READY 叙事需要分层

### 发现

默认 `config/loop-pilot.yaml` 仍是：

```yaml
runtime:
  state_backend: json
```

这使得以下 0.4 命令默认不可用：

- `db`
- `review`
- `summary`
- `today` 的完整个人任务流
- `run daily`

这本身是安全的，但 README 顶部显示 `0.4 READY`，新用户会误以为默认配置即可跑完整 0.4。

### 修改建议

保留 fail-closed 默认，但新增显式 profile：

```text
config/
  loop-pilot.yaml                 # safe demo / json default
  profiles/
    personal-sqlite.yaml          # local daily use
    smoke-sqlite.yaml             # isolated CLI smoke
```

并新增命令或文档入口：

```bash
loop-pilot init --profile personal-sqlite
loop-pilot doctor --profile personal-sqlite
```

如果暂不实现 profile CLI，至少在 README Quickstart 里分成两条：

1. Mini/demo quickstart：JSON、离线、fixture；
2. Personal daily quickstart：SQLite、review、summary、daily。

## P1：`today` 缺少查看型命令

### 发现

`loop-pilot today --help` 目前只有：

```text
add
add-queue
```

没有 `list` / `show` / `done` / `defer`。对“早上半小时接入当天任务”的真实场景来说，用户第一反应会是：

```bash
loop-pilot today list
```

当前会得到：

```text
Error: No such command 'list'.
```

### 修改建议

补齐最低可用命令：

```bash
loop-pilot today list
loop-pilot today show <item_id>
loop-pilot today done <item_id>
loop-pilot today defer <item_id> --until YYYY-MM-DD
```

验收标准：

- 空 today 时输出清晰 `_No tasks scheduled for today._`；
- 有任务时显示 id、类型、优先级、来源、建议动作；
- `summary today` 与 `today list` 看到的 Today 区域一致。

## P1：`approve` / `resume` 语义需要收紧

### 发现

本次 smoke 中：

```bash
loop-pilot approve <run_id> --note "CLI smoke approval"
loop-pilot resume <run_id>
```

结果：

```text
Approved <run_id>; review_status=approved
Error: cannot resume: run already finalized after approval
```

这说明当前 `approve` 已经 finalizes run。这个设计可以接受，但 CLI help 里 `resume` 的描述是：

```text
Resume an approved or recoverable run
```

容易让用户误解为 approve 后还需要 resume。

### 修改建议

二选一，不要模糊：

1. **approve-finalizes 模式（推荐当前版本）**
   - `approve` 直接把 patch run 终结为 `TERMINATED/succeeded`;
   - `resume` 只用于 interrupted/recoverable runs；
   - 修改 help：`resume` 不再写 “approved”。

2. **approve-then-resume 模式**
   - `approve` 只记录 human decision；
   - `resume` 执行 post-approval validation/finalization；
   - 需要更复杂的恢复语义，不建议当前马上改。

## P2：Daily run 的 recovery 输出需要可解释

### 发现

`loop-pilot run daily --dry-run` 输出：

```text
recovery-scan: 1 finding(s)
```

但随后单独运行：

```bash
loop-pilot recovery-scan
```

显示：

```text
Recovery scan: OK (no issues)
```

且生成的 `daily-summary.md` 中 blocked 区域为空。

### 修改建议

Daily run 如果显示 recovery finding，必须至少输出：

- finding id；
- run id；
- finding type；
- 是否已自动修复/已过期/仅作为运行时提示；
- 对 summary 的影响。

否则用户会以为系统内部状态不一致。

## P2：失败/阻塞 report 太薄

### 发现

真实 adapter 默认阻塞路径可以正确生成 artifacts，但 `report.md` 只有：

```markdown
# Run <run_id>

Outcome: blocked
```

这对人工排障不够。

### 修改建议

阻塞/失败报告至少包含：

- 阻塞原因；
- Gate 状态；
- 触发命令；
- 是否写入外部世界；
- 下一步建议；
- 关键 artifact 链接。

这不影响安全性，但会显著提升可用性。

## P2：README 的 READY 表述建议加脚注

### 发现

README 中 `0.4 READY` 与 `0.5-prep` 同时出现。自动化验收是绿的，但真实日用仍依赖 sqlite profile 和离线 demo 数据。

### 修改建议

README 顶部保留 `0.4 READY`，但加一句：

```text
0.4 READY means offline/sqlite acceptance is green. Real live connectors and unattended autonomy remain blocked by safety gates.
```

这样既不否定当前成果，也避免读者误解为“已经能真实无人值守联网工作”。

