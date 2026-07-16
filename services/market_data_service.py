"""
market_data.py

Simple market data service using Yahoo Finance.

Python 3.12
"""

from __future__ import annotations

import yfinance as yf
import pandas as pd
from mftool import Mftool
from rapidfuzz import process, fuzz

from portfolio.models import MutualFundHolding

class MarketDataService:

    def __init__(self):

        self.mf = Mftool()
        self.scheme_lookup = self.mf.get_scheme_codes()

        # build name -> code
        self.scheme_lookup = {
            self.normalize_name(name): code
            for code, name in self.scheme_lookup.items()
            if code.isdigit()      # skip the header row
        }

    # ----------------------------------------------------
    # Helper function to extract amfi code of mutual fund
    # ----------------------------------------------------
    def normalize_name(
        self,
        name: str,
    ) -> str:

        name = name.lower()

        replacements = [
            (" - direct plan", ""),
            ("direct plan", ""),
            ("growth option", ""),
            ("growth", ""),
            ("plan", ""),
            ("fund of fund", "fof"),
            ("&", "and"),
            ("(", ""),
            (")", ""),
            (".", ""),
            ("  ", " "),
        ]

        for old, new in replacements:
            name = name.replace(old, new)

        return " ".join(name.split())

    def get_amfi_code(self, fund_name: str):

        fund_name = self.normalize_name(fund_name)

        names = list(self.scheme_lookup.keys())

        match = process.extractOne(
            fund_name,
            names,
            scorer=fuzz.token_sort_ratio,
        )

        if match is None:
            raise ValueError(f"No AMFI match for {fund_name}")

        best_name, score, _ = match

        if score < 80:
            raise ValueError(
                f"Poor AMFI match for {fund_name} ({score})"
            )

        return self.scheme_lookup[best_name]
    
    # ----------------------------------------------------
    # Single Stock Price
    # ----------------------------------------------------

    def current_price(self, symbol: str) -> float:
        """
        Returns latest market price.

        Example:
            INFY
            TCS
            RELIANCE
        """

        ticker = yf.Ticker(f"{symbol}.NS")

        info = ticker.fast_info

        if "lastPrice" in info:
            return float(info["lastPrice"])

        if "last_price" in info:
            return float(info["last_price"])

        history = ticker.history(period="1d")

        if history.empty:
            raise RuntimeError(
                f"Unable to fetch price for {symbol}"
            )

        return float(history["Close"].iloc[-1])

    # ----------------------------------------------------
    # Historical Prices
    # ----------------------------------------------------

    def history(
        self,
        symbol: str,
        period: str = "5y",
    ) -> pd.DataFrame:

        ticker = yf.Ticker(f"{symbol}.NS")

        df = ticker.history(period=period)

        if df.empty:
            raise RuntimeError(
                f"No data available for {symbol}"
            )
        df.index = df.index.tz_localize(None)
        return df

    def mutual_fund_history(
        self,
        holding: MutualFundHolding,
        period: str = "5y",
    ) -> pd.DataFrame:
        """
        Returns historical NAV in the same schema as
        yfinance.history().

        Output columns:

            Open
            High
            Low
            Close
            Volume

        Index:
            DatetimeIndex
        """

        amfi_code = holding.amfi_code

        if not amfi_code:

            amfi_code = self.get_amfi_code(
                holding.fund_name,
            )

        history = self.mf.get_scheme_historical_nav(
            amfi_code
        )

        if isinstance(history, dict):

            # find the first list in the dict
            for value in history.values():

                if isinstance(value, list):

                    history = value
                    break

        if not isinstance(history, list):
            raise RuntimeError(
                f"Unexpected AMFI response:\n{history}"
            )

        df = pd.DataFrame(history)

        if df.empty:

            raise RuntimeError(
                f"No NAV history available for "
                f"{holding.display_name}"
            )

        #
        # mftool returns:
        #
        # date
        # nav
        #

        df.rename(
            columns={
                "date": "Date",
                "nav": "Close",
            },
            inplace=True,
        )

        df["Date"] = pd.to_datetime(
            df["Date"],
            dayfirst=True,
        )

        df["Close"] = (
            df["Close"]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )

        df.sort_values(
            "Date",
            inplace=True,
        )

        df.set_index(
            "Date",
            inplace=True,
        )

        #
        # Match yfinance schema
        #

        df["Open"] = df["Close"]
        df["High"] = df["Close"]
        df["Low"] = df["Close"]
        df["Volume"] = 0

        #
        # Apply requested period
        #

        if period != "max":

            years = int(
                period.replace(
                    "y",
                    "",
                )
            )

            cutoff = (
                pd.Timestamp.today()
                - pd.DateOffset(years=years)
            )

            df = df.loc[
                df.index >= cutoff
            ]

        return df[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        ]
    
    # ----------------------------------------------------
    # Multiple Prices
    # ----------------------------------------------------

    def current_prices(
        self,
        symbols: list[str],
    ) -> dict[str, float]:

        prices = {}

        for symbol in symbols:

            try:

                prices[symbol] = self.current_price(
                    symbol
                )

            except Exception:

                prices[symbol] = 0.0

        return prices

    # ----------------------------------------------------
    # Benchmark
    # ----------------------------------------------------

    def nifty50(
        self,
        period: str = "5y",
    ) -> pd.DataFrame:

        return yf.download(
            "^NSEI",
            period=period,
            progress=False,
            auto_adjust=True,
        )

    # ----------------------------------------------------
    # Portfolio History
    # ----------------------------------------------------

    def portfolio_prices(
        self,
        portfolio,
        period: str = "5y",
    ) -> pd.DataFrame:
        """
        Downloads price history for all holdings.

        Returns

            Date     INFY     TCS     HDFCBANK

        """

        data = {}

        for holding in portfolio:

            symbol = holding.symbol

            try:

                df = self.history(
                    symbol,
                    period,
                )

                data[symbol] = df["Close"]

            except Exception:

                continue

        return pd.DataFrame(data)

    # ----------------------------------------------------
    # Benchmark Close Series
    # ----------------------------------------------------

    def benchmark_series(
        self,
        period: str = "5y",
    ) -> pd.Series:

        df = self.nifty50(period)

        return df["Close"]