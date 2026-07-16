"""
Value at Risk (VaR) and Expected Shortfall (CVaR).

Pure functions only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .statistics import (
    annualized_volatility,
    validate_returns,
)


@dataclass(slots=True)
class VaRSummary:
    historical_var: float
    historical_cvar: float
    parametric_var: float
    parametric_cvar: float


# ---------------------------------------------------------
# Normal distribution helpers
# ---------------------------------------------------------

_NORMAL_Z = {
    0.90: 1.2815515655446004,
    0.95: 1.6448536269514722,
    0.975: 1.959963984540054,
    0.99: 2.3263478740408408,
}


_NORMAL_PDF = {
    0.90: 0.17549833193248685,
    0.95: 0.10313564037537139,
    0.975: 0.0584450698050354,
    0.99: 0.02665214220345808,
}


def _z(confidence: float) -> float:

    if confidence not in _NORMAL_Z:
        raise ValueError(
            f"Unsupported confidence level: {confidence}"
        )

    return _NORMAL_Z[confidence]


# ---------------------------------------------------------
# Historical VaR
# ---------------------------------------------------------

def historical_var(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    r = validate_returns(returns)

    percentile = (
        (1 - confidence)
        * 100
    )

    return float(
        -np.percentile(
            r,
            percentile,
        )
    )


# ---------------------------------------------------------
# Historical CVaR
# ---------------------------------------------------------

def historical_cvar(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    r = validate_returns(returns)

    var = historical_var(
        r,
        confidence,
    )

    tail = r[
        r <= -var
    ]

    if len(tail) == 0:
        return var

    return float(
        -tail.mean()
    )


# ---------------------------------------------------------
# Parametric VaR
# ---------------------------------------------------------

def parametric_var(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    r = validate_returns(returns)

    mu = r.mean()

    sigma = r.std(ddof=1)

    z = _z(confidence)

    return float(
        -(mu - z * sigma)
    )


# ---------------------------------------------------------
# Parametric CVaR
# ---------------------------------------------------------

def parametric_cvar(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    r = validate_returns(returns)

    mu = r.mean()

    sigma = r.std(ddof=1)

    z = _z(confidence)

    pdf = _NORMAL_PDF[confidence]

    alpha = 1 - confidence

    return float(
        -(mu - sigma * pdf / alpha)
    )


# ---------------------------------------------------------
# Annualized VaR
# ---------------------------------------------------------

def annualized_var(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    return (
        historical_var(
            returns,
            confidence,
        )
        * np.sqrt(252)
    )


# ---------------------------------------------------------
# Annualized CVaR
# ---------------------------------------------------------

def annualized_cvar(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float:

    return (
        historical_cvar(
            returns,
            confidence,
        )
        * np.sqrt(252)
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

def summary(
    returns: pd.Series,
    confidence: float = 0.95,
) -> VaRSummary:

    return VaRSummary(
        historical_var=historical_var(
            returns,
            confidence,
        ),
        historical_cvar=historical_cvar(
            returns,
            confidence,
        ),
        parametric_var=parametric_var(
            returns,
            confidence,
        ),
        parametric_cvar=parametric_cvar(
            returns,
            confidence,
        ),
    )