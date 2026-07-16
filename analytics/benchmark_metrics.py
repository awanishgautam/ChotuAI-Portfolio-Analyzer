from __future__ import annotations

import numpy as np
import pandas as pd

from analytics.benchmark import (
    BenchmarkSummary,
    RollingStatistics,
)


class BenchmarkMetrics:
    """
    Computes benchmark-relative statistics.

    Inputs must be PRICE series.
    """

    def __init__(
        self,
        portfolio_prices: pd.Series,
        benchmark_prices: pd.Series,
        benchmark_name: str = "Benchmark",
        periods_per_year: int = 252,
        risk_free_rate: float = 0.0,
    ):
        
        if isinstance(portfolio_prices, pd.DataFrame):
            portfolio_prices = portfolio_prices.iloc[:, 0]

        if isinstance(benchmark_prices, pd.DataFrame):
            benchmark_prices = benchmark_prices.iloc[:, 0]
        self.periods = periods_per_year
        self.risk_free_rate = risk_free_rate
        self.benchmark_name = benchmark_name

        portfolio_prices = portfolio_prices.copy()
        benchmark_prices = benchmark_prices.copy()
        portfolio_prices.index = pd.to_datetime(portfolio_prices.index)
        benchmark_prices.index = pd.to_datetime(benchmark_prices.index)

        if portfolio_prices.index.tz is not None:
            portfolio_prices.index = portfolio_prices.index.tz_localize(None)

        if benchmark_prices.index.tz is not None:
            benchmark_prices.index = benchmark_prices.index.tz_localize(None)

        portfolio_prices = portfolio_prices.sort_index()
        benchmark_prices = benchmark_prices.sort_index()

        df = pd.concat(
            [
                portfolio_prices.rename("portfolio"),
                benchmark_prices.rename("benchmark"),
            ],
            axis=1,
        ).dropna()

        if len(df) < 2:
            raise ValueError(
                "Portfolio and benchmark have insufficient overlapping history."
            )

        self.portfolio_prices = df["portfolio"]
        self.benchmark_prices = df["benchmark"]

        self.portfolio_returns = (
            self.portfolio_prices.pct_change().dropna()
        )

        self.benchmark_returns = (
            self.benchmark_prices.pct_change().dropna()
        )

        returns = pd.concat(
            [
                self.portfolio_returns.rename("portfolio"),
                self.benchmark_returns.rename("benchmark"),
            ],
            axis=1,
            join="inner",
        ).dropna()

        self.portfolio_returns = returns["portfolio"]
        self.benchmark_returns = returns["benchmark"]
        
    ######################################################################
    # Basic statistics
    ######################################################################

    @staticmethod
    def _annual_return(
        prices: pd.Series,
        periods: int,
    ):

        years = (
            prices.index[-1] - prices.index[0]
        ).days / 365.25

        if years <= 0:
            return 0.0

        total_return = (
            prices.iloc[-1]
            / prices.iloc[0]
        )

        return total_return ** (1 / years) - 1

    @staticmethod
    def _total_return(
        prices: pd.Series,
    ) -> float:

        return prices.iloc[-1] / prices.iloc[0] - 1

    @staticmethod
    def _annual_volatility(
        returns: pd.Series,
        periods: int,
    ) -> float:

        return returns.std() * np.sqrt(periods)

    ######################################################################
    # Benchmark metrics
    ######################################################################

    def beta(self):

        cov = self.portfolio_returns.cov(
            self.benchmark_returns
        )

        var = self.benchmark_returns.var()

        if var == 0:
            return None

        return cov / var

    def alpha(self):

        beta = self.beta()

        if beta is None:
            return None

        rp = self._annual_return(
            self.portfolio_prices,
            self.periods,
        )

        rb = self._annual_return(
            self.benchmark_prices,
            self.periods,
        )

        return (
            rp
            - (
                self.risk_free_rate
                + beta * (rb - self.risk_free_rate)
            )
        )

    def correlation(self):

        return self.portfolio_returns.corr(
            self.benchmark_returns,
        )

    def tracking_error(self):

        diff = (
            self.portfolio_returns
            - self.benchmark_returns
        )

        return diff.std() * np.sqrt(
            self.periods,
        )

    def information_ratio(self):

        te = self.tracking_error()

        if te == 0:
            return None

        excess = (
            self._annual_return(
                self.portfolio_prices,
                self.periods,
            )
            -
            self._annual_return(
                self.benchmark_prices,
                self.periods,
            )
        )

        return excess / te

    ######################################################################
    # Rolling statistics
    ######################################################################

    def rolling_beta(
        self,
        window: int = 60,
    ):

        cov = (
            self.portfolio_returns
            .rolling(window)
            .cov(self.benchmark_returns)
        )

        var = (
            self.benchmark_returns
            .rolling(window)
            .var()
        )

        return cov / var

    def rolling_alpha(
        self,
        window: int = 60,
    ):

        beta = self.rolling_beta(window)

        rp = (
            1
            + self.portfolio_returns
        ).rolling(window).apply(
            np.prod,
            raw=True,
        ) ** (
            self.periods / window
        ) - 1

        rb = (
            1
            + self.benchmark_returns
        ).rolling(window).apply(
            np.prod,
            raw=True,
        ) ** (
            self.periods / window
        ) - 1

        return rp - (
            self.risk_free_rate
            + beta
            * (
                rb
                - self.risk_free_rate
            )
        )

    def rolling_correlation(
        self,
        window: int = 60,
    ):

        return (
            self.portfolio_returns
            .rolling(window)
            .corr(
                self.benchmark_returns,
            )
        )

    ######################################################################
    # Summary
    ######################################################################

    def summary(self):

        return BenchmarkSummary(

            benchmark_name=self.benchmark_name,

            portfolio_return=self._total_return(
                self.portfolio_prices,
            ),

            benchmark_return=self._total_return(
                self.benchmark_prices,
            ),

            portfolio_cagr=self._annual_return(
                self.portfolio_prices,
                self.periods,
            ),

            benchmark_cagr=self._annual_return(
                self.benchmark_prices,
                self.periods,
            ),

            alpha=self.alpha(),

            beta=self.beta(),

            correlation=self.correlation(),

            tracking_error=self.tracking_error(),

            information_ratio=self.information_ratio(),

            volatility_portfolio=self._annual_volatility(
                self.portfolio_returns,
                self.periods,
            ),

            volatility_benchmark=self._annual_volatility(
                self.benchmark_returns,
                self.periods,
            ),
        )

    def rolling_statistics(
        self,
        window: int = 60,
    ):

        return RollingStatistics(

            rolling_beta=self.rolling_beta(
                window,
            ),

            rolling_alpha=self.rolling_alpha(
                window,
            ),

            rolling_correlation=self.rolling_correlation(
                window,
            ),
        )