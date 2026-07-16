import numpy as np
import pandas as pd
import pytest

from analytics.risk.statistics import beta, correlation, downside_deviation, validate_returns, z_score


def test_validate_returns_cleans_non_finite_values() -> None:
    values = pd.Series([0.01, np.nan, np.inf, -0.02, -np.inf])
    assert validate_returns(values).tolist() == [0.01, -0.02]


def test_validate_returns_rejects_insufficient_data() -> None:
    with pytest.raises(ValueError, match="two observations"):
        validate_returns(pd.Series([0.01, np.nan]))


def test_relationship_statistics() -> None:
    benchmark = pd.Series([0.01, 0.02, -0.01, 0.03])
    portfolio = benchmark * 2
    assert beta(portfolio, benchmark) == pytest.approx(2)
    assert correlation(portfolio, benchmark) == pytest.approx(1)


def test_downside_deviation_and_constant_z_score() -> None:
    assert downside_deviation(pd.Series([0.01, -0.02, -0.01])) > 0
    assert z_score(pd.Series([0.01, 0.01, 0.01])).eq(0).all()
