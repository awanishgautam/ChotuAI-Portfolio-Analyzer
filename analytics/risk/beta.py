"""
Benchmark-related statistics.

Pure functions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .constants import (
    DEFAULT_RISK_FREE_RATE,
    TRADING_DAYS_PER_YEAR,
)
from .statistics import (
    beta,
    correlation,
    tracking_error,
)


@dataclass(slots=True)
class BetaSummary:
    beta: float
    alpha: float
    correlation: float
    tracking_error: float
    r_squared: float

# ---------------------------------------------------------
# Jensen Alpha
# ---------------------------------------------------------
def alpha(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> float:

    portfolio = (
        portfolio_returns.mean()
        * TRADING_DAYS_PER_YEAR
    )

    benchmark = (
        benchmark_returns.mean()
        * TRADING_DAYS_PER_YEAR
    )

    b = beta(
        portfolio_returns,
        benchmark_returns,
    )

    return (
        portfolio
        - (
            risk_free_rate
            + b
            * (
                benchmark
                - risk_free_rate
            )
        )
    )


def r_squared(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:

    corr = correlation(
        portfolio_returns,
        benchmark_returns,
    )

    return corr ** 2


def rolling_beta(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 60,
) -> pd.Series:

    df = pd.concat(
        [
            portfolio_returns.rename("p"),
            benchmark_returns.rename("b"),
        ],
        axis=1,
    ).dropna()

    values = []
    index = []

    for i in range(
        window,
        len(df) + 1,
    ):

        sample = df.iloc[
            i - window:i
        ]

        cov = np.cov(
            sample["p"],
            sample["b"],
            ddof=1,
        )[0][1]

        var = np.var(
            sample["b"],
            ddof=1,
        )

        values.append(
            0.0 if var == 0 else cov / var
        )

        index.append(
            sample.index[-1]
        )

    return pd.Series(
        values,
        index=index,
        name="Rolling Beta",
    )


def rolling_alpha(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    window: int = 60,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> pd.Series:

    df = pd.concat(
        [
            portfolio_returns.rename("p"),
            benchmark_returns.rename("b"),
        ],
        axis=1,
    ).dropna()

    values = []
    index = []

    for i in range(
        window,
        len(df) + 1,
    ):

        sample = df.iloc[
            i - window:i
        ]

        values.append(
            alpha(
                sample["p"],
                sample["b"],
                risk_free_rate,
            )
        )

        index.append(
            sample.index[-1]
        )

    return pd.Series(
        values,
        index=index,
        name="Rolling Alpha",
    )


def summary(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
) -> BetaSummary:

    return BetaSummary(
        beta=beta(
            portfolio_returns,
            benchmark_returns,
        ),
        alpha=alpha(
            portfolio_returns,
            benchmark_returns,
            risk_free_rate,
        ),
        correlation=correlation(
            portfolio_returns,
            benchmark_returns,
        ),
        tracking_error=tracking_error(
            portfolio_returns,
            benchmark_returns,
        ),
        r_squared=r_squared(
            portfolio_returns,
            benchmark_returns,
        ),
    )