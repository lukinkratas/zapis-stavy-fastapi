import logging
from functools import lru_cache
from typing import Any, Callable

from boto3 import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .config import get_aws_settings
from .utils import log_func

logger = logging.getLogger(__name__)


@lru_cache
def get_session() -> BaseClient:
    """Lazy init session."""
    aws_settings = get_aws_settings()
    return Session(
        aws_access_key_id=aws_settings.access_key_id,
        aws_secret_access_key=aws_settings.secret_access_key,
        region_name=aws_settings.region_name,
    )


@lru_cache
def get_ses_client() -> BaseClient:
    """Lazy init ses client."""
    session = get_session()
    return session.client("ses")


@lru_cache
def get_logs_client() -> BaseClient:
    """Lazy init cloudwatch logs client."""
    session = get_session()
    return session.client("logs")


def _request(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Wrap boto function in try-except block."""
    try:
        response = func(*args, **kwargs)

    except ClientError as e:
        logging.error(e)
        raise e

    return response


@log_func(logger.debug)
def ses_send_email(email: str, message: dict[str, Any]) -> str:
    """Send email via SES service."""
    ses_client = get_ses_client()
    return _request(
        ses_client.send_email,
        Source="lukin.kratas@seznam.cz",  # must be verified
        Destination={"ToAddresses": [email]},
        Message=message,
    )
