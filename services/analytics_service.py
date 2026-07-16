from __future__ import annotations

from portfolio import Portfolio

from services.interfaces import AnalyticsProvider


class AnalyticsService:

    def __init__(
        self,
        provider: AnalyticsProvider,
    ):
        self.provider = provider

    def metrics(
        self,
        portfolio: Portfolio,
    ):
        return self.provider.calculate_metrics(
            portfolio
        )

    def benchmark(
        self,
        portfolio: Portfolio,
        benchmark: str,
    ):
        return self.provider.compare_with_benchmark(
            portfolio,
            benchmark,
        )