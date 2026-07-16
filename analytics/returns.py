from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


TRADING_DAYS = 252


@dataclass(slots=True)
class ReturnSummary:
    cumulative_return: float
    annual_return: float
    cagr: float
    volatility: float
    best_day: float
    worst_day: float


class ReturnsEngine:
    """
    Computes portfolio return statistics.

    Input:
        Daily portfolio values OR daily prices.

    Output:
        Returns, CAGR, annualized return, volatility, etc.
    """

    def __init__(
        self,
        prices: pd.Series,
    ):

        if len(prices) < 2:
            raise ValueError(
                "At least two prices are required."
            )

        self.prices = prices.sort_index()

    # --------------------------------------------------

    @property
    def daily_returns(self) -> pd.Series:

        return (
            self.prices
            .pct_change()
            .dropna()
        )

    # --------------------------------------------------

    @property
    def cumulative_return(self) -> float:

        return (
            self.prices.iloc[-1]
            / self.prices.iloc[0]
            - 1
        )

    # --------------------------------------------------

    @property
    def annual_return(self) -> float:

        r = self.daily_returns

        return float(
            r.mean() * TRADING_DAYS
        )

    # --------------------------------------------------

    @property
    def volatility(self) -> float:

        r = self.daily_returns

        return float(
            r.std() * np.sqrt(TRADING_DAYS)
        )

    # --------------------------------------------------

    @property
    def cagr(self) -> float:

        years = (
            (
                self.prices.index[-1]
                - self.prices.index[0]
            ).days
            / 365.25
        )

        if years <= 0:
            return 0

        return float(
            (
                self.prices.iloc[-1]
                / self.prices.iloc[0]
            )
            ** (1 / years)
            - 1
        )

    # --------------------------------------------------

    @property
    def best_day(self) -> float:

        return float(
            self.daily_returns.max()
        )

    # --------------------------------------------------

    @property
    def worst_day(self) -> float:

        return float(
            self.daily_returns.min()
        )

    # --------------------------------------------------

    @property
    def cumulative_curve(
        self,
    ) -> pd.Series:

        return (
            1 + self.daily_returns
        ).cumprod()

    # --------------------------------------------------

    @property
    def drawdown_curve(
        self,
    ) -> pd.Series:

        curve = self.cumulative_curve

        peak = curve.cummax()

        return (
            curve - peak
        ) / peak

    # --------------------------------------------------

    @property
    def max_drawdown(self) -> float:

        return float(
            self.drawdown_curve.min()
        )

    # --------------------------------------------------

    @property
    def monthly_returns(
        self,
    ) -> pd.Series:

        monthly = (
            self.prices
            .resample("ME")
            .last()
        )

        return (
            monthly
            .pct_change()
            .dropna()
        )

    # --------------------------------------------------

    @property
    def yearly_returns(
        self,
    ) -> pd.Series:

        yearly = (
            self.prices
            .resample("YE")
            .last()
        )

        return (
            yearly
            .pct_change()
            .dropna()
        )

    # --------------------------------------------------

    def rolling_return(
        self,
        window: int = 252,
    ) -> pd.Series:

        return (
            self.prices
            .pct_change(window)
        )

    # --------------------------------------------------

    def rolling_volatility(
        self,
        window: int = 30,
    ) -> pd.Series:

        return (
            self.daily_returns
            .rolling(window)
            .std()
            * np.sqrt(TRADING_DAYS)
        )

    # --------------------------------------------------

    def rolling_cagr(
        self,
        window: int = 252,
    ) -> pd.Series:

        result = []

        index = []

        prices = self.prices

        for i in range(
            window,
            len(prices),
        ):

            start = prices.iloc[
                i - window
            ]

            end = prices.iloc[i]

            years = window / TRADING_DAYS

            cagr = (
                end / start
            ) ** (1 / years) - 1

            result.append(cagr)

            index.append(
                prices.index[i]
            )

        return pd.Series(
            result,
            index=index,
        )

    # --------------------------------------------------

    def summary(
        self,
    ) -> ReturnSummary:

        return ReturnSummary(
            cumulative_return=self.cumulative_return,
            annual_return=self.annual_return,
            cagr=self.cagr,
            volatility=self.volatility,
            best_day=self.best_day,
            worst_day=self.worst_day,
        )

    # --------------------------------------------------

    @staticmethod
    def portfolio_value(
        prices: pd.DataFrame,
        weights: Iterable[float],
        initial: float = 100000,
    ) -> pd.Series:
        """
        Create a portfolio value series from
        historical prices and asset weights.

        weights should sum to 1.
        """

        weights = np.asarray(weights)

        if not np.isclose(
            weights.sum(),
            1.0,
        ):
            raise ValueError(
                "Weights must sum to 1."
            )

        returns = (
            prices
            .pct_change()
            .dropna()
        )

        portfolio_returns = (
            returns * weights
        ).sum(axis=1)

        return (
            initial
            * (1 + portfolio_returns)
            .cumprod()
        )