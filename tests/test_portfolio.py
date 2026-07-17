from datetime import date

import pytest
from pydantic import ValidationError

from domain.enums import Exchange
from portfolio.builder import PortfolioBuilder
from portfolio.models import EquityHolding
from portfolio.portfolio_engine import PortfolioEngine


def holding(symbol: str, quantity: float, average: float, last: float) -> EquityHolding:
    return EquityHolding(name=symbol, symbol=symbol, exchange=Exchange.NSE,
        quantity=quantity, average_price=average, last_price=last,
        invested_value=quantity * average, current_value=quantity * last,
        pnl=quantity * (last - average), pnl_percent=((last / average) - 1) * 100)


def test_portfolio_metrics_allocation_and_summary() -> None:
    portfolio = PortfolioBuilder(owner="Ada", benchmark="NIFTY 50").from_holdings(
        [holding("AAA", 10, 100, 120), holding("BBB", 5, 200, 180)])
    assert portfolio.invested_value == 2000
    assert portfolio.market_value == 2100
    assert portfolio.pnl_percent == 5
    assert portfolio.allocation() == pytest.approx({"AAA": 1200 / 21, "BBB": 900 / 21})
    assert portfolio.summary()["date"] == date.today().isoformat()


def test_builder_preserves_metadata_positions_and_cash() -> None:
    portfolio = PortfolioBuilder(owner="Ada", benchmark="SENSEX").build(
        holdings=[holding("AAA", 1, 100, 110)], positions=[], cash=250)
    assert (portfolio.owner, portfolio.benchmark, portfolio.cash) == ("Ada", "SENSEX", 250)


def test_holding_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        holding("BAD", -1, 100, 100)


def test_portfolio_engine_can_skip_unused_account_calls() -> None:
    class Provider:
        def get_holdings(self):
            return [holding("AAA", 1, 100, 110)]

        def get_positions(self):
            raise AssertionError("positions should not be fetched")

        def get_cash(self):
            raise AssertionError("cash should not be fetched")

    portfolio = PortfolioEngine(Provider()).build(
        include_positions=False,
        include_cash=False,
    )
    assert len(portfolio.holdings) == 1
    assert portfolio.positions == []
    assert portfolio.cash == 0
