import logging
from functools import lru_cache
from typing import Any, Callable

from boto3 import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .utils import log_func

logger = logging.getLogger(__name__)
session = Session()


@lru_cache
def _get_ses_client(session: Session) -> BaseClient:
    """Lazy init ses client."""
    return session.client("ses")


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
    ses_client = _get_ses_client(session)
    return _request(
        ses_client.send_email,
        Source="lukin.kratas@seznam.cz",  # must be verified
        Destination={"ToAddresses": [email]},
        Message=message,
    )
