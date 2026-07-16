"""
Portfolio Risk Engine

Facade over all analytics modules.

This class is the only class that Streamlit,
FastAPI, CLI or AI agents should use.

Everything else remains internal.

Python 3.12+
"""

from __future__ import annotations

from functools import cached_property

import pandas as pd

from .constants import (
    DEFAULT_CONFIG,
    RiskConfig,
)
from .models import (
    AnalyticsResult,
    PortfolioHealth,
    RiskMetrics,
    RollingMetrics,
)


class RiskEngine:
    """
    High-level portfolio analytics engine.

    Parameters
    ----------
    portfolio_prices

        Daily portfolio value history.

    benchmark_prices

        Daily benchmark value history.

    Example
    -------

    engine = RiskEngine(
        portfolio_prices,
        benchmark_prices,
    )

    metrics = engine.summary()
    """

    # -----------------------------------------------------
    # Constructor
    # -----------------------------------------------------

    def __init__(
        self,
        portfolio_prices: pd.Series,
        benchmark_prices: pd.Series | None = None,
        *,
        benchmark_name: str = "Benchmark",
        config: RiskConfig | None = None,
    ):

        self.config = config or DEFAULT_CONFIG

        self.config.validate()

        self.benchmark_name = benchmark_name

        self.portfolio_prices = self._prepare_prices(
            portfolio_prices,
            "portfolio",
        )

        if benchmark_prices is not None:

            self.benchmark_prices = self._prepare_prices(
                benchmark_prices,
                "benchmark",
            )

            (
                self.portfolio_prices,
                self.benchmark_prices,
            ) = self._align(
                self.portfolio_prices,
                self.benchmark_prices,
            )

        else:

            self.benchmark_prices = None

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    def _prepare_prices(
        self,
        prices: pd.Series | pd.DataFrame,
        name: str,
    ) -> pd.Series:

        import pandas as pd

        # Convert DataFrame to Series
        if isinstance(prices, pd.DataFrame):

            if "Close" in prices.columns:
                prices = prices["Close"]
            else:
                prices = prices.squeeze()

        prices = prices.copy()

        # Ensure datetime index
        prices.index = pd.to_datetime(prices.index)

        # Remove timezone if present
        if getattr(prices.index, "tz", None) is not None:
            prices.index = prices.index.tz_localize(None)

        prices = prices.sort_index()

        prices.name = name

        return prices

    def _align(
        self,
        portfolio: pd.Series,
        benchmark: pd.Series,
    ):
        import pandas as pd

        if isinstance(portfolio, pd.DataFrame):
            portfolio = portfolio.squeeze()

        if isinstance(benchmark, pd.DataFrame):
            if "Close" in benchmark.columns:
                benchmark = benchmark["Close"]
            else:
                benchmark = benchmark.squeeze()

        portfolio = portfolio.rename("portfolio")
        benchmark = benchmark.rename("benchmark")

        portfolio.index = pd.to_datetime(portfolio.index)
        benchmark.index = pd.to_datetime(benchmark.index)

        if getattr(portfolio.index, "tz", None) is not None:
            portfolio.index = portfolio.index.tz_localize(None)

        if getattr(benchmark.index, "tz", None) is not None:
            benchmark.index = benchmark.index.tz_localize(None)

        df = pd.concat([portfolio, benchmark], axis=1).dropna()

        return (
            df["portfolio"],
            df["benchmark"],
        )

    # -----------------------------------------------------
    # Cached Prices
    # -----------------------------------------------------

    @cached_property
    def portfolio_returns(
        self,
    ) -> pd.Series:

        return (
            self.portfolio_prices
            .pct_change()
            .dropna()
        )

    @cached_property
    def benchmark_returns(
        self,
    ) -> pd.Series | None:

        if self.benchmark_prices is None:
            return None

        return (
            self.benchmark_prices
            .pct_change()
            .dropna()
        )

    # -----------------------------------------------------
    # Convenience
    # -----------------------------------------------------

    @property
    def observations(
        self,
    ) -> int:

        return len(
            self.portfolio_returns
        )

    @property
    def has_benchmark(
        self,
    ) -> bool:

        return (
            self.benchmark_prices
            is not None
        )

    @property
    def risk_free_rate(
        self,
    ) -> float:

        return self.config.risk_free_rate

    # -----------------------------------------------------
    # Internal helper
    # -----------------------------------------------------

    def _empty_metrics(
        self,
    ) -> RiskMetrics:

        return RiskMetrics(
            benchmark_name=self.benchmark_name,
            observations=self.observations,
            risk_free_rate=self.risk_free_rate,
        )

    def _empty_health(
        self,
    ) -> PortfolioHealth:

        return PortfolioHealth()

    def _empty_rolling(
        self,
    ) -> RollingMetrics:

        return RollingMetrics()

    # -----------------------------------------------------
    # Placeholder methods
    # (implemented in Part 2)
    # -----------------------------------------------------

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    def metrics(self) -> RiskMetrics:
        """
        Compute all portfolio risk metrics.

        Returns
        -------
        RiskMetrics
        """

        from analytics.risk.statistics import (
            annualized_volatility,
        )

        from analytics.risk.drawdown import (
            max_drawdown,
            current_drawdown,
        )

        from analytics.risk.ratios import (
            sharpe_ratio,
            sortino_ratio,
            calmar_ratio,
            information_ratio,
        )

        from analytics.risk.var import (
            historical_var,
            historical_cvar,
        )

        from analytics.risk.beta import (
            beta,
            alpha,
            correlation,
            tracking_error,
            r_squared,
        )

        portfolio_returns = self.portfolio_returns
        benchmark_returns = self.benchmark_returns

        if benchmark_returns is not None:
            aligned = (
                pd.concat(
                    [portfolio_returns, benchmark_returns],
                    axis=1,
                )
                .dropna()
            )

            portfolio_returns = aligned.iloc[:, 0]
            benchmark_returns = aligned.iloc[:, 1]

        metrics = self._empty_metrics()

        # --------------------------------------------
        # Returns
        # --------------------------------------------

        from analytics.returns import ReturnsEngine

        returns = ReturnsEngine(
            self.portfolio_prices
        )

        metrics.cumulative_return = (
            returns.cumulative_return
        )

        metrics.cagr = (
            returns.cagr
        )

        # --------------------------------------------
        # Risk
        # --------------------------------------------

        metrics.volatility = annualized_volatility(
            portfolio_returns
        )

        metrics.max_drawdown = max_drawdown(
            self.portfolio_prices
        )

        metrics.current_drawdown = current_drawdown(
            self.portfolio_prices
        )

        # --------------------------------------------
        # Ratios
        # --------------------------------------------

        metrics.sharpe_ratio = sharpe_ratio(
            portfolio_returns,
            risk_free_rate=self.risk_free_rate,
        )

        metrics.sortino_ratio = sortino_ratio(
            portfolio_returns,
            risk_free_rate=self.risk_free_rate,
        )

        metrics.calmar_ratio = calmar_ratio(
            prices=self.portfolio_prices,
            returns=portfolio_returns,
        )

        # --------------------------------------------
        # VaR
        # --------------------------------------------

        metrics.historical_var = historical_var(
            portfolio_returns
        )

        metrics.historical_cvar = historical_cvar(
            portfolio_returns
        )

        # --------------------------------------------
        # Benchmark Metrics
        # --------------------------------------------

        if benchmark_returns is not None:

            metrics.beta = beta(
                portfolio_returns,
                benchmark_returns,
            )

            metrics.alpha = alpha(
                portfolio_returns,
                benchmark_returns,
                risk_free_rate=self.risk_free_rate,
            )

            metrics.correlation = correlation(
                portfolio_returns,
                benchmark_returns,
            )

            metrics.r_squared = r_squared(
                portfolio_returns,
                benchmark_returns,
            )

            metrics.tracking_error = tracking_error(
                portfolio_returns,
                benchmark_returns,
            )

            metrics.information_ratio = information_ratio(
                portfolio_returns,
                benchmark_returns,
            )

        # --------------------------------------------
        # Metadata
        # --------------------------------------------

        metrics.observations = len(
            portfolio_returns
        )

        metrics.benchmark_name = (
            self.benchmark_name
        )

        metrics.risk_free_rate = (
            self.risk_free_rate
        )

        return metrics

    def rolling_metrics(self):

        return RollingMetrics()

    def health(self):

        return PortfolioHealth()

    def summary(self):

        return AnalyticsResult(
            metrics=self.metrics(),
            rolling=self.rolling_metrics(),
            health=self.health(),
        )
    