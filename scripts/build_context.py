from fund_data import (
    CONFIG_PATH,
    PRICE_DIR,
    REPORT_DIR,
    NavPoint,
    annualized_volatility,
    latest_report_date,
    max_drawdown,
    pct_change,
    percentile_position,
    read_json,
    safe_round,
    value_at,
    write_json,
)
from datetime import date


PERIODS = {
    "1w": 5,
    "1m": 20,
    "3m": 60,
    "6m": 120,
    "1y": 250,
}


def main():
    config = read_json(CONFIG_PATH)
    profile = config["profile"]
    fund_summaries = []
    total_value = 0.0

    for fund in config["funds"]:
        code = fund["code"]
        price_file = PRICE_DIR / f"{code}.json"
        screenshot_profit_amount = fund.get("screenshot_profit_amount")
        screenshot_profit_pct = fund.get("screenshot_profit_pct")
        holding_amount = fund.get("holding_amount")
        if not price_file.exists():
            fund_summaries.append(
                {
                    "code": code,
                    "name": fund.get("name"),
                    "type": fund.get("type"),
                    "category": fund.get("category"),
                    "notes": (fund.get("notes") or "") + "；公开净值数据暂未抓取成功",
                    "latest_date": None,
                    "latest_nav": None,
                    "daily_return_pct": None,
                    "estimate": None,
                    "data_status": {
                        "is_stale": True,
                        "days_old": None,
                        "max_allowed_days": None,
                        "reason": "没有可用公开净值缓存",
                    },
                    "holding": {
                        "shares": fund.get("shares"),
                        "cost_nav": fund.get("cost_nav"),
                        "cost_amount": safe_round(holding_amount - screenshot_profit_amount)
                        if holding_amount is not None and screenshot_profit_amount is not None
                        else holding_amount,
                        "current_value": holding_amount,
                        "profit_amount": screenshot_profit_amount,
                        "profit_pct": screenshot_profit_pct,
                        "monthly_plan": fund.get("monthly_plan", 0),
                        "target_ratio": fund.get("target_ratio"),
                        "screenshot_profit_amount": screenshot_profit_amount,
                        "screenshot_profit_pct": screenshot_profit_pct,
                        "screenshot_yesterday_profit": fund.get("screenshot_yesterday_profit"),
                    },
                    "metrics": {
                        "returns_pct": {"1w": None, "1m": None, "3m": None, "6m": None, "1y": None},
                        "max_drawdown_1y_pct": None,
                        "max_drawdown_all_pct": None,
                        "position_60d_pct": None,
                        "position_250d_pct": None,
                        "position_window_pct": None,
                        "position_window_days": 0,
                        "annualized_volatility_60d_pct": None,
                        "history_rows": 0,
                    },
                }
            )
            total_value += holding_amount or 0
            continue

        prices = read_json(price_file)
        points = [
            NavPoint(
                nav_date=row["date"],
                nav=row["nav"],
                accumulated_nav=row.get("accumulated_nav"),
                daily_return_pct=row.get("daily_return_pct"),
            )
            for row in prices.get("history", [])
        ]
        if not points:
            continue

        latest = points[0]
        latest_nav = latest.nav
        shares = fund.get("shares")
        cost_nav = fund.get("cost_nav")

        if shares is None and holding_amount and cost_nav:
            shares = holding_amount / cost_nav
        current_value = shares * latest_nav if shares else holding_amount
        if shares and cost_nav:
            cost_amount = shares * cost_nav
            profit_amount = current_value - cost_amount if current_value is not None else None
            profit_pct = pct_change(current_value, cost_amount) if current_value is not None else None
        elif current_value is not None and screenshot_profit_amount is not None:
            cost_amount = current_value - screenshot_profit_amount
            profit_amount = screenshot_profit_amount
            profit_pct = screenshot_profit_pct if screenshot_profit_pct is not None else pct_change(current_value, cost_amount)
        else:
            cost_amount = holding_amount
            profit_amount = None
            profit_pct = None
        total_value += current_value or 0

        values_latest_first = [item.nav for item in points]
        values_oldest_first = list(reversed(values_latest_first))
        returns = {
            label: safe_round(pct_change(latest_nav, value_at(points, days)))
            for label, days in PERIODS.items()
        }

        history_rows = len(points)
        position_window_days = min(history_rows, 250)
        freshness = data_freshness(latest.nav_date, fund.get("type"), fund.get("category"))

        summary = {
            "code": code,
            "name": fund.get("name") or prices.get("estimate", {}).get("name"),
            "type": fund.get("type"),
            "category": fund.get("category"),
            "notes": fund.get("notes"),
            "latest_date": latest.nav_date,
            "latest_nav": latest_nav,
            "daily_return_pct": latest.daily_return_pct,
            "estimate": prices.get("estimate"),
            "data_status": freshness,
            "holding": {
                "shares": safe_round(shares, 4) if shares else None,
                "cost_nav": cost_nav,
                "cost_amount": safe_round(cost_amount),
                "current_value": safe_round(current_value),
                "profit_amount": safe_round(profit_amount),
                "profit_pct": safe_round(profit_pct),
                "monthly_plan": fund.get("monthly_plan", 0),
                "target_ratio": fund.get("target_ratio"),
                "screenshot_profit_amount": screenshot_profit_amount,
                "screenshot_profit_pct": screenshot_profit_pct,
                "screenshot_yesterday_profit": fund.get("screenshot_yesterday_profit"),
            },
            "metrics": {
                "returns_pct": returns,
                "max_drawdown_1y_pct": safe_round(max_drawdown(list(reversed(values_latest_first[:250])))),
                "max_drawdown_all_pct": safe_round(max_drawdown(values_oldest_first)),
                "position_60d_pct": safe_round(percentile_position(values_latest_first[:60], latest_nav)),
                "position_250d_pct": safe_round(percentile_position(values_latest_first[:250], latest_nav)),
                "position_window_pct": safe_round(percentile_position(values_latest_first[:position_window_days], latest_nav)),
                "position_window_days": position_window_days,
                "annualized_volatility_60d_pct": safe_round(annualized_volatility(points, 60)),
                "history_rows": history_rows,
            },
        }
        fund_summaries.append(summary)

    category_totals = {}
    for item in fund_summaries:
        current_value = item["holding"]["current_value"] or 0
        item["holding"]["portfolio_ratio"] = safe_round(current_value / total_value, 4) if total_value else None
        category = item.get("category") or "未分类"
        category_totals[category] = category_totals.get(category, 0) + current_value

    category_ratios = {
        category: safe_round(value / total_value, 4) if total_value else None
        for category, value in category_totals.items()
    }

    risk_flags = []
    max_single = profile.get("max_single_fund_ratio")
    max_sector = profile.get("max_sector_fund_ratio")
    for item in fund_summaries:
        ratio = item["holding"]["portfolio_ratio"]
        if ratio is not None and max_single and ratio > max_single:
            risk_flags.append(f"{item['name']} 仓位 {ratio:.1%} 超过单只基金上限 {max_single:.0%}")
    for category, ratio in category_ratios.items():
        if ratio is not None and max_sector and ratio > max_sector:
            risk_flags.append(f"{category} 类基金合计仓位 {ratio:.1%} 超过分类上限 {max_sector:.0%}")

    context = {
        "report_date": latest_report_date(),
        "profile": profile,
        "portfolio": {
            "total_value": safe_round(total_value),
            "fund_count": len(fund_summaries),
            "category_ratios": category_ratios,
            "risk_flags": risk_flags,
        },
        "funds": fund_summaries,
    }

    output = REPORT_DIR / f"context-{context['report_date']}.json"
    write_json(output, context)
    write_json(REPORT_DIR / "latest_context.json", context)
    print(f"Wrote {output}")


def data_freshness(latest_date: str | None, fund_type: str | None, category: str | None):
    if not latest_date:
        return {
            "is_stale": True,
            "days_old": None,
            "max_allowed_days": None,
            "reason": "没有公开净值日期",
        }
    latest = date.fromisoformat(latest_date)
    days_old = (date.today() - latest).days
    text = f"{fund_type or ''} {category or ''}".upper()
    is_qdii = "QDII" in text or "海外" in text or "港股" in text
    max_allowed_days = 5 if is_qdii else 3
    return {
        "is_stale": days_old > max_allowed_days,
        "days_old": days_old,
        "max_allowed_days": max_allowed_days,
        "reason": f"净值距今天 {days_old} 天，{'QDII/海外基金' if is_qdii else '境内基金'}允许 {max_allowed_days} 天内",
    }


if __name__ == "__main__":
    main()
