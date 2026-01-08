from logging.config import dictConfig

from .config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure logging."""
    handlers = ["stdout", "rotating_file"]

    if (
        settings.ENV_STATE == "prod"
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
                "uuid_length": 8 if settings.ENV_STATE == "dev" else 32,
                "default_value": "-",
            }
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
                "source_token": settings.LOGTAIL_TOKEN,
                "host": settings.LOGTAIL_HOST,
            },
        },
        "loggers": {
            "api": {
                "handlers": handlers,
                "level": "DEBUG" if settings.ENV_STATE == "dev" else "INFO",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
