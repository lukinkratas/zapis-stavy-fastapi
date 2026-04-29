import socket
import os
from logging.config import dictConfig
from pathlib import Path

from dotenv import load_dotenv

from .aws import get_logs_client
load_dotenv(override=True)

ENV = os.getenv("ENV", "dev")
LOG_DIR = Path("logs")

def configure_logging() -> None:
    """Configure logging."""
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8 if ENV == "dev" else 32,
                "default_value": "-",
            },
        },
        "formatters": {
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
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
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
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "filters": ["correlation_id"],
                "formatter": "simple",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(LOG_DIR / "api.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
                "level": "DEBUG",
                "filters": ["correlation_id"],
                "formatter": "json",
            },
            "watchtower": {
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_client": get_logs_client(),
                "log_group_name": "zapis-stavy",
                "log_stream_name": f"{ENV}-{socket.gethostname()}",
                "create_log_group": False, # terraform managed
                "level": "INFO",
                "filters": ["correlation_id"],
                "formatter": "simple",
            }
        },
        "loggers": {
            "api": {
                "handlers": ["stdout", "rotating_file", "watchtower"],
                "level": "DEBUG" if ENV == "dev" else "INFO",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
