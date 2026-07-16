class PortfolioException(Exception):
    """Base exception."""


class AuthenticationError(PortfolioException):
    """Authentication failed."""


class MarketDataError(PortfolioException):
    """Unable to fetch market data."""


class AnalyticsError(PortfolioException):
    """Analytics computation failed."""


class AIError(PortfolioException):
    """AI service failed."""