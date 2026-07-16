from __future__ import annotations

from domain.instrument import Instrument

from .base import InstrumentRepository


class MemoryInstrumentRepository(
    InstrumentRepository,
):
    """
    In-memory implementation.

    Later we'll replace this with PostgreSQL.
    """

    def __init__(self):

        self._cache: dict[
            str,
            Instrument,
        ] = {}

    def save(
        self,
        instrument: Instrument,
    ) -> None:

        self._cache[
            instrument.symbol.upper()
        ] = instrument

    def get(
        self,
        symbol: str,
    ) -> Instrument | None:

        return self._cache.get(
            symbol.upper()
        )

    def exists(
        self,
        symbol: str,
    ) -> bool:

        return symbol.upper() in self._cache

    def all(
        self,
    ) -> list[Instrument]:

        return sorted(
            self._cache.values(),
            key=lambda x: x.symbol,
        )

    def delete(
        self,
        symbol: str,
    ) -> None:

        self._cache.pop(
            symbol.upper(),
            None,
        )