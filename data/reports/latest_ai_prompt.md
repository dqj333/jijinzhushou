你是一个谨慎的个人基金分析助手。请基于我提供的结构化 JSON 上下文，输出中文日报和买卖计划。

硬性要求：
- 不要编造 JSON 里没有的数据。
- 先解释组合风险，再解释单只基金。
- 建议必须落到动作级别：继续定投、暂停、观察、小额加仓、降低买入额、减仓提醒。
- 每个买入建议都要给出金额区间或占月预算比例。
- 如果指标冲突，要明确写出冲突点，而不是给出武断结论。
- 这不是投资建议，不能承诺收益。

输出结构：

# 基金日报

## 组合结论
- 今日整体判断：
- 主要风险：
- 今日行动：

## 单只基金
对每只基金输出：
- 状态：
- 数据依据：
- 风险点：
- 今日建议：

# 买卖计划

## 今日计划
列出每只基金今日是否买入、买入金额、原因。

## 本周计划
给出本周定投和观察安排。

## 条件触发计划
给出下跌、上涨、仓位超限时的操作规则。

# 需要人工确认
列出因为数据不足或需要用户判断而不能自动决定的事项。


下面是今日 JSON 上下文和规则计划：

```json
{
  "context": {
    "report_date": "2026-05-24",
    "profile": {
      "risk_level": "medium",
      "monthly_budget": 1500,
      "cash_reserve": 0,
      "max_single_fund_ratio": 0.25,
      "max_sector_fund_ratio": 0.35,
      "style": "稳健定投，每月最多投入1500元，按约20个交易日折算每日预算；只在低位、回调、仓位不足时分批加仓，不追涨",
      "budget_confirmed": true
    },
    "portfolio": {
      "total_value": 1046.09,
      "fund_count": 15,
      "category_ratios": {
        "红利低波": 0.1139,
        "A股宽基": 0.1877,
        "海外科技": 0.1146,
        "债券": 0.4162,
        "红利": 0.0567,
        "海外宽基": 0.0197,
        "黄金": 0.0187,
        "港股科技": 0.0532,
        "主动权益": 0.0097,
        "农业": 0.0095
      },
      "risk_flags": [
        "债券 类基金合计仓位 41.6% 超过分类上限 35%"
      ]
    },
    "funds": [
      {
        "code": "008163",
        "name": "南方标普红利低波50ETF联接A",
        "type": "指数基金",
        "category": "红利低波",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-22",
        "latest_nav": 1.0465,
        "daily_return_pct": -0.39,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 2,
          "max_allowed_days": 3,
          "reason": "净值距今天 2 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 119.18,
          "current_value": 119.11,
          "profit_amount": -0.07,
          "profit_pct": -0.06,
          "monthly_plan": 0,
          "target_ratio": 0.1,
          "screenshot_profit_amount": -0.07,
          "screenshot_profit_pct": -0.06,
          "screenshot_yesterday_profit": -0.4,
          "portfolio_ratio": 0.1139
        },
        "metrics": {
          "returns_pct": {
            "1w": -1.27,
            "1m": -2.72,
            "3m": -2.7,
            "6m": -7.54,
            "1y": -10.33
          },
          "max_drawdown_1y_pct": -12.29,
          "max_drawdown_all_pct": -12.29,
          "position_60d_pct": 0.0,
          "position_250d_pct": 0.0,
          "position_window_pct": 0.0,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 11.03,
          "history_rows": 260
        }
      },
      {
        "code": "110020",
        "name": "易方达沪深300ETF联接A",
        "type": "宽基指数",
        "category": "A股宽基",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-22",
        "latest_nav": 1.951,
        "daily_return_pct": 1.21,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 2,
          "max_allowed_days": 3,
          "reason": "净值距今天 2 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 100.0,
          "current_value": 103.35,
          "profit_amount": 3.35,
          "profit_pct": 3.35,
          "monthly_plan": 0,
          "target_ratio": 0.12,
          "screenshot_profit_amount": 3.35,
          "screenshot_profit_pct": 3.35,
          "screenshot_yesterday_profit": 1.05,
          "portfolio_ratio": 0.0988
        },
        "metrics": {
          "returns_pct": {
            "1w": -0.26,
            "1m": 1.78,
            "3m": 4.08,
            "6m": 6.05,
            "1y": 26.58
          },
          "max_drawdown_1y_pct": -7.24,
          "max_drawdown_all_pct": -7.24,
          "position_60d_pct": 74.54,
          "position_250d_pct": 88.1,
          "position_window_pct": 88.1,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 16.41,
          "history_rows": 260
        }
      },
      {
        "code": "022459",
        "name": "易方达中证A500ETF联接A",
        "type": "宽基指数",
        "category": "A股宽基",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.3367,
        "daily_return_pct": 0.16,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 90.0,
          "current_value": 93.02,
          "profit_amount": 3.02,
          "profit_pct": 3.36,
          "monthly_plan": 0,
          "target_ratio": 0.12,
          "screenshot_profit_amount": 3.02,
          "screenshot_profit_pct": 3.36,
          "screenshot_yesterday_profit": 1.02,
          "portfolio_ratio": 0.0889
        },
        "metrics": {
          "returns_pct": {
            "1w": -2.76,
            "1m": 3.82,
            "3m": 4.15,
            "6m": 10.75,
            "1y": 36.23
          },
          "max_drawdown_1y_pct": -8.24,
          "max_drawdown_all_pct": -8.24,
          "position_60d_pct": 78.96,
          "position_250d_pct": 90.54,
          "position_window_pct": 90.54,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 18.59,
          "history_rows": 260
        }
      },
      {
        "code": "006555",
        "name": "浦银安盛全球智能科技股票(QDII)A",
        "type": "QDII股票",
        "category": "海外科技",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-19",
        "latest_nav": 3.4585,
        "daily_return_pct": -0.66,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 5,
          "max_allowed_days": 5,
          "reason": "净值距今天 5 天，QDII/海外基金允许 5 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 10.0,
          "current_value": 10.48,
          "profit_amount": 0.48,
          "profit_pct": 4.83,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 0.48,
          "screenshot_profit_pct": 4.83,
          "screenshot_yesterday_profit": -0.3,
          "portfolio_ratio": 0.01
        },
        "metrics": {
          "returns_pct": {
            "1w": -4.83,
            "1m": 10.94,
            "3m": 28.56,
            "6m": 40.52,
            "1y": 84.68
          },
          "max_drawdown_1y_pct": -13.22,
          "max_drawdown_all_pct": -13.22,
          "position_60d_pct": 77.98,
          "position_250d_pct": 84.76,
          "position_window_pct": 84.76,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 42.31,
          "history_rows": 260
        }
      },
      {
        "code": "270042",
        "name": "广发纳斯达克100ETF联接人民币(QDII)A",
        "type": "QDII指数",
        "category": "海外科技",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-19",
        "latest_nav": 8.1029,
        "daily_return_pct": -0.7,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 5,
          "max_allowed_days": 5,
          "reason": "净值距今天 5 天，QDII/海外基金允许 5 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 60.0,
          "current_value": 65.93,
          "profit_amount": 5.93,
          "profit_pct": 9.89,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 5.93,
          "screenshot_profit_pct": 9.89,
          "screenshot_yesterday_profit": -0.61,
          "portfolio_ratio": 0.063
        },
        "metrics": {
          "returns_pct": {
            "1w": -0.9,
            "1m": 8.95,
            "3m": 12.7,
            "6m": 11.12,
            "1y": 36.0
          },
          "max_drawdown_1y_pct": -14.26,
          "max_drawdown_all_pct": -14.26,
          "position_60d_pct": 87.81,
          "position_250d_pct": 90.59,
          "position_window_pct": 90.59,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 20.83,
          "history_rows": 260
        }
      },
      {
        "code": "000834",
        "name": "大成纳斯达克100ETF联接(QDII)A",
        "type": "QDII指数",
        "category": "海外科技",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-19",
        "latest_nav": 6.2581,
        "daily_return_pct": -0.7,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 5,
          "max_allowed_days": 5,
          "reason": "净值距今天 5 天，QDII/海外基金允许 5 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 40.0,
          "current_value": 43.43,
          "profit_amount": 3.43,
          "profit_pct": 8.56,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 3.43,
          "screenshot_profit_pct": 8.56,
          "screenshot_yesterday_profit": -0.39,
          "portfolio_ratio": 0.0415
        },
        "metrics": {
          "returns_pct": {
            "1w": -1.0,
            "1m": 8.43,
            "3m": 12.17,
            "6m": 10.66,
            "1y": 35.84
          },
          "max_drawdown_1y_pct": -14.01,
          "max_drawdown_all_pct": -14.01,
          "position_60d_pct": 87.31,
          "position_250d_pct": 90.36,
          "position_window_pct": 90.36,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 20.63,
          "history_rows": 260
        }
      },
      {
        "code": "004400",
        "name": "金信民兴债券A",
        "type": "债券基金",
        "category": "债券",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.0629,
        "daily_return_pct": 0.02,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 210.0,
          "current_value": 210.16,
          "profit_amount": 0.16,
          "profit_pct": 0.08,
          "monthly_plan": 0,
          "target_ratio": 0.16,
          "screenshot_profit_amount": 0.16,
          "screenshot_profit_pct": 0.08,
          "screenshot_yesterday_profit": 0.02,
          "portfolio_ratio": 0.2009
        },
        "metrics": {
          "returns_pct": {
            "1w": 0.1,
            "1m": 0.28,
            "3m": -0.08,
            "6m": -1.41,
            "1y": 0.74
          },
          "max_drawdown_1y_pct": -2.39,
          "max_drawdown_all_pct": -2.39,
          "position_60d_pct": 56.72,
          "position_250d_pct": 37.98,
          "position_window_pct": 37.98,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 2.63,
          "history_rows": 260
        }
      },
      {
        "code": "009051",
        "name": "易方达中证红利ETF联接发起式A",
        "type": "指数基金",
        "category": "红利",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.2743,
        "daily_return_pct": -0.31,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 60.0,
          "current_value": 59.36,
          "profit_amount": -0.64,
          "profit_pct": -1.07,
          "monthly_plan": 0,
          "target_ratio": 0.1,
          "screenshot_profit_amount": -0.64,
          "screenshot_profit_pct": -1.07,
          "screenshot_yesterday_profit": -0.23,
          "portfolio_ratio": 0.0567
        },
        "metrics": {
          "returns_pct": {
            "1w": -1.67,
            "1m": -0.46,
            "3m": -1.64,
            "6m": -0.69,
            "1y": 5.05
          },
          "max_drawdown_1y_pct": -7.22,
          "max_drawdown_all_pct": -7.22,
          "position_60d_pct": 12.37,
          "position_250d_pct": 46.78,
          "position_window_pct": 46.78,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 12.48,
          "history_rows": 260
        }
      },
      {
        "code": "050025",
        "name": "博时标普500ETF联接(QDII)A",
        "type": "QDII指数",
        "category": "海外宽基",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-19",
        "latest_nav": 5.4119,
        "daily_return_pct": -0.71,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 5,
          "max_allowed_days": 5,
          "reason": "净值距今天 5 天，QDII/海外基金允许 5 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 20.0,
          "current_value": 20.66,
          "profit_amount": 0.66,
          "profit_pct": 3.28,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 0.66,
          "screenshot_profit_pct": 3.28,
          "screenshot_yesterday_profit": -0.04,
          "portfolio_ratio": 0.0197
        },
        "metrics": {
          "returns_pct": {
            "1w": -0.66,
            "1m": 3.98,
            "3m": 4.29,
            "6m": 5.6,
            "1y": 23.29
          },
          "max_drawdown_1y_pct": -9.57,
          "max_drawdown_all_pct": -9.57,
          "position_60d_pct": 86.24,
          "position_250d_pct": 90.44,
          "position_window_pct": 90.44,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 14.69,
          "history_rows": 260
        }
      },
      {
        "code": "007194",
        "name": "长城短债A",
        "type": "债券基金",
        "category": "债券",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.2453,
        "daily_return_pct": 0.02,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 215.0,
          "current_value": 215.21,
          "profit_amount": 0.21,
          "profit_pct": 0.1,
          "monthly_plan": 0,
          "target_ratio": 0.16,
          "screenshot_profit_amount": 0.21,
          "screenshot_profit_pct": 0.1,
          "screenshot_yesterday_profit": 0.03,
          "portfolio_ratio": 0.2057
        },
        "metrics": {
          "returns_pct": {
            "1w": 0.09,
            "1m": 0.27,
            "3m": 0.93,
            "6m": 1.41,
            "1y": 2.81
          },
          "max_drawdown_1y_pct": -0.33,
          "max_drawdown_all_pct": -0.33,
          "position_60d_pct": 100.0,
          "position_250d_pct": 100.0,
          "position_window_pct": 100.0,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 0.19,
          "history_rows": 260
        }
      },
      {
        "code": "000218",
        "name": "国泰黄金ETF联接A",
        "type": "商品指数",
        "category": "黄金",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 3.5621,
        "daily_return_pct": -1.32,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 20.0,
          "current_value": 19.53,
          "profit_amount": -0.47,
          "profit_pct": -2.34,
          "monthly_plan": 0,
          "target_ratio": 0.06,
          "screenshot_profit_amount": -0.47,
          "screenshot_profit_pct": -2.34,
          "screenshot_yesterday_profit": 0.02,
          "portfolio_ratio": 0.0187
        },
        "metrics": {
          "returns_pct": {
            "1w": -4.38,
            "1m": -6.52,
            "3m": -12.41,
            "6m": 5.82,
            "1y": 24.57
          },
          "max_drawdown_1y_pct": -25.02,
          "max_drawdown_all_pct": -25.02,
          "position_60d_pct": 21.33,
          "position_250d_pct": 49.46,
          "position_window_pct": 49.46,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 35.32,
          "history_rows": 260
        }
      },
      {
        "code": "013308",
        "name": "易方达恒生科技ETF联接(QDII)A",
        "type": "QDII指数",
        "category": "港股科技",
        "notes": "来自支付宝持仓截图，截图中收益金额被浮层部分遮挡，按收益率约 1.26% 估算为 +0.70 元",
        "latest_date": "2026-05-20",
        "latest_nav": 1.1647,
        "daily_return_pct": 0.34,
        "estimate": null,
        "data_status": {
          "is_stale": false,
          "days_old": 4,
          "max_allowed_days": 5,
          "reason": "净值距今天 4 天，QDII/海外基金允许 5 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 55.0,
          "current_value": 55.7,
          "profit_amount": 0.7,
          "profit_pct": 1.26,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 0.7,
          "screenshot_profit_pct": 1.26,
          "screenshot_yesterday_profit": 0.24,
          "portfolio_ratio": 0.0532
        },
        "metrics": {
          "returns_pct": {
            "1w": -4.16,
            "1m": -3.5,
            "3m": -12.1,
            "6m": -17.85,
            "1y": -11.97
          },
          "max_drawdown_1y_pct": -29.32,
          "max_drawdown_all_pct": -29.32,
          "position_60d_pct": 22.57,
          "position_250d_pct": 8.82,
          "position_window_pct": 8.82,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 27.33,
          "history_rows": 260
        }
      },
      {
        "code": "010385",
        "name": "华安汇嘉精选混合A",
        "type": "主动混合",
        "category": "主动权益",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.5273,
        "daily_return_pct": 1.56,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 10.0,
          "current_value": 10.18,
          "profit_amount": 0.18,
          "profit_pct": 1.78,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": 0.18,
          "screenshot_profit_pct": 1.78,
          "screenshot_yesterday_profit": 0.09,
          "portfolio_ratio": 0.0097
        },
        "metrics": {
          "returns_pct": {
            "1w": -2.09,
            "1m": 2.63,
            "3m": -0.24,
            "6m": 16.89,
            "1y": 49.68
          },
          "max_drawdown_1y_pct": -11.83,
          "max_drawdown_all_pct": -11.83,
          "position_60d_pct": 48.42,
          "position_250d_pct": 83.98,
          "position_window_pct": 83.98,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 20.03,
          "history_rows": 260
        }
      },
      {
        "code": "014064",
        "name": "银华农业产业股票发起式C",
        "type": "主动股票",
        "category": "农业",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.1942,
        "daily_return_pct": -1.19,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 10.0,
          "current_value": 9.98,
          "profit_amount": -0.02,
          "profit_pct": -0.24,
          "monthly_plan": 0,
          "target_ratio": 0.05,
          "screenshot_profit_amount": -0.02,
          "screenshot_profit_pct": -0.24,
          "screenshot_yesterday_profit": -0.15,
          "portfolio_ratio": 0.0095
        },
        "metrics": {
          "returns_pct": {
            "1w": -2.86,
            "1m": -8.14,
            "3m": -6.22,
            "6m": -10.27,
            "1y": -6.38
          },
          "max_drawdown_1y_pct": -19.48,
          "max_drawdown_all_pct": -19.48,
          "position_60d_pct": 0.0,
          "position_250d_pct": 0.0,
          "position_window_pct": 0.0,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 28.0,
          "history_rows": 260
        }
      },
      {
        "code": "000123",
        "name": "汇添富实业债债券C",
        "type": "债券基金",
        "category": "债券",
        "notes": "来自支付宝持仓截图，截图时间约 2026-05-14 21:59",
        "latest_date": "2026-05-20",
        "latest_nav": 1.5205,
        "daily_return_pct": 0.02,
        "estimate": null,
        "data_status": {
          "is_stale": true,
          "days_old": 4,
          "max_allowed_days": 3,
          "reason": "净值距今天 4 天，境内基金允许 3 天内"
        },
        "holding": {
          "shares": null,
          "cost_nav": null,
          "cost_amount": 10.0,
          "current_value": 9.99,
          "profit_amount": -0.01,
          "profit_pct": -0.06,
          "monthly_plan": 0,
          "target_ratio": 0.08,
          "screenshot_profit_amount": -0.01,
          "screenshot_profit_pct": -0.06,
          "screenshot_yesterday_profit": 0.03,
          "portfolio_ratio": 0.0095
        },
        "metrics": {
          "returns_pct": {
            "1w": -0.36,
            "1m": 0.38,
            "3m": -0.63,
            "6m": 0.93,
            "1y": 9.08
          },
          "max_drawdown_1y_pct": -2.16,
          "max_drawdown_all_pct": -2.16,
          "position_60d_pct": 53.14,
          "position_250d_pct": 88.18,
          "position_window_pct": 88.18,
          "position_window_days": 250,
          "annualized_volatility_60d_pct": 3.08,
          "history_rows": 260
        }
      }
    ]
  },
  "plan": {
    "daily_budget": 75.0,
    "planned_amount": 30,
    "cash_left": 45.0,
    "algorithm": {
      "name": "目标仓位 + 回调增强 + 风险过滤",
      "budget_rule": "月预算按20个交易日折算为日预算，不强行用完",
      "amount_rule": "强信号30-40元，中信号20元，弱信号10元；单日最多买4只",
      "hard_filters": [
        "数据过期",
        "仓位明显超目标",
        "分类仓位超上限",
        "目标仓位为0"
      ]
    },
    "decisions": [
      {
        "code": "013308",
        "name": "易方达恒生科技ETF联接(QDII)A",
        "tier": "可以买",
        "score": 4.75,
        "reasons": [
          "近250条净值处于低位",
          "仓位低于目标",
          "近一周有回撤"
        ],
        "risks": [
          "QDII/海外基金净值有延迟，需要降低对今日涨跌的权重"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 0.34,
        "blocked": false,
        "action": "可以买",
        "amount": 30
      },
      {
        "code": "008163",
        "name": "南方标普红利低波50ETF联接A",
        "tier": "可观察",
        "score": 3.0,
        "reasons": [
          "近250条净值处于低位"
        ],
        "risks": [
          "未触发明显单项风险"
        ],
        "latest_date": "2026-05-22",
        "daily_return_pct": -0.39,
        "blocked": false,
        "action": "可观察",
        "amount": 0
      },
      {
        "code": "006555",
        "name": "浦银安盛全球智能科技股票(QDII)A",
        "tier": "可观察",
        "score": 0.5,
        "reasons": [
          "仓位明显低于目标",
          "今日小幅回调",
          "近一周有回撤"
        ],
        "risks": [
          "近250条净值位置中性偏高",
          "近一月涨幅较大",
          "QDII/海外基金净值有延迟，需要降低对今日涨跌的权重"
        ],
        "latest_date": "2026-05-19",
        "daily_return_pct": -0.66,
        "blocked": false,
        "action": "可观察",
        "amount": 0
      },
      {
        "code": "050025",
        "name": "博时标普500ETF联接(QDII)A",
        "tier": "可观察",
        "score": -1.25,
        "reasons": [
          "仓位明显低于目标",
          "今日小幅回调"
        ],
        "risks": [
          "近250条净值位置偏高，追涨风险较大",
          "QDII/海外基金净值有延迟，需要降低对今日涨跌的权重"
        ],
        "latest_date": "2026-05-19",
        "daily_return_pct": -0.71,
        "blocked": false,
        "action": "可观察",
        "amount": 0
      },
      {
        "code": "270042",
        "name": "广发纳斯达克100ETF联接人民币(QDII)A",
        "tier": "禁止买",
        "score": -3.25,
        "reasons": [
          "仓位低于目标",
          "今日小幅回调"
        ],
        "risks": [
          "近250条净值位置偏高，追涨风险较大",
          "持仓已有较高浮盈",
          "QDII/海外基金净值有延迟，需要降低对今日涨跌的权重"
        ],
        "latest_date": "2026-05-19",
        "daily_return_pct": -0.7,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "000834",
        "name": "大成纳斯达克100ETF联接(QDII)A",
        "tier": "禁止买",
        "score": -3.25,
        "reasons": [
          "仓位低于目标",
          "今日小幅回调"
        ],
        "risks": [
          "近250条净值位置偏高，追涨风险较大",
          "持仓已有较高浮盈",
          "QDII/海外基金净值有延迟，需要降低对今日涨跌的权重"
        ],
        "latest_date": "2026-05-19",
        "daily_return_pct": -0.7,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "110020",
        "name": "易方达沪深300ETF联接A",
        "tier": "禁止买",
        "score": -4.0,
        "reasons": [
          "仓位低于目标"
        ],
        "risks": [
          "近250条净值位置偏高，追涨风险较大",
          "今日已有上涨"
        ],
        "latest_date": "2026-05-22",
        "daily_return_pct": 1.21,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "022459",
        "name": "易方达中证A500ETF联接A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 0.16,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "004400",
        "name": "金信民兴债券A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内",
          "当前仓位明显超过目标仓位",
          "债券 分类仓位已超过上限"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 0.02,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "009051",
        "name": "易方达中证红利ETF联接发起式A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": -0.31,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "007194",
        "name": "长城短债A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内",
          "当前仓位明显超过目标仓位",
          "债券 分类仓位已超过上限"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 0.02,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "000218",
        "name": "国泰黄金ETF联接A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": -1.32,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "010385",
        "name": "华安汇嘉精选混合A",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 1.56,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "014064",
        "name": "银华农业产业股票发起式C",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": -1.19,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      },
      {
        "code": "000123",
        "name": "汇添富实业债债券C",
        "tier": "禁止买",
        "score": -99,
        "reasons": [
          "触发硬性风控"
        ],
        "risks": [
          "净值距今天 4 天，境内基金允许 3 天内",
          "债券 分类仓位已超过上限"
        ],
        "latest_date": "2026-05-20",
        "daily_return_pct": 0.02,
        "blocked": true,
        "action": "禁止买",
        "amount": 0
      }
    ]
  }
}
```
