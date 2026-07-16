from __future__ import annotations

from datetime import datetime
from typing import Any

from kiteconnect import KiteConnect

from app_config import settings
from domain import (
    AssetType,
    Exchange,
    OrderType,
)

from domain.enums import Exchange
from portfolio.models import AssetHolding, EquityHolding, MutualFundHolding, Position
from utils import get_logger
from brokers import BrokerProvider
from pydantic import SecretStr

logger = get_logger(__name__)

def secret(value):
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    return value

class ZerodhaProvider(BrokerProvider):
    """
    PortfolioProvider implementation using Zerodha Kite Connect.
    """

    def __init__(
        self,
        access_token: str,
    ):

        self.kite = KiteConnect(
            api_key=secret(settings.zerodha_api_key),
        )

        self.kite.set_access_token(
            access_token,
        )

# -------------------------------------------------------
# Internal Mapping Helpers
# -------------------------------------------------------

    def _map_exchange(
        self,
        exchange: str | None,
    ) -> Exchange:
        """
        Maps Zerodha exchange string to Exchange enum.
        """

        if not exchange:
            return Exchange.NSE

        exchange = exchange.upper()

        if exchange == "BSE":
            return Exchange.BSE

        if exchange == "NSE":
            return Exchange.NSE

        if exchange == "MUTUAL_FUND":
            return Exchange.MUTUAL_FUND
        
        return Exchange.NSE


    def _detect_asset_type(
        self,
        item: dict[str, Any],
    ) -> AssetType:
        """
        Detect asset type from Zerodha holding.

        Extend this method as new asset classes
        are supported.
        """

        segment = (
            item.get("segment", "")
            or ""
        ).upper()

        instrument = (
            item.get("instrument_type", "")
            or ""
        ).upper()

        tradingsymbol = (
            item.get("tradingsymbol", "")
            or ""
        ).upper()

        if "ETF" in tradingsymbol:
            return AssetType.ETF

        if "ETF" in instrument:
            return AssetType.ETF

        if "ETF" in segment:
            return AssetType.ETF

        return AssetType.EQUITY

    def _build_equity_holding(
        self,
        item: dict[str, Any],
    ) -> EquityHolding:
        """
        Converts a Zerodha holding dictionary into
        a domain Holding object.
        """

        quantity = float(item["quantity"])

        average_price = float(item["average_price"])

        last_price = float(item["last_price"])

        invested_value = quantity * average_price

        current_value = quantity * last_price

        pnl = current_value - invested_value

        pnl_percent = (
            (pnl / invested_value) * 100
            if invested_value > 0
            else 0.0
        )

        return EquityHolding(
            symbol=item["tradingsymbol"],
            name=item.get(
                "tradingsymbol",
                item["tradingsymbol"],
            ),
            asset_type=self._detect_asset_type(item),
            exchange=self._map_exchange(
                item.get("exchange"),
            ),
            quantity=quantity,
            average_price=average_price,
            last_price=last_price,
            invested_value=invested_value,
            current_value=current_value,
            pnl=pnl,
            pnl_percent=pnl_percent,
            isin=item.get("isin"),
        )

    def _build_mutual_fund_holding(
        self,
        item: dict[str, Any],
    ) -> MutualFundHolding:

        quantity = float(
            item["quantity"]
        )

        average_nav = float(
            item["average_price"]
        )

        nav = float(
            item["last_price"]
        )

        invested_value = (
            quantity * average_nav
        )

        current_value = (
            quantity * nav
        )

        pnl = (
            current_value
            - invested_value
        )

        pnl_percent = (
            pnl / invested_value * 100
            if invested_value > 0
            else 0.0
        )

        return MutualFundHolding(
            fund_name=item["fund"],
            name=item["fund"],
            folio=item["folio"],
            tradingsymbol=item.get("tradingsymbol"),
            asset_type=AssetType.MUTUAL_FUND,
            exchange=Exchange.MUTUAL_FUND,
            quantity=quantity,
            average_price=average_nav,
            last_price=nav,
            invested_value=invested_value,
            current_value=current_value,
            pnl=pnl,
            pnl_percent=pnl_percent,
            xirr=float(item.get("xirr", 0.0)),
        )    

    # -------------------------------------------------------
    # Holdings
    # -------------------------------------------------------

    def get_equity_holdings(
        self,
    ) -> list[EquityHolding]:

        raw = self.kite.holdings()

        holdings = [
            self._build_equity_holding(item)
            for item in raw
        ]

        logger.info(
            "Fetched %d equity holdings.",
            len(holdings),
        )

        return holdings

    def get_mutual_fund_holdings(
        self,
    ) -> list[MutualFundHolding]:

        try:

            raw = self.kite.mf_holdings()

        except Exception:

            logger.info(
                "No mutual fund holdings found."
            )

            return []

        holdings = [
            self._build_mutual_fund_holding(
                item
            )
            for item in raw
        ]

        logger.info(
            "Fetched %d mutual fund holdings.",
            len(holdings),
        )

        return holdings
    
    def get_holdings(
        self,
    ) -> list[AssetHolding]:

        return (
            self.get_equity_holdings()
            + self.get_mutual_fund_holdings()
        )
    # -------------------------------------------------------
    # Positions
    # -------------------------------------------------------

    def get_positions(self) -> list[Position]:

        data = self.kite.positions()

        positions = []

        for p in data["net"]:

            positions.append(
                Position(
                    symbol=p["tradingsymbol"],
                    quantity=float(p["quantity"]),
                    buy_price=float(p["buy_price"]),
                    sell_price=float(p["sell_price"]),
                    pnl=float(p["pnl"]),
                )
            )

        return positions

    # -------------------------------------------------------
    # Orders
    # -------------------------------------------------------

    def get_transactions(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ):

        orders = self.kite.orders()

        txns: list[Transaction] = []

        for o in orders:

            if o["status"] != "COMPLETE":
                continue

            txn = Transaction(
                order_id=o["order_id"],
                symbol=o["tradingsymbol"],
                order_type=(
                    OrderType.BUY
                    if o["transaction_type"] == "BUY"
                    else OrderType.SELL
                ),
                quantity=float(o["quantity"]),
                price=float(o["average_price"]),
                order_date=datetime.fromisoformat(
                    o["exchange_update_timestamp"]
                ),
            )

            txns.append(txn)

        return txns

    # -------------------------------------------------------
    # User Profile
    # -------------------------------------------------------

    def profile(self) -> dict[str, Any]:
        return self.kite.profile()

    # -------------------------------------------------------
    # Margins
    # -------------------------------------------------------

    def total_margins(self) -> dict[str, Any]:
        return self.kite.margins()

    # -------------------------------------------------------
    # Funds
    # -------------------------------------------------------

    def equity_margins(self) -> dict[str, Any]:
        return self.kite.margins("equity")

    def get_cash(self) -> float:
        margins = self.kite.margins()

        return float(
            margins["equity"]["available"]["cash"]
        )
   
    @property
    def broker_name(self) -> str:
        return "Zerodha"
