from brokers.types import BrokerType

class AuthFactory:

    @staticmethod
    def create(
        broker: BrokerType,
    ):

        if broker == BrokerType.ZERODHA:
            from services.auth.zerodha_auth import ZerodhaAuth

            return ZerodhaAuth()

        if broker == BrokerType.ICICI_DIRECT:
            from services.auth.icici_auth import IciciAuth

            return IciciAuth()

        raise ValueError(
            f"Unsupported broker: {broker}"
        )
