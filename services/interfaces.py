from __future__ import annotations

from abc import ABC, abstractmethod

from portfolio import Portfolio
from portfolio.models import (
    PerformanceMetrics,
    Transaction,
)


class PortfolioProvider(ABC):
    """
    Broker interface.

    Zerodha, Upstox, CSV etc. will implement this.
    """

    @abstractmethod
    def authenticate(self) -> None:
        ...

    @abstractmethod
    def get_holdings(self) -> list[Holding]:
        ...

    @abstractmethod
    def get_transactions(self) -> list[Transaction]:
        ...

    @abstractmethod
    def get_portfolio(self) -> Portfolio:
        ...


class MarketDataProvider(ABC):

    @abstractmethod
    def get_price_history(
        self,
        symbol: str,
        period: str = "1y",
    ):
        ...

    @abstractmethod
    def get_latest_price(
        self,
        symbol: str,
    ) -> float:
        ...


class AnalyticsProvider(ABC):

    @abstractmethod
    def calculate_metrics(
        self,
        portfolio: Portfolio,
    ) -> PerformanceMetrics:
        ...

    @abstractmethod
    def compare_with_benchmark(
        self,
        portfolio: Portfolio,
        benchmark: str,
    ) -> dict:
        ...


class AIProvider(ABC):

    @abstractmethod
    def generate_insights(
        self,
        portfolio: Portfolio,
        metrics: PerformanceMetrics,
    ) -> list[AIInsight]:
        ...

    @abstractmethod
    def chat(
        self,
        question: str,
        portfolio: Portfolio,
        metrics: PerformanceMetrics,
    ) -> str:
        ...