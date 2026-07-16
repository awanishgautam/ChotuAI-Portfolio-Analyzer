from __future__ import annotations

from portfolio import Portfolio
from portfolio.models import PerformanceMetrics
from services.interfaces import AIProvider


class AIService:

    def __init__(
        self,
        provider: AIProvider,
    ):
        self.provider = provider

    def insights(
        self,
        portfolio: Portfolio,
        metrics: PerformanceMetrics,
    ):
        return self.provider.generate_insights(
            portfolio,
            metrics,
        )

    def ask(
        self,
        question: str,
        portfolio: Portfolio,
        metrics: PerformanceMetrics,
    ):
        return self.provider.chat(
            question,
            portfolio,
            metrics,
        )