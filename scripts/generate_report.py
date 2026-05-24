from pathlib import Path
import json

from fund_data import REPORT_DIR, read_json, write_json


MIN_BUY_AMOUNT = 10
TRADING_DAYS_PER_MONTH = 20
MAX_BUY_FUNDS_PER_DAY = 4
QUALITY_BUY_THRESHOLD = 65


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


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


def is_index_fund(fund):
    text = f"{fund.get('category') or ''} {fund.get('type') or ''} {fund.get('name') or ''}"
    return "指数" in text or "ETF" in text or "联接" in text


def component_label(score):
    if score >= 80:
        return "优秀"
    if score >= 65:
        return "合格"
    if score >= 50:
        return "一般"
    return "偏弱"


def score_risk_adjusted_return(fund):
    metrics = fund["metrics"]
    returns = metrics.get("returns_pct", {})
    annual_return = returns.get("1y")
    if annual_return is None and returns.get("6m") is not None:
        annual_return = returns["6m"] * 2
    if annual_return is None and returns.get("3m") is not None:
        annual_return = returns["3m"] * 4

    volatility = metrics.get("annualized_volatility_60d_pct")
    if annual_return is None:
        return 45, "风险调整收益数据不足"
    if volatility is None or volatility <= 0:
        volatility = 3 if is_bond_fund(fund) else 20

    risk_adjusted = annual_return / max(volatility, 1)
    score = 45 + risk_adjusted * 28
    if annual_return > 0:
        score += 5
    return clamp(round(score, 1)), f"近似风险调整收益 {risk_adjusted:.2f}"


def score_drawdown_control(fund):
    drawdown = fund["metrics"].get("max_drawdown_1y_pct")
    if drawdown is None:
        return 50, "最大回撤数据不足"
    dd = abs(drawdown)
    if is_bond_fund(fund):
        score = 95 - dd * 8
    else:
        score = 95 - dd * 2.2
    return clamp(round(score, 1)), f"近一年最大回撤 {pct(drawdown)}"


def score_stability(fund):
    metrics = fund["metrics"]
    returns = metrics.get("returns_pct", {})
    periods = [returns.get(key) for key in ("1w", "1m", "3m", "6m", "1y")]
    known = [value for value in periods if value is not None]
    if not known:
        return 45, "收益稳定性数据不足"

    positive_ratio = sum(1 for value in known if value > 0) / len(known)
    volatility = metrics.get("annualized_volatility_60d_pct")
    score = 45 + positive_ratio * 35
    if volatility is not None:
        if is_bond_fund(fund):
            score += max(0, 12 - volatility) * 1.5
        else:
            score += max(0, 25 - volatility) * 0.6
    return clamp(round(score, 1)), f"{len(known)} 个观察周期中 {positive_ratio:.0%} 为正收益"


def score_category_fit(fund):
    text = f"{fund.get('category') or ''} {fund.get('type') or ''} {fund.get('name') or ''}"
    if is_bond_fund(fund):
        return 68, "债券类适合作为稳定仓，但不作为进攻加仓核心"
    if "宽基" in text or "沪深300" in text or "中证A500" in text or "标普500" in text:
        return 82, "宽基/海外宽基分散度较高"
    if "红利" in text or "低波" in text:
        return 78, "红利低波类具备防守和分红属性"
    if "黄金" in text:
        return 72, "黄金更适合作为组合对冲资产"
    if "科技" in text or "纳斯达克" in text or "港股" in text or "农业" in text:
        return 62, "主题/行业波动较大，需要控制仓位"
    if "主动" in text or "混合" in text or "股票" in text:
        return 58, "主动权益需要补充经理和同类排名数据"
    return 60, "类别适配数据不足"


