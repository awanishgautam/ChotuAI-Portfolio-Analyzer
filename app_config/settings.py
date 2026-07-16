from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    """
    Global application configuration.

    Loads application configuration from the project-local ``.env`` file.

    Process environment variables are intentionally not used for settings or
    credentials, which prevents shell/IDE configuration from overriding the
    checked project configuration source.
    """

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Use only explicit values and the project ``.env`` file."""

        return init_settings, dotenv_settings, file_secret_settings

    # -------------------------
    # Application
    # -------------------------

    app_name: str = "Portfolio AI"

    environment: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    debug: bool = True

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    # -------------------------
    # OpenAI
    # -------------------------

    openai_api_key: SecretStr | None = None

    openai_model: str = "gpt-5"

    # -------------------------
    # Zerodha
    # -------------------------

    zerodha_api_key: str | None = None

    zerodha_api_secret: SecretStr | None = None

    icici_api_key: SecretStr

    icici_api_secret: SecretStr

    redirect_url: str = "http://localhost:8501"
 
    # -------------------------
    # Portfolio
    # -------------------------

    benchmark_symbol: str = "NIFTYBEES"

    risk_free_rate: float = 0.07

    trading_days: int = 252

    # -------------------------
    # UI
    # -------------------------

    page_title: str = "Zerodha_Portfolio_AI"

    page_icon: str = "📈"

    layout: Literal[
        "wide",
        "centered",
    ] = "wide"

    # -------------------------
    # Helpers
    # -------------------------

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"

    @property
    def is_prod(self) -> bool:
        return self.environment == "production"

    @property
    def has_openai(self) -> bool:
        return self.openai_api_key is not None

    @property
    def has_zerodha(self) -> bool:
        return (
            self.zerodha_api_key is not None
            and self.zerodha_api_secret is not None
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


try:
    settings = get_settings()

except ValidationError as exc:
    raise RuntimeError(
        f"Configuration error:\n{exc}"
    ) from exc
