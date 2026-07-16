from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(slots=True)
class BenchmarkSummary:
    benchmark_name: str

    portfolio_return: float
    benchmark_return: float

    portfolio_cagr: float
    benchmark_cagr: float

    alpha: Optional[float]
    beta: Optional[float]
    correlation: Optional[float]

    tracking_error: Optional[float]
    information_ratio: Optional[float]

    volatility_portfolio: float
    volatility_benchmark: float


@dataclass(slots=True)
class RollingStatistics:
    rolling_beta: pd.Series
    rolling_alpha: pd.Series
    rolling_correlation: pd.Series