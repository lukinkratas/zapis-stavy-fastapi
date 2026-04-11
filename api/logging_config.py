import os
from logging.config import dictConfig

from dotenv import load_dotenv

load_dotenv(override=True)

ENV = os.getenv("ENV", "dev")
LOGTAIL_TOKEN = os.getenv("LOGTAIL_TOKEN")
LOGTAIL_HOST = os.getenv("LOGTAIL_HOST")


def configure_logging() -> None:
    """Configure logging."""
    handlers = ["stdout", "rotating_file"]

    if ENV == "prod" and LOGTAIL_TOKEN is not None and LOGTAIL_HOST is not None:
        handlers.append("logtail")

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
                "formatter": "simple",
                "level": "DEBUG",
                "filters": ["correlation_id"],
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "api.log",
                "formatter": "json",
                "level": "DEBUG",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["correlation_id"],
            },
            "logtail": {
                "class": "logtail.LogtailHandler",
                "formatter": "simple",
                "level": "INFO",
                "filters": ["correlation_id"],
                "source_token": LOGTAIL_TOKEN,
                "host": LOGTAIL_HOST,
            },
        },
        "loggers": {
            "api": {
                "handlers": handlers,
                "level": "DEBUG" if ENV == "dev" else "INFO",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
