from pathlib import Path
import json

from fund_data import REPORT_DIR, read_json, write_json


MIN_BUY_AMOUNT = 10
TRADING_DAYS_PER_MONTH = 20
MAX_BUY_FUNDS_PER_DAY = 4


def yuan(value):
    if value is None:
        return "未知"
    return f"{value:,.0f} 元"


def pct(value, digits=2):
    if value is None:
        return "未知"
    return f"{value:.{digits}f}%"


def ratio(value):
    if value is None:
        return "未知"
    return f"{value:.1%}"


def nav(value):
    if value is None:
        return "待补数据"
    return str(value)


def classify_position(position):
    if position is None:
        return "数据不足"
    if position <= 25:
        return "偏低"
    if position <= 55:
        return "中性偏低"
    if position <= 75:
        return "中性偏高"
    return "偏高"


def default_daily_budget(profile):
    if profile.get("budget_confirmed") is False:
        return 0.0
    daily_budget = profile.get("daily_budget")
    if daily_budget is not None:
        return float(daily_budget)
    monthly_budget = float(profile.get("monthly_budget") or 0)
    return round(monthly_budget / TRADING_DAYS_PER_MONTH, 2)


def is_bond_fund(fund):
    text = f"{fund.get('category') or ''} {fund.get('type') or ''} {fund.get('name') or ''}"
    return "债券" in text or "短债" in text or "债" in text


def is_qdii_or_overseas(fund):
    text = f"{fund.get('category') or ''} {fund.get('type') or ''} {fund.get('name') or ''}".upper()
    return "QDII" in text or "海外" in text or "港股" in text or "纳斯达克" in text or "标普500" in text


def hard_blocks(fund, context):
    holding = fund["holding"]
    profile = context["profile"]
    portfolio = context["portfolio"]
    data_status = fund.get("data_status") or {}
    current_ratio = holding.get("portfolio_ratio")
    target_ratio = holding.get("target_ratio")
    category = fund.get("category") or "未分类"
    category_ratio = (portfolio.get("category_ratios") or {}).get(category)
    max_sector_ratio = profile.get("max_sector_fund_ratio")
    blocks = []

    if data_status.get("is_stale"):
        blocks.append(data_status.get("reason") or "公开净值数据过期")
    if target_ratio is not None and target_ratio <= 0:
        blocks.append("目标仓位为 0")
    if current_ratio is not None and target_ratio is not None and current_ratio > target_ratio * 1.15:
        blocks.append("当前仓位明显超过目标仓位")
    if category_ratio is not None and max_sector_ratio is not None and category_ratio > max_sector_ratio:
        blocks.append(f"{category} 分类仓位已超过上限")
    return blocks


