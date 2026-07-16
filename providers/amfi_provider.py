from __future__ import annotations

from datetime import datetime

from .market_data_provider import MarketDataProvider
from .models import PriceBar, Quote

class MutualFundProvider(MarketDataProvider):

    def latest_price(
        self,
        holding: MutualFundHolding,
    ) -> float:
        ...

    def history(
        self,
        holding: MutualFundHolding,
        period="5y",
    ) -> list[PriceBar]:
        ...