"""
Statistical helper functions for portfolio analytics.

This module intentionally contains only pure functions.
It has no dependency on Streamlit, FastAPI, Zerodha,
or any UI framework.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants import (
    EPSILON,
    TRADING_DAYS_PER_YEAR,
)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

def validate_returns(
    returns: pd.Series,
) -> pd.Series:
    """
    Remove NaN/Inf values and validate the series.
    """

    if returns is None:
        raise ValueError("Returns cannot be None.")

    cleaned = (
        returns.replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
        .astype(float)
    )

    if len(cleaned) < 2:
        raise ValueError(
            "At least two observations required."
        )

    return cleaned


# ---------------------------------------------------------
# Mean
# ---------------------------------------------------------

def mean_return(
    returns: pd.Series,
) -> float:

    r = validate_returns(returns)

    return float(r.mean())


def annualized_mean(
    returns: pd.Series,
) -> float:

    return (
        mean_return(returns)
        * TRADING_DAYS_PER_YEAR
    )


# ---------------------------------------------------------
# Volatility
# ---------------------------------------------------------

def volatility(
    returns: pd.Series,
) -> float:

    r = validate_returns(returns)

    return float(r.std(ddof=1))


def annualized_volatility(
    returns: pd.Series,
) -> float:

    return (
        volatility(returns)
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


# ---------------------------------------------------------
# Variance
# ---------------------------------------------------------

def variance(
    returns: pd.Series,
) -> float:

    r = validate_returns(returns)

    return float(r.var(ddof=1))


# ---------------------------------------------------------
# Covariance
# ---------------------------------------------------------

def covariance(
    x: pd.Series,
    y: pd.Series,
) -> float:

    df = pd.concat(
        [x, y],
        axis=1,
    ).dropna()

    if len(df) < 2:
        return 0.0

    return float(
        np.cov(
            df.iloc[:, 0],
            df.iloc[:, 1],
            ddof=1,
        )[0][1]
    )


# ---------------------------------------------------------
# Correlation
# ---------------------------------------------------------

def correlation(
    x: pd.Series,
    y: pd.Series,
) -> float:

    df = pd.concat(
        [x, y],
        axis=1,
    ).dropna()

    if len(df) < 2:
        return 0.0

    return float(
        df.iloc[:, 0].corr(
            df.iloc[:, 1]
        )
    )


# ---------------------------------------------------------
# Beta
# ---------------------------------------------------------

def beta(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    cov = covariance(
        portfolio_returns,
        benchmark_returns,
    )

    var = variance(
        benchmark_returns
    )

    if abs(var) < EPSILON:
        return 0.0

    return cov / var


# ---------------------------------------------------------
# Tracking Error
# ---------------------------------------------------------

def tracking_error(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    df = pd.concat(
        [
            portfolio_returns.rename("portfolio"),
            benchmark_returns.rename("benchmark"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    active = (
        df["portfolio"]
        - df["benchmark"]
    )

    if len(active) < 2:
        return 0.0

    return float(
        active.std(ddof=1)
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


# ---------------------------------------------------------
# Skewness
# ---------------------------------------------------------

def skewness(
    returns: pd.Series,
) -> float:

    r = validate_returns(returns)

    return float(
        r.skew()
    )


# ---------------------------------------------------------
# Kurtosis
# ---------------------------------------------------------

def kurtosis(
    returns: pd.Series,
) -> float:

    r = validate_returns(returns)

    return float(
        r.kurt()
    )


# ---------------------------------------------------------
# Downside Returns
# ---------------------------------------------------------

def downside_returns(
    returns: pd.Series,
    target: float = 0.0,
) -> pd.Series:

    r = validate_returns(returns)

    return r[
        r < target
    ]


# ---------------------------------------------------------
# Downside Deviation
# ---------------------------------------------------------

def downside_deviation(
    returns: pd.Series,
    target: float = 0.0,
) -> float:

    downside = downside_returns(
        returns,
        target,
    )

    if len(downside) == 0:
        return 0.0

    diff = (
        downside
        - target
    )

    return float(
        np.sqrt(
            np.mean(
                diff**2
            )
        )
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


# ---------------------------------------------------------
# Rolling Mean
# ---------------------------------------------------------

def rolling_mean(
    returns: pd.Series,
    window: int,
) -> pd.Series:

    return (
        validate_returns(returns)
        .rolling(window)
        .mean()
    )


# ---------------------------------------------------------
# Rolling Volatility
# ---------------------------------------------------------

def rolling_volatility(
    returns: pd.Series,
    window: int,
) -> pd.Series:

    return (
        validate_returns(returns)
        .rolling(window)
        .std(ddof=1)
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


# ---------------------------------------------------------
# Z-score
# ---------------------------------------------------------

def z_score(
    returns: pd.Series,
) -> pd.Series:

    r = validate_returns(
        returns
    )

    std = r.std(ddof=1)

    if std < EPSILON:
        return pd.Series(
            0.0,
            index=r.index,
        )

    return (
        r - r.mean()
    ) / std


# ---------------------------------------------------------
# Winsorize
# ---------------------------------------------------------

def winsorize(
    returns: pd.Series,
    limit: float = 0.01,
) -> pd.Series:
    """
    Clip extreme observations.
    """

    r = validate_returns(
        returns
    )

    lower = r.quantile(limit)

    upper = r.quantile(
        1 - limit
    )

    return r.clip(
        lower,
        upper,
    )