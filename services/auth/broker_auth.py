from abc import ABC, abstractmethod

class BrokerAuth(ABC):

    @property
    @abstractmethod
    def login_url(self) -> str:
        ...

    @abstractmethod
    def exchange_request_token(
        self,
        request_token: str,
    ) -> str:
        ...

    @abstractmethod
    def authenticate_from_callback(
        self,
        query_params,
    ) -> str | None:
        """
        Reads the callback parameters and returns
        an access token if authentication succeeded.

        Returns None if the callback hasn't happened yet.
        """
        ...

    @abstractmethod
    def verify(
        self,
        access_token: str,
    ) -> bool:
        ...