from enum import Enum


class BrokerType(str, Enum):
    ZERODHA = "zerodha"
    ICICI_DIRECT = "icici_direct"
    MOCK = "mock"