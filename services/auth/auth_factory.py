from brokers.types import BrokerType

from services.auth.zerodha_auth import ZerodhaAuth

from services.auth.icici_auth import IciciAuth


class AuthFactory:

    @staticmethod
    def create(
        broker: BrokerType,
    ):

        if broker == BrokerType.ZERODHA:

            return ZerodhaAuth()

        if broker == BrokerType.ICICI_DIRECT:

            return IciciAuth()

        raise ValueError(
            f"Unsupported broker: {broker}"
        )