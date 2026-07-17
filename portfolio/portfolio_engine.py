from domain.enums import AssetType
from portfolio.builder import PortfolioBuilder
from portfolio.portfolio import Portfolio
from brokers.base import BrokerProvider


class PortfolioEngine:
    """
    Builds a portfolio from the configured broker.
    """

    def __init__(
        self,
        provider: BrokerProvider,
    ):
        self.provider = provider

    def build(
        self,
        asset_type: AssetType | None = None,
        *,
        include_positions: bool = True,
        include_cash: bool = True,
    ) -> Portfolio:
        """
        Build a portfolio.

        asset_type=None -> All assets
        asset_type=EQUITY -> Equity only
        asset_type=MUTUAL_FUND -> Mutual Funds only
        """
        if asset_type is AssetType.EQUITY:
            holdings = self.provider.get_equity_holdings()
        elif asset_type is AssetType.MUTUAL_FUND:
            holdings = self.provider.get_mutual_fund_holdings()
        else:
            holdings = self.provider.get_holdings()

        if asset_type is not None:

            holdings = [
                holding
                for holding in holdings
                if holding.asset_type == asset_type
            ]
        
        positions = self.provider.get_positions() if include_positions else []

        cash = self.provider.get_cash() if include_cash else 0.0

        return PortfolioBuilder().build(
            holdings=holdings,
            positions=positions,
            cash=cash,
        )
