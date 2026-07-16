"""
Global constants used by the risk analytics package.

This module intentionally contains only configuration values
and simple helper functions.

It has no dependency on Streamlit, FastAPI, Zerodha,
or any external API.
"""

from __future__ import annotations

from dataclasses import dataclass


# -------------------------------------------------------
# Trading Calendar
# -------------------------------------------------------

TRADING_DAYS_PER_YEAR: int = 252

WEEKS_PER_YEAR: int = 52

MONTHS_PER_YEAR: int = 12


# -------------------------------------------------------
# Risk Free Rate
# -------------------------------------------------------

DEFAULT_RISK_FREE_RATE: float = 0.06  # 6% annual


# -------------------------------------------------------
# Confidence Levels
# -------------------------------------------------------

DEFAULT_VAR_CONFIDENCE: float = 0.95

SUPPORTED_CONFIDENCE_LEVELS = (
    0.90,
    0.95,
    0.99,
)


# -------------------------------------------------------
# Numerical Stability
# -------------------------------------------------------

EPSILON: float = 1e-12


# -------------------------------------------------------
# Rolling Windows
# -------------------------------------------------------

DEFAULT_ROLLING_WINDOW = 60

ROLLING_WINDOWS = (
    21,     # 1 month
    63,     # 1 quarter
    126,    # 6 months
    252,    # 1 year
)


# -------------------------------------------------------
# Annualization
# -------------------------------------------------------

SQRT_252 = TRADING_DAYS_PER_YEAR ** 0.5


# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

@dataclass(slots=True)
class RiskConfig:
    """
    Configuration object for the analytics engine.
    """

    risk_free_rate: float = DEFAULT_RISK_FREE_RATE

    trading_days: int = TRADING_DAYS_PER_YEAR

    rolling_window: int = DEFAULT_ROLLING_WINDOW

    confidence_level: float = DEFAULT_VAR_CONFIDENCE

    annualize: bool = True

    def validate(self) -> None:

        if self.trading_days <= 0:
            raise ValueError(
                "trading_days must be positive."
            )

        if not (
            0 < self.confidence_level < 1
        ):
            raise ValueError(
                "confidence_level must lie between 0 and 1."
            )

        if self.rolling_window < 2:
            raise ValueError(
                "rolling_window must be >= 2."
            )

        if self.risk_free_rate < -1:
            raise ValueError(
                "Invalid risk-free rate."
            )


DEFAULT_CONFIG = RiskConfig()


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def annualize_return(
    value: float,
    periods: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Annualize a periodic return.
    """

    return value * periods


def annualize_volatility(
    volatility: float,
    periods: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Annualize a standard deviation.
    """

    return volatility * (periods ** 0.5)