from logging.config import dictConfig

from .config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure logging."""
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8 if settings.ENV_STATE == "dev" else 32,
                "default_value": "-",
            }
        },
        "formatters": {
            "detailed": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)-8s | "
                    "%(name)s | "
                    "%(filename)s:%(lineno)d | "
                    "%(funcName)s | "
                    "[%(correlation_id)s] %(message)s"
                ),
            },
            "simple": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)-8s | "
                    "%(name)s | "
                    "[%(correlation_id)s] %(message)s"
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "filters": ["correlation_id"],
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "zapisstavyapi.log",
                "formatter": "detailed",
                "level": "DEBUG",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["correlation_id"],
            },
        },
        "loggers": {
            "zapisstavyapi": {
                "handlers": ["console", "rotating_file"],
                "level": "DEBUG" if settings.ENV_STATE == "dev" else "INFO",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
