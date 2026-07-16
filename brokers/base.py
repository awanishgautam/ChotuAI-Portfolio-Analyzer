from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from portfolio.portfolio import Portfolio
from portfolio.models import (
    AssetHolding,
    EquityHolding,
    MutualFundHolding,
    Transaction,
    Position
)

class BrokerProvider(ABC):
    """
    Base class for all broker implementations.
    """

    @abstractmethod
    def get_equity_holdings(
        self,
    ) -> list[EquityHolding]:
        ...

    @abstractmethod
    def get_mutual_fund_holdings(
        self,
    ) -> list[MutualFundHolding]:
        ...

    @abstractmethod
    def get_portfolio(self):
        ...
        
    @property
    @abstractmethod
    def broker_name(self) -> str:
        ...

    @abstractmethod
    def get_holdings(self) -> list[AssetHolding]:
        ...

    @abstractmethod
    def get_positions(self) -> list[Position]:
        ...

    @abstractmethod
    def get_cash(self) -> float:
        ...
        
    @abstractmethod
    def get_transactions(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        ...

    def get_portfolio(self) -> Portfolio:

        return Portfolio(
            holdings=self.get_holdings(),
            positions=self.get_positions(),
            transactions=self.get_transactions(),
            cash=self.get_cash(),
        )
    
'''
    @abstractmethod
    def login_url(self) -> str:
        ...

    @abstractmethod
    def authenticate(
        self,
        request_token: str,
    ) -> None:
        ...

    @abstractmethod
    def is_authenticated(self) -> bool:
        ...

    @abstractmethod
    def logout(self) -> None:
        ...
'''