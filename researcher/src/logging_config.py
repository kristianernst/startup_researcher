from __future__ import annotations

import copy
import logging
import os
from logging.config import dictConfig

_DEFAULT_LOGGING_CONFIG: dict[str, object] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


def configure_logging(level: str | int | None = None) -> None:
    """Configure application-wide logging safely.

    Calling this multiple times is safe and idempotent; the first caller sets up
    the root logger and subsequent callers return immediately.
    """

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    config = copy.deepcopy(_DEFAULT_LOGGING_CONFIG)

    env_level = level if level is not None else os.getenv("LOG_LEVEL", "INFO")
    if isinstance(env_level, str):
        numeric_level = getattr(logging, env_level.upper(), logging.INFO)
    else:
        numeric_level = int(env_level)

    level_name = logging.getLevelName(numeric_level)

    config_root = config["root"]  # type: ignore[assignment]
    if isinstance(config_root, dict):
        config_root["level"] = level_name

    config_handlers = config["handlers"]  # type: ignore[assignment]
    if isinstance(config_handlers, dict):
        for handler in config_handlers.values():
            if isinstance(handler, dict):
                handler["level"] = level_name

    dictConfig(config)  # type: ignore[arg-type]


__all__ = ["configure_logging"]
