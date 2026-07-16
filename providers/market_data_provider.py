from __future__ import annotations

from abc import ABC, abstractmethod

from .models import PriceBar, Quote


class MarketDataProvider(ABC):

    @abstractmethod
    def supports(
        self,
        holding,
    ) -> bool:
        ...
        
    @abstractmethod
    def latest_price(
        self,
        symbol: str,
    ) -> float:
        """
        Latest traded price.
        """
        ...

    @abstractmethod
    def quote(
        self,
        symbol: str,
    ) -> Quote:
        ...

    @abstractmethod
    def history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> list[PriceBar]:
        ...

    @abstractmethod
    def multiple_history(
        self,
        symbols: list[str],
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, list[PriceBar]]:
        ...