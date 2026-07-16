from pyclbr import Function

from breeze_connect import BreezeConnect
from datetime import date, datetime, timedelta
import logging
import pprint

from portfolio.models import (
    AssetHolding,
    EquityHolding,
    MutualFundHolding,
    Position,
    Transaction,
)

from domain.enums import (
    Exchange,
    OrderType,
    ETF_CODES,
)

from domain import (
    AssetType,
    Exchange,
    OrderType,
)

from app_config import settings
from brokers.base import BrokerProvider

class ICICIDirectProvider(BrokerProvider):

    def __init__(
        self,
        access_token: str,
    ):

        self.breeze = BreezeConnect(
            api_key=settings.icici_api_key.get_secret_value(),
        )

        self.breeze.generate_session(
            api_secret=settings.icici_api_secret.get_secret_value(),
            session_token=access_token,
        )

    def get_holdings(
        self,
        ) -> list[AssetHolding]:

            return (
                self.get_equity_holdings()
                + self.get_mutual_fund_holdings()
            )
    
    def get_equity_holdings(
        self,
        ) -> list[AssetHolding]:

        demat_response = self.breeze.get_demat_holdings()
        holdings_response = self.breeze.get_portfolio_holdings(
            exchange_code="NSE",
            from_date=(
                datetime.now() - timedelta(days=365)
            ).strftime("%Y-%m-%dT00:00:00.000Z"),
            to_date=datetime.now().strftime(
                "%Y-%m-%dT00:00:00.000Z"
            ),
            stock_code="",
            portfolio_type="",
        )

        demat = demat_response.get(
            "Success",
            [],
        )

        portfolio = holdings_response.get(
            "Success",
            [],
        )

        portfolio_lookup = {
            item["stock_code"]: item
            for item in portfolio
        }

        holdings = []

        for item in demat:

            symbol = item["stock_code"]

            portfolio_item = portfolio_lookup.get(
                symbol,
                {},
            )

            quantity = float(
                item.get(
                    "quantity",
                    0,
                )
            )

            average_price = float(
                portfolio_item.get(
                    "average_price",
                    0,
                )
                or 0
            )

            last_price = float(
                portfolio_item.get(
                    "current_market_price",
                    0,
                )
                or 0
            )

            invested_value = (
                quantity
                * average_price
            )

            current_value = (
                quantity
                * last_price
            )

            pnl = (
                current_value
                - invested_value
            )

            pnl_percent = (
                pnl / invested_value * 100
                if invested_value > 0
                else 0
            )

            exchange = portfolio_item.get(
                "exchange_code",
                "NSE",
            )

            holdings.append(
                EquityHolding(
                    name=symbol,
                    symbol=symbol,
                    exchange=Exchange(exchange),
                    isin=item.get(
                        "stock_ISIN",
                    ),
                    sector=None,
                    quantity=quantity,
                    average_price=average_price,
                    last_price=last_price,
                    invested_value=invested_value,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                )
            )
        return holdings

    def _is_etf(self, item):
        return item["stock_code"] in ETF_CODES

    def _is_mutual_fund(self, item):
        isin = item["stock_ISIN"]

        return (
            isin.startswith("INF")
            and not self._is_etf(item)
        )

    def _build_mutual_fund_holding(
        self,
        demat_item: dict,
        portfolio_item: dict,
    ) -> MutualFundHolding:

        quantity = float(demat_item["quantity"])

        average_nav = float(
            portfolio_item.get("average_price", 0) or 0
        )

        nav = float(
            portfolio_item.get("current_market_price", 0) or 0
        )

        invested_value = quantity * average_nav
        current_value = quantity * nav

        pnl = current_value - invested_value

        pnl_percent = (
            pnl / invested_value * 100
            if invested_value > 0
            else 0.0
        )

        return MutualFundHolding(
            fund_name=demat_item["stock_code"],
            name=demat_item["stock_code"],
            folio="",
            tradingsymbol=demat_item["stock_code"],
            isin=demat_item.get("stock_ISIN", ""),
            asset_type=AssetType.MUTUAL_FUND,
            exchange=Exchange.MUTUAL_FUND,
            quantity=quantity,
            average_price=average_nav,
            last_price=nav,
            invested_value=invested_value,
            current_value=current_value,
            pnl=pnl,
            pnl_percent=pnl_percent,
            xirr=None,
        )

    def get_mutual_fund_holdings(
        self,
    ) -> list[AssetHolding]:
        
        logging.info(
            "ICICI Direct APIs only support Equity. Mutual Funds Are not supported",
        )
        return []
    
        demat = self.breeze.get_demat_holdings()["Success"]
        logging.info("Total demat holdings: %d", len(demat))
        for item in demat:
            logging.info(
                "%s %s",
                item["stock_code"],
                item["stock_ISIN"],
            )

        portfolio = self.breeze.get_portfolio_holdings(
            exchange_code="NSE",
            from_date=(
                datetime.now() - timedelta(days=365)
            ).strftime("%Y-%m-%dT00:00:00.000Z"),
            to_date=datetime.now().strftime(
                "%Y-%m-%dT00:00:00.000Z"),
            stock_code="",
            portfolio_type="",
        )["Success"]

        portfolio_lookup = {
            item["stock_code"]: item
            for item in portfolio
        }

        holdings = []

        for item in demat:

            # icici get_demat_holdings() returns all: equity, MF, ETF, ..
            # Check and remove ETFs, Equity
            isin = item.get("stock_ISIN", "")

            if (self._is_etf(item)):
                continue

            if not self._is_mutual_fund(item):
                continue
            logging.info("Mutual funds found: %d", len(holdings))
            for item in holdings:
                logger.info(
                    "%s  %s",
                    item["stock_code"],
                    item["stock_ISIN"],
                )

            portfolio_item = portfolio_lookup.get(
                item["stock_code"],
                {},
            )

            holdings.append(
                self._build_mutual_fund_holding(
                    item,
                    portfolio_item,
                )
            )

        return holdings
    
    @property
    def broker_name(self) -> str:
        return "ICICI Direct"

    def get_positions(self):

        response = self.breeze.get_portfolio_positions()

        positions = []

        items = response.get("Success") or []

        if not items:
            logging.info("No open positions found.")
            return positions

        for item in items:

            positions.append(
                Position(
                    symbol=item["stock_code"],
                    quantity=float(item["quantity"]),
                    buy_price=float(item.get("average_price") or 0),
                    sell_price=float(item.get("current_market_price") or 0),
                    pnl=float(item.get("booked_profit_loss") or 0),
                )
            )

        return positions

    def get_transactions(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ):

        if end_date is None:
            end_date = date.today()

        if start_date is None:
            start_date = end_date - timedelta(days=365)

        response = self.breeze.get_trade_list(
            from_date=start_date.strftime("%Y-%m-%dT00:00:00.000Z"),
            to_date=end_date.strftime("%Y-%m-%dT00:00:00.000Z"),
            exchange_code="NSE",
            product_type="",
            action="",
            stock_code="",
        )

        trades = []

        for item in response.get("Success", []):

            trades.append(
                Transaction(
                    order_id=item["order_id"],
                    symbol=item["stock_code"],
                    order_type=(
                        OrderType.BUY
                        if item["action"].lower() == "buy"
                        else OrderType.SELL
                    ),
                    quantity=float(item["quantity"]),
                    price=float(item["average_cost"]),
                    order_date=datetime.strptime(
                        item["trade_date"],
                        "%d-%b-%Y",
                    ),
                )
            )

        return trades

    def get_cash(self) -> float:

        response = self.breeze.get_funds()

        funds = response.get(
            "Success",
            {},
        )

        return float(
            funds.get(
                "unallocated_balance",
                0,
            )
        )
    
    '''
    def login_url(self) -> str:
        raise NotImplementedError(
            "Authentication is handled by IciciAuth."
        )


    def authenticate(
        self,
        request_token: str | None = None,
    ) -> None:
        pass


    def logout(self) -> None:
        pass


    def is_authenticated(self) -> bool:
        return True
'''    
