from __future__ import annotations

from enum import Enum


class AssetType(str, Enum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUAL_FUND"
    BOND = "BOND"
    GOLD = "GOLD"
    REIT = "REIT"
    INVIT = "INVIT"
    CASH = "CASH"
    ALL = "All"


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    MUTUAL_FUND = "MUTUAL_FUND"

ETF_CODES = {
    "CPSETF",
    "ICIGOL",
    "GOLDEX",
    "ICIPSE",
    "TATSIL",
    # add others
}

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"