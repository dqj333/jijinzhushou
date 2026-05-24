# 支付宝基金助手

本项目是一个本地基金分析助手：在 `data/funds.json` 中维护支付宝持仓、预算和风险规则，脚本会抓取公开基金净值数据，计算组合仓位、净值位置、近期回撤和风险约束，并生成每日加仓建议。

输出仅用于个人复盘和辅助决策，不构成投资建议，也不保证收益。

## 当前能力

- 读取本地持仓配置和历史净值缓存。
- 从东方财富公开接口更新基金净值。
- 按目标仓位、回调幅度、净值分位、QDII 延迟、单基金/单类别上限等规则评分。
- 生成 Markdown 日报、HTML 看板、结构化交易计划和 AI 提示词上下文。

## 快速开始

启动本地 Web 版：

```powershell
.\run_web.ps1
```

如果 PowerShell 脚本执行策略受限：

```powershell
.\run_web.cmd
```

打开后访问：

```text
http://127.0.0.1:8765
```

Web 第一版提供今日建议、持仓编辑、策略设置、重新计算报告和日报查看。

页面中的“重新计算”不会联网抓取新净值，它会使用 `data/prices/` 里已经保存的本地净值数据，适合你刚改完持仓、收益或预算后立即刷新建议。“联网更新净值”会先访问公开基金接口，再生成报告；如果接口慢或超时，系统会自动改用本地净值继续生成。

推荐在 PowerShell 中运行：

```powershell
.\run_daily.ps1
```

如果 PowerShell 脚本执行策略受限，可以运行：

```powershell
.\run_daily.cmd
```

如果网络较慢，或者只想基于已有缓存重新计算：

```powershell
.\run_cached.cmd
```

也可以直接运行 Python 入口：

```powershell
python scripts/run_daily.py
```

## 输出文件

- `data/reports/latest_dashboard.html`：可视化看板。
- `data/reports/latest_daily_report.md`：文字版日报。
- `data/reports/latest_trade_plan.json`：结构化买入计划。
- `data/reports/latest_context.json`：计算后的完整分析上下文。
- `data/reports/latest_ai_prompt.md`：可交给 AI 继续分析的提示词。

## 配置说明

核心配置文件是 `data/funds.json`。

`profile` 控制整体策略：

- `monthly_budget`：每月计划投入金额，默认按 20 个交易日折算每日预算。
- `daily_budget`：可选；如果设置，则直接作为当日预算。
- `budget_confirmed`：预算是否已经确认；为 `false` 时只输出加仓候选，不给真实买入金额。
- `max_single_fund_ratio`：单只基金最高组合占比。
- `max_sector_fund_ratio`：单个类别最高组合占比。
- `style`：投资风格说明，会写入报告。

每只基金的主要字段：

- `code`：基金代码。
- `name`：基金名称。
- `category`：分类，例如债券、A 股宽基、海外科技、黄金。
- `holding_amount`：当前持有金额。
- `target_ratio`：目标组合占比，例如 `0.12` 表示 12%。
- `screenshot_profit_amount` / `screenshot_profit_pct`：从支付宝持仓截图记录的持有收益。

## 规则概览

脚本会综合以下因素打分：

- 当前净值位置是否偏低。
- 当前仓位是否低于目标仓位。
- 当日是否回调。
- 近一周是否已经涨得过快。
- 当前持仓是否已有较高浮盈。
- 单只基金和分类仓位是否超过上限。
- QDII/海外基金是否存在净值延迟。

然后输出：

- 今日可买基金。
- 每只基金建议金额。
- 可观察和禁止买入清单。
- 组合风险和分类仓位。

## 目录结构

```text
.
├── data/
│   ├── funds.json
│   ├── prices/
│   └── reports/
├── prompts/
├── scripts/
│   ├── fetch_funds.py
│   ├── build_context.py
│   ├── generate_report.py
│   ├── serve_web.py
│   └── run_daily.py
├── web/
├── run_cached.cmd
├── run_daily.cmd
├── run_web.cmd
├── run_web.ps1
└── run_daily.ps1
```

## 后续项目化方向

- 把脚本整理成正式 Python 包，增加命令行参数。
- 增加配置校验，避免基金代码、仓位比例或预算填写错误。
- 增加单元测试和固定样例，保护评分规则不被误改。
- 做一个本地网页界面，支持编辑持仓、查看历史报告和对比每日建议。
