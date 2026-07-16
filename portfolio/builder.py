"""
builder.py

Converts broker-specific holdings into the internal
Portfolio domain model.

This module knows how to translate Zerodha's API
response into Portfolio/Holding objects.

No dependency on Streamlit or AI.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .portfolio import Portfolio
from portfolio.models import AssetHolding, Position


class PortfolioBuilder:
    """
    Factory for building Portfolio objects from
    broker API responses.
    """

    def __init__(
        self,
        owner: str = "User",
        benchmark: str = "NIFTY 50",
    ):

        self.owner = owner
        self.benchmark = benchmark

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------
    def build(
        self,
        *,
        holdings: list[AssetHolding],
        positions: list[Position],
        cash: float,
    ) -> Portfolio:

        return Portfolio(
            owner=self.owner,
            benchmark=self.benchmark,
            holdings=holdings,
            positions=positions,
            cash=cash,
        )
    
    def from_holdings(
    self,
    holdings: list[AssetHolding],
) -> Portfolio:
        """
        Build a Portfolio from Holding objects returned by
        ZerodhaProvider.
        """

        portfolio = Portfolio(
            owner=self.owner,
            benchmark=self.benchmark,
        )

        portfolio.extend(holdings)

        return portfolio
        # -------------------------------------------------

    def from_positions(
            self,
            positions: Iterable[dict[str, Any]],
        ) -> Portfolio:
            """
            Convert Kite positions() response into
            a Portfolio.

            Useful for intraday/F&O positions.
            """

            portfolio = Portfolio(
                owner=self.owner,
                benchmark=self.benchmark,
            )

            for item in positions:

                quantity = float(
                    item.get("quantity", 0)
                )

                if quantity == 0:
                    continue

                portfolio.add(
                    Holding(
                        symbol=item.get(
                            "tradingsymbol",
                            "",
                        ),
                        exchange=item.get(
                            "exchange",
                            "NSE",
                        ),
                        quantity=quantity,
                        average_price=float(
                            item.get(
                                "average_price",
                                0,
                            )
                        ),
                        last_price=float(
                            item.get(
                                "last_price",
                                0,
                            )
                        ),
                        instrument_token=item.get(
                            "instrument_token"
                        ),
                        product=item.get(
                            "product",
                            "",
                        ),
                    )
                )

            return portfolio

    # -------------------------------------------------

    def from_dataframe(
        self,
        df,
    ) -> Portfolio:
        """
        Convert a pandas DataFrame into Portfolio.

        Required columns:

            Symbol
            Quantity
            Average Price
            Last Price
        """

        portfolio = Portfolio(
            owner=self.owner,
            benchmark=self.benchmark,
        )

        for _, row in df.iterrows():

            portfolio.add(
                Holding(
                    symbol=row["Symbol"],
                    exchange=row.get(
                        "Exchange",
                        "NSE",
                    ),
                    quantity=float(
                        row["Quantity"]
                    ),
                    average_price=float(
                        row["Average Price"]
                    ),
                    last_price=float(
                        row["Last Price"]
                    ),
                )
            )

        return portfolio

    # -------------------------------------------------

    def empty(self) -> Portfolio:
        """
        Return an empty Portfolio.
        """

        return Portfolio(
            owner=self.owner,
            benchmark=self.benchmark,
        )
