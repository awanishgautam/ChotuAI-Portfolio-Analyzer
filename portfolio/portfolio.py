"""
portfolio.py

Core Portfolio domain model.

This module has NO dependency on:
    - Streamlit
    - FastAPI
    - Zerodha
    - Database

It is pure business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable
import pandas as pd
from pydantic import Field
from typing import Union

from portfolio.models import EquityHolding, MutualFundHolding, Position

Holding = Union[
    EquityHolding,
    MutualFundHolding,
]

# ==========================================================
# Portfolio
# ==========================================================

@dataclass(slots=True)
class Portfolio:

    owner: str = "User"

    benchmark: str = "NIFTY 50"

    as_of: date = field(default_factory=date.today)

    holdings: list[Holding] = field(
        default_factory=list
    )
    positions: list[Position] = field(default_factory=list)

    cash: float = 0

    # ------------------------------------------------------
    # Collection Helpers
    # ------------------------------------------------------

    def add(
        self,
        holding: Holding,
    ) -> None:

        self.holdings.append(
            holding
        )

    def extend(
        self,
        holdings: Iterable[Holding],
    ) -> None:

        self.holdings.extend(
            holdings
        )

    def remove(
        self,
        symbol: str,
    ) -> None:

        self.holdings = [
            h
            for h in self.holdings
            if h.symbol != symbol
        ]

    def get(
        self,
        symbol: str,
    ) -> Holding | None:

        for holding in self.holdings:

            if holding.symbol == symbol:
                return holding

        return None

    # ------------------------------------------------------
    # Portfolio Metrics
    # ------------------------------------------------------

    @property
    def invested_value(
        self,
    ) -> float:

        return sum(
            h.invested_value
            for h in self.holdings
        )

    @property
    def market_value(
        self,
    ) -> float:

        return sum(
            h.market_value
            for h in self.holdings
        )

    @property
    def pnl(
        self,
    ) -> float:

        return (
            self.market_value
            - self.invested_value
        )

    @property
    def pnl_percent(
        self,
    ) -> float:

        if self.invested_value == 0:
            return 0.0

        return (
            self.pnl
            / self.invested_value
            * 100
        )

    # ------------------------------------------------------
    # Allocation
    # ------------------------------------------------------

    def allocation(
        self,
    ) -> dict[str, float]:

        total = self.market_value

        if total == 0:
            return {}

        return {
            h.display_name: (
                h.current_value / total * 100
            )
            for h in self.holdings
        }

    # ------------------------------------------------------
    # Largest Holdings
    # ------------------------------------------------------

    def top_holdings(
        self,
        n: int = 10,
    ) -> list[Holding]:

        return sorted(
            self.holdings,
            key=lambda x: x.market_value,
            reverse=True,
        )[:n]

    # ------------------------------------------------------
    # DataFrame
    # ------------------------------------------------------

    def dataframe(
        self,
    ) -> pd.DataFrame:

        rows = []

        allocation = self.allocation()

        for h in self.holdings:

            row = {
                "Asset Type": h.asset_type.value,
                "Name": h.display_name,
                "Quantity": h.quantity,
                "Average Price": h.average_price,
                "Last Price": h.last_price,
                "Invested": round(
                    h.invested_value,
                    2,
                ),
                "Current Value": round(
                    h.current_value,
                    2,
                ),
                "PnL": round(
                    h.pnl,
                    2,
                ),
                "PnL %": round(
                    h.pnl_percent,
                    2,
                ),
                "Allocation %": round(
                    allocation.get(
                        h.display_name,
                        0,
                    ),
                    2,
                ),
            }

            if isinstance(h, EquityHolding):

                row["Symbol"] = h.display_name
                row["Exchange"] = h.exchange.value
                row["ISIN"] = h.isin
                row["Sector"] = h.sector

            elif isinstance(h, MutualFundHolding):

                row["Folio"] = h.folio
                row["XIRR"] = h.xirr
                row["AMC Symbol"] = h.display_name

            rows.append(row)

        df = pd.DataFrame(rows)

        if not df.empty:

            df = df.sort_values(
                "Current Value",
                ascending=False,
            )

        return df

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    def summary(
        self,
    ) -> dict:

        return {
            "owner": self.owner,
            "benchmark": self.benchmark,
            "date": self.as_of.isoformat(),
            "holdings": len(
                self.holdings
            ),
            "invested_value": round(
                self.invested_value,
                2,
            ),
            "market_value": round(
                self.market_value,
                2,
            ),
            "pnl": round(
                self.pnl,
                2,
            ),
            "pnl_percent": round(
                self.pnl_percent,
                2,
            ),
        }

    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(
            self.holdings
        )

    def __iter__(
        self,
    ):

        return iter(
            self.holdings
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"Portfolio("
            f"holdings={len(self)}, "
            f"value={self.market_value:,.2f})"
        )
