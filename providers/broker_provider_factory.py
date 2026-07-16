from providers.icici_provider import ICICIDirectProvider
from providers.zerodha_provider import ZerodhaProvider
from brokers import BrokerType


class ProviderFactory:

    @staticmethod
    def create(
        broker: str,
        access_token: str,
    ):

        broker = broker.lower()

        if broker == BrokerType.ZERODHA:

            return ZerodhaProvider(
                access_token,
            )

        if broker == BrokerType.ICICI_DIRECT:

            return ICICIDirectProvider(
                access_token,
            )

#        if broker == BrokerType.MOCK:

        raise ValueError(
            f"Unsupported broker: {broker}"
        )