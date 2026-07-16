from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from .enums import AssetType, Exchange


class Instrument(BaseModel):
    """
    Master definition of a tradable instrument.

    Every holding references an Instrument.
    """

    model_config = ConfigDict(extra="ignore")

    symbol: str

    name: str

    exchange: Exchange

    asset_type: AssetType

    isin: Optional[str] = None

    sector: Optional[str] = None

    industry: Optional[str] = None

    currency: str = "INR"

    benchmark: Optional[str] = None

    expense_ratio: Optional[float] = None

    amc: Optional[str] = None

    fund_manager: Optional[str] = None

    is_active: bool = True