from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RiskMetrics(BaseModel):
    """
    Complete portfolio risk analytics.

    Returned by RiskEngine.summary()
    """

    model_config = ConfigDict(
        extra="ignore"
    )

    # =====================================================
    # Returns
    # =====================================================

    cumulative_return: float = Field(default=0.0)

    annual_return: float = Field(default=0.0)

    cagr: float = Field(default=0.0)

    # =====================================================
    # Risk
    # =====================================================

    volatility: float = Field(default=0.0)

    downside_deviation: float = Field(default=0.0)

    max_drawdown: float = Field(default=0.0)

    current_drawdown: float = Field(default=0.0)

    drawdown_duration: int = Field(default=0)

    # =====================================================
    # Ratios
    # =====================================================

    sharpe_ratio: float = Field(default=0.0)

    sortino_ratio: float = Field(default=0.0)

    calmar_ratio: float = Field(default=0.0)

    treynor_ratio: float = Field(default=0.0)

    information_ratio: float = Field(default=0.0)

    omega_ratio: float = Field(default=0.0)

    appraisal_ratio: float = Field(default=0.0)

    # =====================================================
    # Benchmark
    # =====================================================

    alpha: float = Field(default=0.0)

    beta: float = Field(default=0.0)

    correlation: float = Field(default=0.0)

    r_squared: float = Field(default=0.0)

    tracking_error: float = Field(default=0.0)

    excess_return: float = Field(default=0.0)

    upside_capture: float = Field(default=0.0)

    downside_capture: float = Field(default=0.0)

    capture_ratio: float = Field(default=0.0)

    # =====================================================
    # Tail Risk
    # =====================================================

    historical_var: float = Field(default=0.0)

    historical_cvar: float = Field(default=0.0)

    parametric_var: float = Field(default=0.0)

    parametric_cvar: float = Field(default=0.0)

    # =====================================================
    # Distribution
    # =====================================================

    skewness: float = Field(default=0.0)

    kurtosis: float = Field(default=0.0)

    # =====================================================
    # Trading Statistics
    # =====================================================

    best_day: float = Field(default=0.0)

    worst_day: float = Field(default=0.0)

    positive_days: int = Field(default=0)

    negative_days: int = Field(default=0)

    win_rate: float = Field(default=0.0)

    # =====================================================
    # Portfolio
    # =====================================================

    observations: int = Field(default=0)

    benchmark_name: str = Field(default="")

    risk_free_rate: float = Field(default=0.0)


class RollingMetrics(BaseModel):
    """
    Rolling statistics used for charts.
    """

    model_config = ConfigDict(extra="ignore")

    rolling_return: list[float] = Field(default_factory=list)

    rolling_volatility: list[float] = Field(default_factory=list)

    rolling_sharpe: list[float] = Field(default_factory=list)

    rolling_sortino: list[float] = Field(default_factory=list)

    rolling_beta: list[float] = Field(default_factory=list)

    rolling_alpha: list[float] = Field(default_factory=list)

    rolling_drawdown: list[float] = Field(default_factory=list)


class PortfolioHealth(BaseModel):
    """
    High-level health assessment.

    Useful for AI summaries and dashboards.
    """

    model_config = ConfigDict(extra="ignore")

    score: int = Field(default=0)

    risk_level: str = Field(default="Unknown")

    diversification_score: int = Field(default=0)

    concentration_score: int = Field(default=0)

    drawdown_score: int = Field(default=0)

    volatility_score: int = Field(default=0)

    recommendation: str = Field(default="")


class AnalyticsResult(BaseModel):
    """
    Complete object returned by the analytics engine.
    """

    model_config = ConfigDict(extra="ignore")

    metrics: RiskMetrics

    rolling: RollingMetrics

    health: PortfolioHealth
    