def evaluate_fund(fund, context):
    holding = fund["holding"]
    metrics = fund["metrics"]
    returns = metrics.get("returns_pct", {})
    position = metrics.get("position_window_pct")
    position_days = metrics.get("position_window_days") or 0
    current_ratio = holding.get("portfolio_ratio")
    target_ratio = holding.get("target_ratio")
    daily_return = fund.get("daily_return_pct")
    one_week = returns.get("1w")
    one_month = returns.get("1m")
    profit_pct = holding.get("profit_pct")
    blocks = hard_blocks(fund, context)
    score = 0.0
    reasons = []
    risks = []

    if blocks:
        return {
            "code": fund["code"],
            "name": fund["name"],
            "tier": "禁止买",
            "score": -99,
            "reasons": ["触发硬性风控"],
            "risks": blocks,
            "latest_date": fund.get("latest_date"),
            "daily_return_pct": fund.get("daily_return_pct"),
            "blocked": True,
        }

    if position is None:
        risks.append("历史净值不足，不能判断位置分位")
    elif position_days < 120:
        risks.append(f"只有近{position_days}条净值，位置分位只作短期参考")
        if position <= 25:
            score += 1
            reasons.append("短期位置偏低")
        elif position >= 80:
            score -= 2
            risks.append("短期位置偏高")
    else:
        if position <= 20:
            score += 3
            reasons.append(f"近{position_days}条净值处于低位")
        elif position <= 40:
            score += 2
            reasons.append(f"近{position_days}条净值位置不高")
        elif position <= 65:
            score += 1
            reasons.append(f"近{position_days}条净值位置中性")
        elif position >= 85:
            score -= 4
            risks.append(f"近{position_days}条净值位置偏高，追涨风险较大")
        elif position >= 75:
            score -= 2
            risks.append(f"近{position_days}条净值位置中性偏高")

    if current_ratio is not None and target_ratio is not None:
        gap = target_ratio - current_ratio
        if gap >= 0.04:
            score += 2
            reasons.append("仓位明显低于目标")
        elif gap > 0.015:
            score += 1
            reasons.append("仓位低于目标")
        elif gap >= 0:
            risks.append("仓位接近目标")

    if daily_return is not None:
        if daily_return <= -2.5:
            score += 1.5
            reasons.append("今日明显回调，适合小额分批")
        elif daily_return <= -0.5:
            score += 0.75
            reasons.append("今日小幅回调")
        elif daily_return >= 2:
            score -= 2
            risks.append("今日涨幅较大，不追高")
        elif daily_return >= 1:
            score -= 1
            risks.append("今日已有上涨")

    if one_week is not None:
        if one_week <= -5:
            score += 1.5
            reasons.append("近一周回撤较多")
        elif one_week <= -2:
            score += 0.75
            reasons.append("近一周有回撤")
        elif one_week >= 6:
            score -= 2
            risks.append("近一周涨幅偏大")
        elif one_week >= 3:
            score -= 1
            risks.append("近一周上涨较快")

    if one_month is not None and one_month >= 10:
        score -= 1
        risks.append("近一月涨幅较大")

    if profit_pct is not None:
        if profit_pct <= -5:
            score += 0.5
            reasons.append("持仓浮亏，可用纪律性小额加仓摊薄")
        elif profit_pct >= 8:
            score -= 1
            risks.append("持仓已有较高浮盈")

    if is_bond_fund(fund):
        score -= 1
        risks.append("债券基金偏稳定仓，不因短期波动频繁加仓")

    if is_qdii_or_overseas(fund):
        risks.append("QDII/海外基金净值有延迟，需要降低对今日涨跌的权重")

    if score >= 4.5:
        tier = "可以买"
    elif score >= 2:
        tier = "可观察"
    elif score <= -2:
        tier = "禁止买"
    else:
        tier = "可观察"

    return {
        "code": fund["code"],
        "name": fund["name"],
        "tier": tier,
        "score": round(score, 2),
        "reasons": reasons or ["没有明显加仓优势"],
        "risks": risks or ["未触发明显单项风险"],
        "latest_date": fund.get("latest_date"),
        "daily_return_pct": fund.get("daily_return_pct"),
        "blocked": tier == "禁止买",
    }


