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
    CorrelationAnalysis,
    ExposureBreakdown,
    PortfolioHealth,
    RiskMetrics,
    RollingMetrics,
    StressTestResult,
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
        portfolio=None,
        asset_prices: pd.DataFrame | None = None,
    ):

        self.config = config or DEFAULT_CONFIG

        self.config.validate()

        self.benchmark_name = benchmark_name
        self.portfolio = portfolio
        self.asset_prices = asset_prices.copy() if asset_prices is not None else None

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

    def rolling_metrics(self, windows: tuple[int, ...] | None = None) -> RollingMetrics:
        windows = windows or tuple(dict.fromkeys((21, 63, 126, 252, self.config.rolling_window)))
        returns = self.portfolio_returns
        result = RollingMetrics()
        for window in windows:
            if window < 2 or len(returns) < window:
                continue
            mean = returns.rolling(window).mean()
            vol = returns.rolling(window).std(ddof=1) * self.config.trading_days ** 0.5
            annual_return = mean * self.config.trading_days
            downside = returns.sub(self.risk_free_rate / self.config.trading_days).clip(upper=0).pow(2).rolling(window).mean().pow(0.5) * self.config.trading_days ** 0.5
            wealth = (1 + returns).cumprod()
            frame = pd.DataFrame({
                "return": (1 + returns).rolling(window).apply(lambda x: x.prod(), raw=True) - 1,
                "volatility": vol,
                "sharpe": (annual_return - self.risk_free_rate) / vol.replace(0, pd.NA),
                "sortino": (annual_return - self.risk_free_rate) / downside.replace(0, pd.NA),
                "drawdown": wealth / wealth.cummax() - 1,
            })
            if self.benchmark_returns is not None:
                aligned = pd.concat([returns.rename("p"), self.benchmark_returns.rename("b")], axis=1).dropna()
                frame["beta"] = aligned.p.rolling(window).cov(aligned.b) / aligned.b.rolling(window).var()
                frame["alpha"] = (aligned.p.rolling(window).mean() * self.config.trading_days - self.risk_free_rate) - frame["beta"] * (aligned.b.rolling(window).mean() * self.config.trading_days - self.risk_free_rate)
                frame["correlation"] = aligned.p.rolling(window).corr(aligned.b)
            frame = frame.dropna(how="all")
            payload = {"dates": [str(x.date()) for x in frame.index]}
            payload.update({column: [float(x) if pd.notna(x) else 0.0 for x in frame[column]] for column in frame.columns})
            result.by_window[str(window)] = payload
        primary = result.by_window.get(str(self.config.rolling_window), {})
        result.dates = primary.get("dates", [])
        mapping = {"rolling_return": "return", "rolling_volatility": "volatility", "rolling_sharpe": "sharpe", "rolling_sortino": "sortino", "rolling_beta": "beta", "rolling_alpha": "alpha", "rolling_drawdown": "drawdown", "rolling_correlation": "correlation"}
        for field, key in mapping.items():
            setattr(result, field, primary.get(key, []))
        return result

    def health(self):
        metrics = self.metrics()
        volatility_score = max(0, min(100, round(100 - metrics.volatility * 250)))
        drawdown_score = max(0, min(100, round(100 + metrics.max_drawdown * 200)))
        weights = []
        if self.portfolio is not None and self.portfolio.market_value > 0:
            weights = [h.market_value / self.portfolio.market_value for h in self.portfolio.holdings]
        hhi = sum(weight * weight for weight in weights) if weights else 1.0
        diversification = max(0, min(100, round((1 - hhi) * 125)))
        concentration = max(0, 100 - round(max(weights, default=1.0) * 100))
        risk_score = round(0.4 * volatility_score + 0.35 * drawdown_score + 0.25 * diversification)
        return_score = max(0, min(100, round(50 + metrics.sharpe_ratio * 20)))
        score = round(0.7 * risk_score + 0.3 * return_score)
        level = "Low" if risk_score >= 75 else "Moderate" if risk_score >= 50 else "High"
        recommendation = "Portfolio risk appears balanced." if score >= 70 else "Review concentration and downside risk." if score >= 45 else "Reduce concentration and tail-risk exposure."
        return PortfolioHealth(score=score, risk_score=risk_score, return_score=return_score, risk_level=level, diversification_score=diversification, concentration_score=concentration, drawdown_score=drawdown_score, volatility_score=volatility_score, recommendation=recommendation)

    def exposures(self) -> ExposureBreakdown:
        if self.portfolio is None:
            return ExposureBreakdown()
        return ExposureBreakdown(
            sector=self.portfolio.allocation_by("sector"),
            country=self.portfolio.allocation_by("country"),
            asset_type=self.portfolio.allocation_by("asset_type"),
        )

    def stress_tests(self) -> list[StressTestResult]:
        beta_value = self.metrics().beta if self.has_benchmark else 1.0
        value = self.portfolio.market_value if self.portfolio is not None else float(self.portfolio_prices.iloc[-1])
        scenarios = {"Market correction": -0.10, "Severe bear market": -0.25, "Volatility shock": -0.15, "Recovery rally": 0.10}
        return [StressTestResult(scenario=name, shock=shock, estimated_return=shock * beta_value, estimated_loss=max(0.0, -shock * beta_value * value)) for name, shock in scenarios.items()]

    def correlation_analysis(self) -> CorrelationAnalysis:
        if self.asset_prices is None or self.asset_prices.shape[1] < 2:
            return CorrelationAnalysis()
        corr = self.asset_prices.pct_change().corr().fillna(0.0)
        pairs = [(float(corr.iloc[i, j]), corr.index[i], corr.columns[j]) for i in range(len(corr)) for j in range(i + 1, len(corr))]
        highest = max(pairs, default=(0.0, "", ""), key=lambda item: item[0])
        average = sum(item[0] for item in pairs) / len(pairs) if pairs else 0.0
        return CorrelationAnalysis(assets=[str(x) for x in corr.columns], matrix=corr.astype(float).values.tolist(), average_correlation=average, highest_pair=[str(highest[1]), str(highest[2])] if pairs else [], highest_correlation=highest[0])

    def summary(self):

        return AnalyticsResult(
            metrics=self.metrics(),
            rolling=self.rolling_metrics(),
            health=self.health(),
            exposures=self.exposures(),
            stress_tests=self.stress_tests(),
            correlations=self.correlation_analysis(),
        )