def score_data_quality(fund):
    metrics = fund["metrics"]
    data_status = fund.get("data_status") or {}
    rows = metrics.get("history_rows") or 0
    score = 35
    if rows >= 250:
        score += 45
    elif rows >= 120:
        score += 32
    elif rows >= 60:
        score += 20
    if not data_status.get("is_stale"):
        score += 20
    else:
        days_old = data_status.get("days_old")
        if days_old is not None and days_old <= 7:
            score += 8
    return clamp(round(score, 1)), f"历史净值 {rows} 条；{data_status.get('reason', '数据状态未知')}"


def fund_quality_score(fund):
    risk_return, risk_return_note = score_risk_adjusted_return(fund)
    drawdown, drawdown_note = score_drawdown_control(fund)
    stability, stability_note = score_stability(fund)
    category_fit, category_note = score_category_fit(fund)
    data_quality, data_note = score_data_quality(fund)

    if is_index_fund(fund):
        weights = {
            "risk_adjusted_return": 0.35,
            "drawdown_control": 0.25,
            "stability": 0.15,
            "category_fit": 0.15,
            "data_quality": 0.10,
        }
    else:
        weights = {
            "risk_adjusted_return": 0.30,
            "drawdown_control": 0.25,
            "stability": 0.15,
            "category_fit": 0.10,
            "data_quality": 0.20,
        }

    components = {
        "risk_adjusted_return": {
            "score": risk_return,
            "label": "风险调整收益",
            "note": risk_return_note,
        },
        "drawdown_control": {
            "score": drawdown,
            "label": "回撤控制",
            "note": drawdown_note,
        },
        "stability": {
            "score": stability,
            "label": "稳定性",
            "note": stability_note,
        },
        "category_fit": {
            "score": category_fit,
            "label": "类别适配",
            "note": category_note,
        },
        "data_quality": {
            "score": data_quality,
            "label": "数据质量",
            "note": data_note,
        },
    }
    score = sum(components[key]["score"] * weight for key, weight in weights.items())
    return round(score, 1), components


def allocation_need(fund, context, daily_budget):
    holding = fund["holding"]
    current_value = holding.get("current_value") or 0
    target_ratio = holding.get("target_ratio")
    total_after_budget = (context["portfolio"].get("total_value") or 0) + daily_budget
    if target_ratio is None or target_ratio <= 0 or total_after_budget <= 0:
        return {
            "target_amount": 0,
            "gap_amount": 0,
            "gap_ratio": 0,
            "score": 0,
            "note": "目标仓位未设置",
        }

    target_amount = target_ratio * total_after_budget
    gap_amount = target_amount - current_value
    gap_ratio = gap_amount / target_amount if target_amount > 0 else 0

    if gap_amount <= 0:
        score = 0
        note = "当前仓位不低于目标，不使用新增资金"
    elif gap_ratio < 0.05:
        score = 20
        note = "仓位接近目标，避免频繁微调"
    elif gap_ratio < 0.15:
        score = 45
        note = "轻微低配，可小额补齐"
    elif gap_ratio < 0.30:
        score = 70
        note = "明显低配，优先补齐"
    else:
        score = 90
        note = "严重低配，但仍受单日预算限制"

    return {
        "target_amount": round(target_amount, 2),
        "gap_amount": round(gap_amount, 2),
        "gap_ratio": round(gap_ratio, 4),
        "score": score,
        "note": note,
    }


