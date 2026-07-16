"""
Drawdown analytics.

This module contains pure functions for computing drawdowns,
maximum drawdown, recovery periods, and underwater curves.

No dependency on:
    - Streamlit
    - FastAPI
    - Zerodha
    - OpenAI
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------


@dataclass(slots=True)
class DrawdownSummary:
    max_drawdown: float
    max_drawdown_date: pd.Timestamp | None
    recovery_date: pd.Timestamp | None
    drawdown_duration: int
    current_drawdown: float


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _validate(prices: pd.Series) -> pd.Series:

    prices = (
        prices
        .dropna()
        .astype(float)
        .sort_index()
    )

    if len(prices) < 2:
        raise ValueError(
            "At least two observations required."
        )

    return prices


# ---------------------------------------------------------
# Running Peak
# ---------------------------------------------------------


def running_peak(
    prices: pd.Series,
) -> pd.Series:

    prices = _validate(prices)

    return prices.cummax()


# ---------------------------------------------------------
# Drawdown Curve
# ---------------------------------------------------------


def drawdown_curve(
    prices: pd.Series,
) -> pd.Series:
    """
    Returns drawdown series.

    Example

        0.00
       -0.02
       -0.08
       -0.01
        0.00
    """

    prices = _validate(prices)

    peak = running_peak(prices)

    return (
        prices - peak
    ) / peak


# ---------------------------------------------------------
# Underwater Curve
# ---------------------------------------------------------


def underwater_curve(
    prices: pd.Series,
) -> pd.Series:
    """
    Alias for drawdown curve.
    """

    return drawdown_curve(prices)


# ---------------------------------------------------------
# Maximum Drawdown
# ---------------------------------------------------------


def max_drawdown(
    prices: pd.Series,
) -> float:

    return float(
        drawdown_curve(prices).min()
    )


# ---------------------------------------------------------
# Drawdown Date
# ---------------------------------------------------------


def max_drawdown_date(
    prices: pd.Series,
):

    dd = drawdown_curve(prices)

    return dd.idxmin()


# ---------------------------------------------------------
# Current Drawdown
# ---------------------------------------------------------


def current_drawdown(
    prices: pd.Series,
) -> float:

    return float(
        drawdown_curve(prices).iloc[-1]
    )


# ---------------------------------------------------------
# Recovery Date
# ---------------------------------------------------------


def recovery_date(
    prices: pd.Series,
):

    prices = _validate(prices)

    peak = running_peak(prices)

    worst = drawdown_curve(prices).idxmin()

    previous_peak = peak.loc[worst]

    after = prices.loc[worst:]

    recovered = after[
        after >= previous_peak
    ]

    if recovered.empty:
        return None

    return recovered.index[0]


# ---------------------------------------------------------
# Drawdown Duration
# ---------------------------------------------------------


def drawdown_duration(
    prices: pd.Series,
) -> int:
    """
    Number of periods between the
    maximum drawdown and recovery.
    """

    worst = max_drawdown_date(prices)

    recovered = recovery_date(prices)

    if recovered is None:
        return 0

    return (
        prices.index.get_loc(recovered)
        - prices.index.get_loc(worst)
    )


# ---------------------------------------------------------
# Longest Drawdown
# ---------------------------------------------------------


def longest_drawdown(
    prices: pd.Series,
) -> int:
    """
    Longest continuous underwater period.
    """

    dd = drawdown_curve(prices)

    longest = 0
    current = 0

    for value in dd:

        if value < 0:
            current += 1
            longest = max(
                longest,
                current,
            )
        else:
            current = 0

    return longest


# ---------------------------------------------------------
# Rolling Maximum Drawdown
# ---------------------------------------------------------


def rolling_max_drawdown(
    prices: pd.Series,
    window: int = 252,
) -> pd.Series:

    prices = _validate(prices)

    result = []

    index = []

    for i in range(
        window,
        len(prices) + 1,
    ):

        window_prices = prices.iloc[
            i - window:i
        ]

        result.append(
            max_drawdown(window_prices)
        )

        index.append(
            prices.index[i - 1]
        )

    return pd.Series(
        result,
        index=index,
        name="Rolling Max Drawdown",
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------


def summary(
    prices: pd.Series,
) -> DrawdownSummary:

    return DrawdownSummary(
        max_drawdown=max_drawdown(
            prices
        ),
        max_drawdown_date=max_drawdown_date(
            prices
        ),
        recovery_date=recovery_date(
            prices
        ),
        drawdown_duration=drawdown_duration(
            prices
        ),
        current_drawdown=current_drawdown(
            prices
        ),
    )
