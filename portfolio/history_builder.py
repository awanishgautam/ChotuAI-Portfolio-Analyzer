"""
Build historical portfolio value.

Assumption (MVP):
Current holdings existed for the entire history.

This is sufficient for computing risk metrics for a
personal dashboard. It ignores buys/sells over time.
"""

from __future__ import annotations

import pandas as pd
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.market_data_service import MarketDataService
from domain.enums import AssetType

logger = logging.getLogger(__name__)

class PortfolioHistoryBuilder:

    _history_cache: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
    _cache_ttl_seconds = 15 * 60

    def __init__(self):

        self.market = MarketDataService()
        self.components = pd.DataFrame()

    # -----------------------------------------------------

    def build(
        self,
        portfolio,
        period: str = "5y",
    ) -> pd.Series:
        """
        Returns a portfolio value time series.

        Index:
            Date

        Values:
            Total portfolio value
        """

        series_list = []

        mf_total = 0
        mf_success = 0
        mf_skipped = []

        holdings = list(portfolio)
        mf_total = sum(h.asset_type == AssetType.MUTUAL_FUND for h in holdings)

        def fetch(holding):
            key = (holding.asset_type.value, holding.display_name, period)
            cached = self._history_cache.get(key)
            if cached and time.monotonic() - cached[0] < self._cache_ttl_seconds:
                return cached[1]
            if holding.asset_type in {AssetType.EQUITY, AssetType.ETF}:
                history = self.market.history(holding.symbol, period=period)
            elif holding.asset_type == AssetType.MUTUAL_FUND:
                history = self.market.mutual_fund_history(holding, period=period)
            else:
                return None
            self._history_cache[key] = (time.monotonic(), history)
            return history

        workers = min(8, max(1, len(holdings)))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="price-history") as executor:
            futures = {executor.submit(fetch, holding): holding for holding in holdings}
            for future in as_completed(futures):
                holding = futures[future]
                try:
                    history = future.result()
                    if holding.asset_type == AssetType.MUTUAL_FUND and history is not None:
                        mf_success += 1
                except Exception as e:

                    if holding.asset_type == AssetType.MUTUAL_FUND:
                        mf_skipped.append(
                            (
                                holding.display_name,
                                str(e),
                            )
                        )
                    logger.warning("Skipping %s : %s", holding.display_name, e)
                    continue

                if history is None or history.empty:
                    logger.warning("Empty history for %s", holding.display_name)
                    continue

                close = history["Close"] * holding.quantity
                close.name = holding.display_name
                series_list.append(close)

        logger.info(
            "Mutual funds processed: %d/%d",
            mf_success,
            mf_total,
        )

        if mf_skipped:

            logger.warning("Skipped mutual funds:")

            for name, reason in mf_skipped:

                logger.warning(
                    "  %s -> %s",
                    name,
                    reason,
                )

        else:

            logger.info(
                "No mutual funds were skipped."
            )

        if not series_list:
            logger.info("Portfolio has no holdings.")
            return pd.DataFrame()

        #
        # Combine all holdings
        #

        portfolio_df = pd.concat(
            series_list,
            axis=1,
        )

        #
        # Sort by date
        #

        portfolio_df.sort_index(
            inplace=True,
        )

        #
        # Fill missing values with last available price.
        # This prevents artificial drops on weekends and holidays.
        #

        portfolio_df.ffill(
            inplace=True,
        )

        #
        # Ignore dates before a holding existed.
        #

        portfolio_df = portfolio_df.dropna(
            how="all"
        )
        self.components = portfolio_df.copy()

        #
        # Portfolio value
        #

        portfolio_value = portfolio_df.sum(
            axis=1,
        )

        if len(portfolio_value) < 30:

            raise ValueError(
                "Insufficient historical data for analytics."
            )

        portfolio_value.name = "Portfolio"

        return portfolio_value

    # -----------------------------------------------------

    def benchmark(
        self,
        period: str = "5y",
    ) -> pd.Series:

        return self.market.benchmark_series(
            period
        )
