import socket
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from .aws import get_logs_client
from .config import get_settings

LOG_DIR = Path("logs")


def configure_logging() -> None:
    """Configure logging."""
    settings = get_settings()
    filters: dict[str, Any] = {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 8 if settings.env == "dev" else 32,
            "default_value": "-",
        },
    }

    formatters: dict[str, Any] = {
        "simple": {
            "class": "logging.Formatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                "%(asctime)s | "
                "%(levelname)-8s | "
                "%(name)s | "
                "[%(correlation_id)s] %(message)s"
            ),
        },
        "detailed": {
            "class": "logging.Formatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                "%(asctime)s | "
                "%(levelname)-8s | "
                "%(name)s | "
                "%(filename)s:%(lineno)d | "
                "%(funcName)s | "
                "[%(correlation_id)s] %(message)s"
            ),
        },
        "json": {
            "class": "pythonjsonlogger.json.JsonFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": (
                "%(asctime)s"
                "%(levelname)s"
                "%(name)s"
                "%(filename)s"
                "%(lineno)d"
                "%(funcName)s"
                "%(correlation_id)s"
                "%(message)s"
            ),
        },
    }

    handlers: dict[str, Any] = {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "filters": ["correlation_id"],
            "formatter": "simple",
        }
    }
    active_handlers = ["stdout"]

    if settings.env == "dev":
        handlers["rotating_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "api.log"),
            "maxBytes": 2 * 1024 * 1024,  # 2MB
            "backupCount": 5,
            "encoding": "utf8",
            "level": "DEBUG",
            "filters": ["correlation_id"],
            "formatter": "json",
        }
        active_handlers.append("rotating_file")
        log_level = "DEBUG"

    elif settings.env == "test":
        log_level = "DEBUG"

    elif settings.env == "prod":
        handlers["watchtower"] = {
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": get_logs_client(),
            "log_group_name": "zapis-stavy",
            "log_stream_name": f"{settings.env}-{socket.gethostname()}",
            "create_log_group": False,  # terraform managed
            "level": "INFO",
            "filters": ["correlation_id"],
            "formatter": "simple",
        }
        active_handlers.append("watchtower")
        log_level = "INFO"

    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": filters,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": {
            "api": {
                "handlers": active_handlers,
                "level": log_level,
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