def opportunity_factor(fund):
    metrics = fund["metrics"]
    returns = metrics.get("returns_pct", {})
    position = metrics.get("position_window_pct")
    one_week = returns.get("1w")
    one_month = returns.get("1m")
    drawdown = metrics.get("max_drawdown_1y_pct")

    factor = 1.0
    notes = []

    if position is not None:
        if position <= 20:
            factor += 0.18
            notes.append("净值处于历史低位")
        elif position <= 40:
            factor += 0.08
            notes.append("净值位置不高")
        elif position >= 85:
            factor -= 0.22
            notes.append("净值位置偏高")
        elif position >= 75:
            factor -= 0.12
            notes.append("净值位置中性偏高")

    if one_week is not None:
        if one_week <= -5:
            factor += 0.12
            notes.append("近一周回撤较大")
        elif one_week <= -2:
            factor += 0.06
            notes.append("近一周有回撤")
        elif one_week >= 6:
            factor -= 0.16
            notes.append("近一周上涨过快")
        elif one_week >= 3:
            factor -= 0.08
            notes.append("近一周涨幅较快")

    if one_month is not None and one_month >= 10:
        factor -= 0.10
        notes.append("近一月涨幅较大")

    if drawdown is not None and drawdown <= -25 and not is_bond_fund(fund):
        factor += 0.05
        notes.append("当前资产历史回撤较深，允许小幅提高补仓优先级")

    if is_qdii_or_overseas(fund):
        factor -= 0.03
        notes.append("QDII/海外基金净值存在延迟，机会因子保守处理")

    factor = round(max(0.7, min(1.3, factor)), 2)
    return factor, notes or ["无明显估值/回撤机会，机会因子保持中性"]


def data_confidence(fund):
    data_status = fund.get("data_status") or {}
    rows = fund["metrics"].get("history_rows") or 0
    confidence = 1.0
    notes = []
    if rows < 120:
        confidence -= 0.15
        notes.append("历史净值不足 120 条")
    if data_status.get("is_stale"):
        days_old = data_status.get("days_old")
        if days_old is None:
            confidence -= 0.35
        elif days_old > 10:
            confidence -= 0.30
        elif days_old > 5:
            confidence -= 0.18
        else:
            confidence -= 0.10
        notes.append(data_status.get("reason") or "净值数据不是最新")
    return round(max(0.45, min(1.0, confidence)), 2), notes


def hard_blocks(fund, context):
    holding = fund["holding"]
    profile = context["profile"]
    portfolio = context["portfolio"]
    data_status = fund.get("data_status") or {}
    current_ratio = holding.get("portfolio_ratio")
    target_ratio = holding.get("target_ratio")
    category = fund.get("category") or "未分类"
    category_ratio = (portfolio.get("category_ratios") or {}).get(category)
    max_single_ratio = profile.get("max_single_fund_ratio")
    max_sector_ratio = profile.get("max_sector_fund_ratio")
    blocks = []

    if not fund.get("latest_date"):
        blocks.append("没有可用净值数据")
    if data_status.get("days_old") is not None and data_status["days_old"] > (12 if is_qdii_or_overseas(fund) else 8):
        blocks.append("净值数据过旧，不能新增买入")
    if target_ratio is not None and target_ratio <= 0:
        blocks.append("目标仓位为 0")
    if current_ratio is not None and target_ratio is not None and current_ratio > target_ratio * 1.20:
        blocks.append("当前仓位超过目标仓位 120%")
    if current_ratio is not None and max_single_ratio and current_ratio > max_single_ratio:
        blocks.append("单只基金仓位超过组合上限")
    if category_ratio is not None and max_sector_ratio is not None and category_ratio > max_sector_ratio:
        blocks.append(f"{category} 分类仓位已超过上限")
    return blocks


