import numpy as np
import pandas as pd

from analytics.risk.risk_engine import RiskEngine
from domain.enums import Exchange
from portfolio.builder import PortfolioBuilder
from portfolio.models import EquityHolding, MutualFundHolding


def _holding(symbol: str, value: float, sector: str) -> EquityHolding:
    return EquityHolding(name=symbol, symbol=symbol, exchange=Exchange.NSE,
        quantity=1, average_price=value, last_price=value, invested_value=value,
        current_value=value, sector=sector)


def test_advanced_summary_includes_scores_exposures_stress_and_correlations() -> None:
    index = pd.date_range("2025-01-01", periods=300, freq="B")
    a = pd.Series(100 * np.cumprod(1 + np.sin(np.arange(300)) * 0.002 + 0.0004), index=index)
    b = pd.Series(80 * np.cumprod(1 + np.cos(np.arange(300)) * 0.003 + 0.0002), index=index)
    benchmark = pd.Series(100 * np.cumprod(1 + np.sin(np.arange(300) / 2) * 0.002 + 0.0003), index=index)
    portfolio = PortfolioBuilder().from_holdings([
        _holding("AAA", 600, "Technology"), _holding("BBB", 400, "Financials")])

    result = RiskEngine(a + b, benchmark, portfolio=portfolio,
        asset_prices=pd.DataFrame({"AAA": a, "BBB": b})).summary()

    assert 0 <= result.health.score <= 100
    assert result.exposures.sector == {"Financials": 40.0, "Technology": 60.0}
    assert result.exposures.country == {"India": 100.0}
    assert len(result.stress_tests) == 4
    assert result.correlations.assets == ["AAA", "BBB"]
    assert {"21", "63", "126", "252"}.issubset(result.rolling.by_window)


def test_short_history_skips_unavailable_rolling_windows() -> None:
    prices = pd.Series([100, 101, 100, 102], index=pd.date_range("2026-01-01", periods=4))
    rolling = RiskEngine(prices).rolling_metrics()
    assert rolling.by_window == {}
    assert rolling.dates == []


def test_indian_mutual_funds_are_not_reported_as_unknown_country() -> None:
    fund = MutualFundHolding(name="Indian Fund", fund_name="Indian Fund", folio="1",
        quantity=10, average_price=10, last_price=10, invested_value=100,
        current_value=100)
    portfolio = PortfolioBuilder().from_holdings([fund])
    assert portfolio.allocation_by("country") == {"India": 100.0}
