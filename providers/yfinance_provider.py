from __future__ import annotations

from datetime import datetime

import yfinance as yf

from .market_data_provider import MarketDataProvider
from .models import PriceBar, Quote


class YahooFinanceProvider(MarketDataProvider):

    def latest_price(
        self,
        symbol: str,
    ) -> float:

        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        return float(info["lastPrice"])

    def quote(
        self,
        symbol: str,
    ) -> Quote:

        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        price = float(info["lastPrice"])

        prev = float(info["previousClose"])

        change = price - prev

        pct = change / prev * 100

        return Quote(
            symbol=symbol,
            price=price,
            previous_close=prev,
            change=change,
            change_percent=pct,
        )

    def history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> list[PriceBar]:

        ticker = yf.Ticker(symbol)

        df = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=True,
        )

        bars: list[PriceBar] = []

        for ts, row in df.iterrows():

            bars.append(
                PriceBar(
                    timestamp=ts.to_pydatetime(),
                    open=float(row.Open),
                    high=float(row.High),
                    low=float(row.Low),
                    close=float(row.Close),
                    volume=int(row.Volume),
                )
            )

        return bars

    def multiple_history(
        self,
        symbols: list[str],
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, list[PriceBar]]:

        result = {}

        for symbol in symbols:
            result[symbol] = self.history(
                symbol,
                period,
                interval,
            )

        return result