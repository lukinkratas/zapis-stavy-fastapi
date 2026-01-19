import logging
from logging.config import dictConfig

from .config import Settings


def mask_email(email: str, masked_length: int) -> str:
    """Mask email - replace characters with stars."""
    name, domain = email.split("@")
    orig_chars = name[:masked_length]
    masked_chars = "*" * (len(name) - masked_length)
    return f"{orig_chars}{masked_chars}@{domain}"


class EmailMaskingFilter(logging.Filter):
    """Email masking used in logging filters."""

    def __init__(self, name: str = "", masked_length: int = 2) -> None:
        super().__init__(name)
        self.masked_length = masked_length

    def filter(self, record: logging.LogRecord) -> bool:
        """Mask logging records containing email."""
        if "email" in record.__dict__:
            record.email = mask_email(record.email, self.masked_length)
        return True


def configure_logging(settings: Settings) -> None:
    """Configure logging."""
    handlers = ["stdout", "rotating_file"]

    if (
        settings.ENV == "prod"
        and settings.LOGTAIL_TOKEN is not None
        and settings.LOGTAIL_HOST is not None
    ):
        handlers.append("logtail")

    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8 if settings.ENV == "dev" else 32,
                "default_value": "-",
            },
            "mask_email": {
                "()": EmailMaskingFilter,
                "masked_length": 2 if settings.ENV == "dev" else 0,
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
                "filters": ["correlation_id", "mask_email"],
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "api.log",
                "formatter": "json",
                "level": "DEBUG",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["correlation_id", "mask_email"],
            },
            "logtail": {
                "class": "logtail.LogtailHandler",
                "formatter": "simple",
                "level": "INFO",
                "filters": ["correlation_id", "mask_email"],
                "source_token": settings.LOGTAIL_TOKEN,
                "host": settings.LOGTAIL_HOST,
            },
        },
        "loggers": {
            "api": {
                "handlers": handlers,
                "level": "DEBUG" if settings.ENV == "dev" else "INFO",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