def evaluate_fund(fund, context, daily_budget):
    quality_score, quality_components = fund_quality_score(fund)
    allocation = allocation_need(fund, context, daily_budget)
    opportunity, opportunity_notes = opportunity_factor(fund)
    confidence, confidence_notes = data_confidence(fund)
    blocks = hard_blocks(fund, context)

    priority = round((quality_score / 100) * allocation["score"] * opportunity * confidence, 2)
    reasons = [
        f"基金质量 {quality_score}/100（{component_label(quality_score)}）",
        f"配置缺口 {yuan(allocation['gap_amount'])}，偏离 {ratio(allocation['gap_ratio'])}：{allocation['note']}",
        f"机会因子 {opportunity}：{'；'.join(opportunity_notes)}",
    ]
    risks = []
    if confidence_notes:
        risks.extend(confidence_notes)
    if quality_score < QUALITY_BUY_THRESHOLD:
        risks.append(f"基金质量分低于买入阈值 {QUALITY_BUY_THRESHOLD}")
    if allocation["gap_amount"] <= 0:
        risks.append("组合不需要继续补该标的")
    if blocks:
        risks.extend(blocks)

    if blocks:
        tier = "禁止买"
        priority = 0
        blocked = True
    elif quality_score < 50:
        tier = "禁止买"
        blocked = True
    elif quality_score < QUALITY_BUY_THRESHOLD or allocation["score"] < 45:
        tier = "可观察"
        blocked = False
    elif priority >= 45:
        tier = "可以买"
        blocked = False
    else:
        tier = "可观察"
        blocked = False

    return {
        "code": fund["code"],
        "name": fund["name"],
        "tier": tier,
        "score": priority,
        "priority_score": priority,
        "quality_score": quality_score,
        "allocation_score": allocation["score"],
        "opportunity_factor": opportunity,
        "data_confidence": confidence,
        "quality_components": quality_components,
        "allocation": allocation,
        "reasons": reasons,
        "risks": risks or ["未触发明显单项风险"],
        "latest_date": fund.get("latest_date"),
        "daily_return_pct": fund.get("daily_return_pct"),
        "blocked": blocked,
    }


