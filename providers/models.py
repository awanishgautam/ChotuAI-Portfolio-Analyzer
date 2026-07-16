from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PriceBar(BaseModel):
    model_config = ConfigDict(extra="ignore")

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: int = 0


class Quote(BaseModel):
    model_config = ConfigDict(extra="ignore")

    symbol: str

    price: float

    previous_close: float

    change: float

    change_percent: float