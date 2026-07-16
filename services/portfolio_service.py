from __future__ import annotations

from services.interfaces import PortfolioProvider


class PortfolioService:

    """
    Facade used by the UI.

    UI never calls Zerodha directly.
    """

    def __init__(
        self,
        provider: PortfolioProvider,
    ):
        self.provider = provider

    def authenticate(self):

        self.provider.authenticate()

    def get_portfolio(self):

        return self.provider.get_portfolio()

    def get_holdings(self):

        return self.provider.get_holdings()

    def get_transactions(self):

        return self.provider.get_transactions()