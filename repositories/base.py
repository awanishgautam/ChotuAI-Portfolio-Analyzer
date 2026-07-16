from __future__ import annotations

from abc import ABC, abstractmethod

from domain.instrument import Instrument


class InstrumentRepository(ABC):

    @abstractmethod
    def save(
        self,
        instrument: Instrument,
    ) -> None:
        ...

    @abstractmethod
    def get(
        self,
        symbol: str,
    ) -> Instrument | None:
        ...

    @abstractmethod
    def exists(
        self,
        symbol: str,
    ) -> bool:
        ...

    @abstractmethod
    def all(
        self,
    ) -> list[Instrument]:
        ...

    @abstractmethod
    def delete(
        self,
        symbol: str,
    ) -> None:
        ...