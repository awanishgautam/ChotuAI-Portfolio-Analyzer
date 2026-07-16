from __future__ import annotations

from domain import AssetType, Exchange
from domain.instrument import Instrument

from .memory_repository import (
    MemoryInstrumentRepository,
)


class InstrumentService:
    """
    High-level repository service.

    Streamlit/FastAPI talks to this class,
    not directly to the repository.
    """

    def __init__(self):

        self.repo = (
            MemoryInstrumentRepository()
        )

    def register(
        self,
        symbol: str,
        name: str,
        exchange: Exchange,
        asset_type: AssetType,
        **kwargs,
    ) -> Instrument:

        inst = Instrument(
            symbol=symbol.upper(),
            name=name,
            exchange=exchange,
            asset_type=asset_type,
            **kwargs,
        )

        self.repo.save(inst)

        return inst

    def get(
        self,
        symbol: str,
    ) -> Instrument | None:

        return self.repo.get(symbol)

    def all(self):

        return self.repo.all()