def amount_for_signal(score, daily_budget, remaining):
    if daily_budget < MIN_BUY_AMOUNT or remaining < MIN_BUY_AMOUNT:
        return 0
    if score >= 6:
        base = 40
    elif score >= 4.5:
        base = 30
    elif score >= 3:
        base = 20
    else:
        base = 10
    max_single = max(MIN_BUY_AMOUNT, daily_budget * 0.45)
    amount = min(base, max_single, remaining)
    return int(amount // 10 * 10) if amount >= MIN_BUY_AMOUNT else 0


def allocate_today(context):
    profile = context["profile"]
    daily_budget = default_daily_budget(profile)
    remaining = daily_budget
    evaluated = [evaluate_fund(fund, context) for fund in context["funds"]]
    evaluated.sort(key=lambda item: item["score"], reverse=True)
    decisions = []
    buy_count = 0

    for item in evaluated:
        action = item["tier"]
        amount = 0
        if item["tier"] == "可以买" and buy_count < MAX_BUY_FUNDS_PER_DAY:
            amount = amount_for_signal(item["score"], daily_budget, remaining)
            if amount > 0:
                action = "可以买"
                remaining -= amount
                buy_count += 1
            else:
                action = "可观察"
        decisions.append({**item, "action": action, "amount": amount})

    planned = sum(item["amount"] for item in decisions)
    return {
        "daily_budget": daily_budget,
        "planned_amount": planned,
        "cash_left": round(daily_budget - planned, 2),
        "algorithm": {
            "name": "目标仓位 + 回调增强 + 风险过滤",
            "budget_rule": "月预算按20个交易日折算为日预算，不强行用完",
            "amount_rule": "强信号30-40元，中信号20元，弱信号10元；单日最多买4只",
            "hard_filters": ["数据过期", "仓位明显超目标", "分类仓位超上限", "目标仓位为0"],
        },
        "decisions": decisions,
    }


def render_report(context, plan):
    profile = context["profile"]
    portfolio = context["portfolio"]
    risk_flags = portfolio.get("risk_flags", [])
    buys = [item for item in plan["decisions"] if item["amount"] > 0]
    blocked = [item for item in plan["decisions"] if item["tier"] == "禁止买"]
    watch = [item for item in plan["decisions"] if item["tier"] == "可观察"]

    lines = [
        f"# 基金助手日报 - {context['report_date']}",
        "",
        "> 这是基于公开净值、支付宝持仓截图和本地规则生成的辅助分析，不构成投资建议。",
        "",
        "## 今日结论",
        "",
        f"- 当前持仓总额：{yuan(portfolio['total_value'])}，基金数量：{portfolio['fund_count']} 只",
        f"- 今日预算：{yuan(plan['daily_budget'])}，计划使用：{yuan(plan['planned_amount'])}，暂不使用：{yuan(plan['cash_left'])}",
        f"- 策略：{profile.get('style')}",
        f"- 算法：{plan['algorithm']['name']}；{plan['algorithm']['amount_rule']}",
    ]

    lines.extend(["", "## 可以买", ""])
    if buys:
        for item in buys:
            lines.append(
                f"- {item['name']}（{item['code']}）：{yuan(item['amount'])}。"
                f"评分 {item['score']}；依据：{'；'.join(item['reasons'])}。风险：{'；'.join(item['risks'])}"
            )
    else:
        lines.append("- 今日没有达到买入阈值的标的。")

    lines.extend(["", "## 可观察", ""])
    for item in watch[:8]:
        lines.append(
            f"- {item['name']}（{item['code']}）：评分 {item['score']}。"
            f"依据：{'；'.join(item['reasons'])}。风险：{'；'.join(item['risks'])}"
        )

    lines.extend(["", "## 禁止买", ""])
    for item in blocked:
        lines.append(
            f"- {item['name']}（{item['code']}）：评分 {item['score']}。主要风险：{'；'.join(item['risks'])}"
        )

    lines.extend(["", "## 组合风险", ""])
    if risk_flags:
        for flag in risk_flags:
            lines.append(f"- {flag}")
    else:
        lines.append("- 未触发仓位上限类硬风险。")

    category_ratios = portfolio.get("category_ratios", {})
    if category_ratios:
        category_text = "；".join(f"{name} {ratio(value)}" for name, value in category_ratios.items())
        lines.append(f"- 分类仓位：{category_text}")

    lines.extend(["", "## 单只基金明细", ""])
    decision_by_code = {item["code"]: item for item in plan["decisions"]}
    for fund in context["funds"]:
        holding = fund["holding"]
        metrics = fund["metrics"]
        returns = metrics.get("returns_pct", {})
        decision = decision_by_code[fund["code"]]
        lines.extend(
            [
                f"### {fund['name']}（{fund['code']}）",
                "",
                f"- 档位：{decision['tier']}，金额 {yuan(decision['amount'])}，评分 {decision['score']}",
                f"- 持仓：{yuan(holding.get('current_value'))}，收益 {yuan(holding.get('profit_amount'))} / {pct(holding.get('profit_pct'))}，组合占比 {ratio(holding.get('portfolio_ratio'))}",
                f"- 净值：{nav(fund.get('latest_nav'))}（{fund.get('latest_date') or '待补数据'}），日涨跌 {pct(fund.get('daily_return_pct'))}",
                f"- 表现：1周 {pct(returns.get('1w'))}，1月 {pct(returns.get('1m'))}，3月 {pct(returns.get('3m'))}，1年 {pct(returns.get('1y'))}",
                f"- 数据：{(fund.get('data_status') or {}).get('reason', '未知')}",
                f"- 位置：近{metrics.get('position_window_days', 0)}条净值 {pct(metrics.get('position_window_pct'))}（{classify_position(metrics.get('position_window_pct'))}），最大回撤 {pct(metrics.get('max_drawdown_1y_pct'))}，波动 {pct(metrics.get('annualized_volatility_60d_pct'))}",
                f"- 依据：{'；'.join(decision['reasons'])}",
                f"- 风险：{'；'.join(decision['risks'])}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_ai_input(context, plan):
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "daily_report_prompt.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    payload = {"context": context, "plan": plan}
    return prompt + "\n\n下面是今日 JSON 上下文和规则计划：\n\n```json\n" + json.dumps(
        payload, ensure_ascii=False, indent=2
    ) + "\n```\n"


def escape_html(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_dashboard(context, plan):
    portfolio = context["portfolio"]
    risk_flags = portfolio.get("risk_flags", [])
    rows = []
    for item in plan["decisions"]:
        action_class = {"可以买": "buy", "可观察": "watch", "禁止买": "pause"}.get(item["tier"], "watch")
        rows.append(
            "<tr>"
            f"<td><strong>{escape_html(item['name'])}</strong><span>{escape_html(item['code'])}</span></td>"
            f"<td><b class='{action_class}'>{escape_html(item['tier'])}</b></td>"
            f"<td>{yuan(item['amount'])}</td>"
            f"<td>{escape_html(item.get('latest_date') or '待补')}<span>{pct(item.get('daily_return_pct'))}</span></td>"
            f"<td>{item['score']}</td>"
            f"<td>{escape_html('；'.join(item['reasons']))}</td>"
            f"<td>{escape_html('；'.join(item['risks']))}</td>"
            "</tr>"
        )

    risk_html = "".join(f"<li>{escape_html(flag)}</li>" for flag in risk_flags) or "<li>未触发仓位上限类硬风险。</li>"
    category_html = "".join(
        f"<span>{escape_html(name)} <strong>{ratio(value)}</strong></span>"
        for name, value in portfolio.get("category_ratios", {}).items()
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>基金助手日报 - {escape_html(context['report_date'])}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f6f7fb; }}
    header {{ padding: 28px 32px; background: #ffffff; border-bottom: 1px solid #e6e8ef; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric, section {{ background: #fff; border: 1px solid #e6e8ef; border-radius: 8px; }}
    .metric {{ padding: 16px; }}
    .metric span {{ display: block; color: #667085; font-size: 13px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 24px; }}
    section {{ padding: 18px; margin-bottom: 18px; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{ padding: 12px; border-top: 1px solid #edf0f5; text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ color: #667085; font-weight: 600; background: #fafbfe; }}
    td span {{ display: block; color: #667085; font-size: 12px; margin-top: 4px; }}
    b.buy {{ color: #0f8a4c; }}
    b.pause {{ color: #c2410c; }}
    b.watch {{ color: #475467; }}
    ul {{ margin: 0; padding-left: 20px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chips span {{ padding: 7px 10px; background: #f2f4f7; border-radius: 999px; color: #344054; font-size: 13px; }}
    @media (max-width: 860px) {{
      main {{ padding: 14px; }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ table-layout: auto; }}
      th:nth-child(6), td:nth-child(6), th:nth-child(7), td:nth-child(7) {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>基金助手日报</h1>
    <div>{escape_html(context['report_date'])} · 目标仓位 + 回调增强 + 风险过滤</div>
  </header>
  <main>
    <div class="grid">
      <div class="metric"><span>持仓总额</span><strong>{yuan(portfolio['total_value'])}</strong></div>
      <div class="metric"><span>今日预算</span><strong>{yuan(plan['daily_budget'])}</strong></div>
      <div class="metric"><span>计划买入</span><strong>{yuan(plan['planned_amount'])}</strong></div>
      <div class="metric"><span>暂不使用</span><strong>{yuan(plan['cash_left'])}</strong></div>
    </div>
    <section>
      <h2>今日计划</h2>
      <table>
        <thead><tr><th>基金</th><th>档位</th><th>金额</th><th>净值日/涨跌</th><th>评分</th><th>依据</th><th>风险</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    <section>
      <h2>组合风险</h2>
      <ul>{risk_html}</ul>
    </section>
    <section>
      <h2>分类仓位</h2>
      <div class="chips">{category_html}</div>
    </section>
  </main>
</body>
</html>
"""


def main():
    context = read_json(REPORT_DIR / "latest_context.json")
    plan = allocate_today(context)
    report = render_report(context, plan)
    report_path = REPORT_DIR / f"daily-report-{context['report_date']}.md"
    latest_report_path = REPORT_DIR / "latest_daily_report.md"
    ai_prompt_path = REPORT_DIR / "latest_ai_prompt.md"
    plan_path = REPORT_DIR / "latest_trade_plan.json"
    dashboard_path = REPORT_DIR / "latest_dashboard.html"
    report_path.write_text(report, encoding="utf-8")
    latest_report_path.write_text(report, encoding="utf-8")
    ai_prompt_path.write_text(render_ai_input(context, plan), encoding="utf-8")
    write_json(plan_path, plan)
    dashboard_path.write_text(render_dashboard(context, plan), encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"Wrote {latest_report_path}")
    print(f"Wrote {ai_prompt_path}")
    print(f"Wrote {plan_path}")
    print(f"Wrote {dashboard_path}")


if __name__ == "__main__":
    main()
