from logging.config import dictConfig


def configure_logging() -> None:
    """Configure logging."""
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": (
                    "%(asctime)s | %(levelname)-8s | %(name)-12s | "
                    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
                ),
            },
            "simple": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "zapisstavyapi.log",
                "formatter": "detailed",
                "level": "DEBUG",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "zapisstavyapi": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
    dictConfig(cfg)
