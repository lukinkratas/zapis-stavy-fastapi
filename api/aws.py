import logging
import os
from functools import lru_cache
from typing import Any, Callable

from boto3 import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from .utils import log_func

logger = logging.getLogger(__name__)
load_dotenv()

session = Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION_NAME"],
)


@lru_cache
def get_ses_client() -> BaseClient:
    """Lazy init ses client."""
    return session.client("ses")


@lru_cache
def get_logs_client() -> BaseClient:
    """Lazy init cloudwatch logs client."""
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
