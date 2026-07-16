from __future__ import annotations

from datetime import datetime

import pandas as pd
import yfinance as yf

from app_config.benchmarks import BENCHMARKS


class BenchmarkService:
    """
    Downloads benchmark history from Yahoo Finance.
    """

    def history(
        self,
        benchmark: str,
        start: datetime,
        end: datetime,
    ) -> pd.Series:

        if benchmark not in BENCHMARKS:

            raise ValueError(
                f"Unsupported benchmark: {benchmark}"
            )

        ticker = BENCHMARKS[
            benchmark
        ].ticker

        df = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df.empty:

            raise RuntimeError(
                f"No history available for {benchmark}"
            )

        if "Close" not in df.columns:

            raise RuntimeError(
                f"Close price missing for {benchmark}"
            )

        close = df["Close"]

        # yfinance may return a DataFrame for a single ticker
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        
        close = df["Close"].squeeze()
        prices = close.copy().dropna()

        prices.name = benchmark

        prices.index = pd.to_datetime(prices.index)

        if prices.index.tz is not None:
            prices.index = prices.index.tz_localize(None)

        return prices

    def available(self):

        return list(
            BENCHMARKS.keys()
        )

    def default(self):

        return "NIFTY 50"