"""
Performance ratio calculations.

All functions are pure and have no dependency on
Streamlit, FastAPI, Zerodha, or OpenAI.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants import (
    DEFAULT_RISK_FREE_RATE,
    EPSILON,
)
from .drawdown import max_drawdown
from .statistics import (
    annualized_mean,
    annualized_volatility,
    beta,
    downside_deviation,
    tracking_error,
)


# ---------------------------------------------------------
# Sharpe Ratio
# ---------------------------------------------------------

def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:

    annual_return = annualized_mean(returns)

    annual_vol = annualized_volatility(returns)

    if annual_vol < EPSILON:
        return 0.0

    return (
        annual_return - risk_free_rate
    ) / annual_vol


# ---------------------------------------------------------
# Sortino Ratio
# ---------------------------------------------------------

def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    target_return: float = 0.0,
) -> float:

    annual_return = annualized_mean(
        returns
    )

    downside = downside_deviation(
        returns,
        target_return,
    )

    if downside < EPSILON:
        return 0.0

    return (
        annual_return - risk_free_rate
    ) / downside


# ---------------------------------------------------------
# Treynor Ratio
# ---------------------------------------------------------

def treynor_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:

    b = beta(
        portfolio_returns,
        benchmark_returns,
    )

    if abs(b) < EPSILON:
        return 0.0

    annual_return = annualized_mean(
        portfolio_returns
    )

    return (
        annual_return - risk_free_rate
    ) / b


# ---------------------------------------------------------
# Calmar Ratio
# ---------------------------------------------------------

def calmar_ratio(
    prices: pd.Series,
    returns: pd.Series,
) -> float:

    annual_return = annualized_mean(
        returns
    )

    mdd = abs(
        max_drawdown(prices)
    )

    if mdd < EPSILON:
        return 0.0

    return annual_return / mdd


# ---------------------------------------------------------
# Information Ratio
# ---------------------------------------------------------

def information_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    active_return = (
        annualized_mean(
            portfolio_returns
        )
        - annualized_mean(
            benchmark_returns
        )
    )

    te = tracking_error(
        portfolio_returns,
        benchmark_returns,
    )

    if te < EPSILON:
        return 0.0

    return active_return / te


# ---------------------------------------------------------
# Omega Ratio
# ---------------------------------------------------------

def omega_ratio(
    returns: pd.Series,
    threshold: float = 0.0,
) -> float:

    positive = (
        returns[
            returns > threshold
        ]
        - threshold
    ).sum()

    negative = (
        threshold
        - returns[
            returns < threshold
        ]
    ).sum()

    if negative < EPSILON:
        return np.inf

    return float(
        positive / negative
    )


# ---------------------------------------------------------
# Upside Capture Ratio
# ---------------------------------------------------------

def upside_capture_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    mask = benchmark_returns > 0

    if mask.sum() == 0:
        return 0.0

    portfolio_up = portfolio_returns[
        mask
    ].mean()

    benchmark_up = benchmark_returns[
        mask
    ].mean()

    if abs(benchmark_up) < EPSILON:
        return 0.0

    return float(
        portfolio_up
        / benchmark_up
    )


# ---------------------------------------------------------
# Downside Capture Ratio
# ---------------------------------------------------------

def downside_capture_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    mask = benchmark_returns < 0

    if mask.sum() == 0:
        return 0.0

    portfolio_down = portfolio_returns[
        mask
    ].mean()

    benchmark_down = benchmark_returns[
        mask
    ].mean()

    if abs(benchmark_down) < EPSILON:
        return 0.0

    return float(
        portfolio_down
        / benchmark_down
    )


# ---------------------------------------------------------
# Capture Ratio
# ---------------------------------------------------------

def capture_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    down = downside_capture_ratio(
        portfolio_returns,
        benchmark_returns,
    )

    if abs(down) < EPSILON:
        return 0.0

    return (
        upside_capture_ratio(
            portfolio_returns,
            benchmark_returns,
        )
        / abs(down)
    )


# ---------------------------------------------------------
# Appraisal Ratio
# ---------------------------------------------------------

def appraisal_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:

    a = alpha(
        portfolio_returns,
        benchmark_returns,
        risk_free_rate,
    )

    te = tracking_error(
        portfolio_returns,
        benchmark_returns,
    )

    if te < EPSILON:
        return 0.0

    return a / te