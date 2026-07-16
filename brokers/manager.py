from __future__ import annotations

from brokers.base import BrokerProvider


class BrokerManager:
    """
    Keeps the currently selected broker.

    Later this class can manage multiple brokers.
    """

    def __init__(self):

        self._provider: BrokerProvider | None = None

    def register(
        self,
        provider: BrokerProvider,
    ) -> None:

        self._provider = provider

    @property
    def provider(self) -> BrokerProvider:

        if self._provider is None:
            raise RuntimeError(
                "Broker not configured."
            )

        return self._provider

    def authenticated(self) -> bool:
        return self.provider.is_authenticated()

    def portfolio(self):
        return self.provider.get_portfolio()

    def holdings(self):
        return self.provider.get_holdings()

    def positions(self):
        return self.provider.get_positions()

    def transactions(self):
        return self.provider.get_transactions()