import pandas as pd
import pytest

from analytics.returns import ReturnsEngine


def test_returns_engine_core_metrics() -> None:
    prices = pd.Series([100.0, 110.0, 99.0, 118.8],
        index=pd.date_range("2025-01-01", periods=4, freq="D"))
    engine = ReturnsEngine(prices)
    assert engine.daily_returns.tolist() == pytest.approx([0.1, -0.1, 0.2])
    assert engine.cumulative_return == pytest.approx(0.188)
    assert engine.max_drawdown == pytest.approx(-0.1)


def test_returns_engine_requires_two_prices() -> None:
    with pytest.raises(ValueError, match="At least two prices"):
        ReturnsEngine(pd.Series([100.0]))


def test_portfolio_value_validates_weights() -> None:
    prices = pd.DataFrame({"a": [100, 110], "b": [100, 90]})
    assert ReturnsEngine.portfolio_value(prices, [0.5, 0.5]).iloc[-1] == pytest.approx(100_000)
    with pytest.raises(ValueError, match="sum to 1"):
        ReturnsEngine.portfolio_value(prices, [0.2, 0.2])
