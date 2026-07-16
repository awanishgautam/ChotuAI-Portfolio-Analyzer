"""
Simple AI Portfolio Agent

Python 3.12
"""

from __future__ import annotations

import json

from openai import OpenAI

from analytics.risk.risk_engine import RiskEngine
from portfolio.models import EquityHolding, MutualFundHolding

class PortfolioAgent:

    def __init__(
        self,
        api_key: str,
    ):

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )
        self.client = OpenAI(
            api_key=api_key,
        )

    # --------------------------------------------------

    def ask(
        self,
        question,
        portfolio,
        portfolio_prices,
        benchmark_prices,
        benchmark_name,
    ):

        engine = RiskEngine(
            portfolio_prices=portfolio_prices,
            benchmark_prices=benchmark_prices,
        )

        analytics = engine.summary()

        prompt = self._build_prompt(
            portfolio,
            analytics,
            question,
            benchmark_name,
        )

        response = self.client.responses.create(
            model="gpt-4.1",
            input=prompt,
             tools=[
                {
                    "type": "web_search_preview",
                }
             ],
        )

        return response.output_text

    # --------------------------------------------------

    def _build_prompt(
        self,
        portfolio,
        analytics,
        question,
        benchmark_name,
    ) -> str:

        portfolio_summary = {
            "market_value": portfolio.market_value,
            "invested_value": portfolio.invested_value,
            "pnl": portfolio.pnl,
            "Benchmark": benchmark_name,
            "holdings": [
                (
                    {
                        "symbol": h.symbol,
                        "name": h.name,
                        "asset_type": h.asset_type.value,
                        "exchange": h.exchange.value,
                        "quantity": h.quantity,
                        "average_price": h.average_price,
                        "last_price": h.last_price,
                        "invested_value": h.invested_value,
                        "current_value": h.current_value,
                        "pnl": h.pnl,
                        "pnl_percent": h.pnl_percent,
                    }
                    if isinstance(h, EquityHolding)
                    else
                    {
                        "fund_name": h.fund_name,
                        "name": h.name,
                        "asset_type": h.asset_type.value,
                        "folio": h.folio,
                        "quantity": h.quantity,
                        "average_price": h.average_price,
                        "last_price": h.last_price,
                        "invested_value": h.invested_value,
                        "current_value": h.current_value,
                        "pnl": h.pnl,
                        "pnl_percent": h.pnl_percent,
                    }
                )
                for h in portfolio.holdings
            ]
        }

        analytics_json = analytics.model_dump()

        return f"""
You are an investment portfolio assistant.

You have access to a web search tool.

Use it whenever the user asks about:

- today's news
- latest market updates
- company news
- RBI decisions
- FED announcements
- earnings
- stock recommendations
- recent events

Do not answer from memory if recent information is required.

If information is missing, explain exactly what is missing instead of simply saying "I don't have enough data."

Keep answers concise and practical.

Portfolio Summary

{json.dumps(portfolio_summary, indent=2)}

Analytics

{json.dumps(analytics_json, indent=2)}

Question

{question}
"""