"""Structured logging helpers using structlog."""
from __future__ import annotations

from logging.config import dictConfig
from pathlib import Path
from typing import Optional

import structlog


def configure_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Configure structlog with JSON output and optional file logging."""

    shared_handlers = ["default"]
    handler_defs = {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    }

    if log_file:
        handler_defs["file"] = {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": str(log_file),
        }
        shared_handlers.append("file")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                }
            },
            "handlers": handler_defs,
            "root": {
                "level": log_level,
                "handlers": shared_handlers,
            },
        }
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


__all__ = ["configure_logging"]
