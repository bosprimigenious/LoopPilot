# WSL 部署与小程序端

本文是 LoopPilot 在个人设备上的下一阶段落地计划：先把 WSL 部署链路做成可重复验证的本地运行环境，再开发一个轻量小程序端，用来查看每日状态、运行记录和人工审阅事项。

## 目标

1. **WSL 一键跑通**：在全新或已有 WSL Ubuntu 环境中，自动完成 clone/pull、虚拟环境、依赖安装、健康检查、测试、验收和 CLI smoke。
2. **移动端可观察**：小程序端先做只读 dashboard 和 review queue，不直接执行危险动作。
3. **安全边界不后退**：小程序端不得绕过 `SafetyGate`、`ReviewService` 或 CLI 的人工审批规则。

## WSL 部署链路

推荐入口：

```bash
bash scripts/deploy_wsl.sh
```

常用参数：

```bash
bash scripts/deploy_wsl.sh --repo-dir "$HOME/LoopPilot"
bash scripts/deploy_wsl.sh --skip-full-tests
bash scripts/deploy_wsl.sh --skip-acceptance
bash scripts/deploy_wsl.sh --skip-api-smoke
bash scripts/deploy_wsl.sh --no-pull
```

全新 WSL 环境建议先安装系统依赖：

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip
```

脚本完成后会输出：

- 仓库路径
- 虚拟环境激活命令
- 部署日志路径 `var/logs/wsl-deploy-*.log`

## 验收标准

WSL 链路完成时至少应通过：

```bash
loop-pilot doctor
loop-pilot adapters doctor
ruff check .
python scripts/verify_api_bridge_contract.py
python scripts/verify_wechat_miniprogram_static.py
python -m pytest -q
python scripts/verify_0_4_acceptance.py
python scripts/verify_0_5_prep.py
loop-pilot run all --fixture-set mini --dry-run
loop-pilot api serve --host 127.0.0.1 --port 17860  # 脚本会临时启动并检查 /api/health
```

其中 `InternLoop` / `PaperLoop` 在 dry-run smoke 中得到 `partial` 是预期结果，因为 patch/revision 需要人工 review 后才能最终通过。

## 小程序端 MVP

首版按微信小程序实现，目录为：

```text
clients/wechat-miniprogram/
```

MVP 页面：

| 页面 | 作用 | 数据来源 |
|------|------|----------|
| 首页 | 今日概览、最新运行、待审阅数量 | mock，后续接本地 API |
| 运行 | 最近 run 列表、详情与 outcome | mock，后续接 `/api/runs`、`/api/runs/{run_id}` |
| 审阅 | 待处理 review item、只读详情与关联 run 快照 | mock，后续接 `/api/reviews`、`/api/reviews/{run_id}` |
| 设置 | 配置 API base URL、切换 mock/live | local storage |

首版不做：

- 自动 approve
- 自动运行 unattended daily
- 真实远端写入
- 云端账号、多用户权限

## 后端接口边界

小程序不能直接执行本地 CLI，因此后续需要一个本地只读 API bridge。建议作为独立阶段实现：

```text
src/loop_pilot/api/
```

候选接口：

```text
GET  /api/health
GET  /api/summary/today
GET  /api/runs
GET  /api/runs/{run_id}
GET  /api/reviews
GET  /api/reviews/{run_id}
POST /api/reviews/{run_id}/approve   # 后置，必须仍走 ReviewService
POST /api/reviews/{run_id}/reject    # 后置，必须带 reason
```

只读 API bridge 已提供第一版入口：

```bash
loop-pilot api serve --host 127.0.0.1 --port 7860
```

`/api/health` 返回版本、状态后端、只读标记、endpoint 清单和写接口禁用状态，供小程序设置页确认 live 连接边界。`/api/summary/today` 返回今日 run 数、阻塞数、outcome 计数、最近运行和待审阅预览，供小程序首页只读展示。`/api/runs/{run_id}` 返回运行详情、`reportPath` 和 manifest 中的只读 `artifacts` 预览，供小程序运行详情页复制报告/产物路径。

`python scripts/verify_api_bridge_contract.py` 不绑定端口，使用临时 SQLite 状态验证 health、today summary、run artifact 预览、review 详情和 POST 拒绝，适合 WSL 部署前置检查。

第一阶段小程序端默认消费 mock 数据；第二阶段可在设置页关闭 mock 并配置上述 API base URL。live API 请求失败时页面会回退 mock 数据并显示数据源/错误提示；第三阶段再接人工确认后的 review 操作。

## 开发顺序

1. 完成并验证 `scripts/deploy_wsl.sh`。
2. 将 WSL 快速入口写入 README。
3. 建立小程序端目录、页面、mock 数据和 API adapter。
4. 增加本地 API bridge 规格与只读实现。（已开始：`loop-pilot api serve`）
5. 小程序从 mock 切换到 live base URL，并验证真机/开发者工具访问方式。
6. 在 review 操作前加入二次确认和后端安全门禁。

## 安全原则

- 小程序端只是操作入口，不是权限来源。
- 所有状态变更必须回到 LoopPilot 后端服务层。
- patch review 仍然必须由人类明确操作，不能自动 approve。
- 未配置 live API 时，小程序默认使用 mock 数据，避免误触发本地运行。
