from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "portfolio_ai.log"

_LOGGER_INITIALIZED = False


def configure_logging(level: str = "INFO") -> None:
    """
    Configure application logging.

    Safe to call multiple times.
    """

    global _LOGGER_INITIALIZED

    if _LOGGER_INITIALIZED:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[console_handler, file_handler],
        force=True,
    )

    logging.captureWarnings(True)

    _LOGGER_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.
    """

    if not _LOGGER_INITIALIZED:
        configure_logging()

    return logging.getLogger(name)