def allocate_amounts(evaluated, daily_budget):
    candidates = [
        item
        for item in evaluated
        if item["tier"] == "可以买" and item["priority_score"] > 0 and item["allocation"]["gap_amount"] > 0
    ]
    candidates.sort(key=lambda item: item["priority_score"], reverse=True)
    candidates = candidates[:MAX_BUY_FUNDS_PER_DAY]
    if daily_budget < MIN_BUY_AMOUNT or not candidates:
        return {item["code"]: 0 for item in evaluated}

    total_priority = sum(item["priority_score"] for item in candidates)
    remaining = int(daily_budget // 10 * 10)
    amounts = {item["code"]: 0 for item in evaluated}
    max_single = int(max(MIN_BUY_AMOUNT, daily_budget * 0.50) // 10 * 10)

    for item in candidates:
        raw_amount = daily_budget * item["priority_score"] / total_priority
        amount = min(raw_amount, max_single, item["allocation"]["gap_amount"])
        amount = int(amount // 10 * 10)
        if amount >= MIN_BUY_AMOUNT:
            amounts[item["code"]] = amount
            remaining -= amount

    while remaining >= MIN_BUY_AMOUNT:
        changed = False
        for item in candidates:
            code = item["code"]
            if remaining < MIN_BUY_AMOUNT:
                break
            if amounts[code] + MIN_BUY_AMOUNT > max_single:
                continue
            if amounts[code] + MIN_BUY_AMOUNT > item["allocation"]["gap_amount"]:
                continue
            amounts[code] += MIN_BUY_AMOUNT
            remaining -= MIN_BUY_AMOUNT
            changed = True
        if not changed:
            break

    return amounts


def allocate_today(context):
    profile = context["profile"]
    daily_budget = default_daily_budget(profile)
    evaluated = [evaluate_fund(fund, context, daily_budget) for fund in context["funds"]]
    evaluated.sort(key=lambda item: item["priority_score"], reverse=True)
    amounts = allocate_amounts(evaluated, daily_budget)

    decisions = []
    for item in evaluated:
        amount = amounts.get(item["code"], 0)
        action = item["tier"]
        if item["tier"] == "可以买" and amount <= 0:
            action = "可观察"
        decisions.append({**item, "action": action, "amount": amount})

    planned = sum(item["amount"] for item in decisions)
    return {
        "daily_budget": daily_budget,
        "planned_amount": planned,
        "cash_left": round(daily_budget - planned, 2),
        "algorithm": {
            "name": "基金质量 + 组合再平衡 + 机会因子",
            "budget_rule": "月预算按约20个交易日折算为日预算；新增资金优先补低配资产，不强行用完",
            "amount_rule": "候选需质量分>=65且低配；按优先级比例分配；单只最高50%日预算；单日最多4只",
            "hard_filters": [
                "无可用净值或数据过旧",
                "目标仓位为0",
                "仓位超过目标120%",
                "单基金或分类仓位超过上限",
            ],
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
                f"优先级 {item['priority_score']}；质量 {item['quality_score']}/100；"
                f"配置缺口 {yuan(item['allocation']['gap_amount'])}；机会因子 {item['opportunity_factor']}。"
                f"依据：{'；'.join(item['reasons'])}。风险：{'；'.join(item['risks'])}"
            )
    else:
        lines.append("- 今日没有达到买入阈值的标的。")

    lines.extend(["", "## 可观察", ""])
    for item in watch[:8]:
        lines.append(
            f"- {item['name']}（{item['code']}）：优先级 {item['priority_score']}，质量 {item['quality_score']}/100。"
            f"依据：{'；'.join(item['reasons'])}。风险：{'；'.join(item['risks'])}"
        )

    lines.extend(["", "## 禁止买", ""])
    for item in blocked:
        lines.append(
            f"- {item['name']}（{item['code']}）：质量 {item['quality_score']}/100。主要原因：{'；'.join(item['risks'])}"
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
        components = decision["quality_components"]
        component_text = "；".join(
            f"{value['label']} {value['score']}" for value in components.values()
        )
        lines.extend(
            [
                f"### {fund['name']}（{fund['code']}）",
                "",
                f"- 档位：{decision['action']}，金额 {yuan(decision['amount'])}，优先级 {decision['priority_score']}",
                f"- 分层评分：质量 {decision['quality_score']}/100，配置 {decision['allocation_score']}/100，机会因子 {decision['opportunity_factor']}，数据可信度 {decision['data_confidence']}",
                f"- 质量分项：{component_text}",
                f"- 配置缺口：目标 {yuan(decision['allocation']['target_amount'])}，缺口 {yuan(decision['allocation']['gap_amount'])}，偏离 {ratio(decision['allocation']['gap_ratio'])}",
                f"- 持仓：{yuan(holding.get('current_value'))}，收益 {yuan(holding.get('profit_amount'))} / {pct(holding.get('profit_pct'))}，组合占比 {ratio(holding.get('portfolio_ratio'))}",
                f"- 净值：{nav(fund.get('latest_nav'))}（{fund.get('latest_date') or '待补数据'}），日涨跌 {pct(fund.get('daily_return_pct'))}",
                f"- 表现：1周 {pct(returns.get('1w'))}，1月 {pct(returns.get('1m'))}，3月 {pct(returns.get('3m'))}，1年 {pct(returns.get('1y'))}",
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
        action_class = {"可以买": "buy", "可观察": "watch", "禁止买": "pause"}.get(item["action"], "watch")
        rows.append(
            "<tr>"
            f"<td><strong>{escape_html(item['name'])}</strong><span>{escape_html(item['code'])}</span></td>"
            f"<td><b class='{action_class}'>{escape_html(item['action'])}</b></td>"
            f"<td>{yuan(item['amount'])}</td>"
            f"<td>{item['quality_score']}</td>"
            f"<td>{item['allocation_score']}</td>"
            f"<td>{item['opportunity_factor']}</td>"
            f"<td>{item['priority_score']}</td>"
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
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric, section {{ background: #fff; border: 1px solid #e6e8ef; border-radius: 8px; }}
    .metric {{ padding: 16px; }}
    .metric span {{ display: block; color: #667085; font-size: 13px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 24px; }}
    section {{ padding: 18px; margin-bottom: 18px; overflow: auto; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 1100px; }}
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
    }}
  </style>
</head>
<body>
  <header>
    <h1>基金助手日报</h1>
    <div>{escape_html(context['report_date'])} · 基金质量 + 组合再平衡 + 机会因子</div>
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
        <thead><tr><th>基金</th><th>动作</th><th>金额</th><th>质量</th><th>配置</th><th>机会</th><th>优先级</th><th>依据</th><th>风险</th></tr></thead>
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
