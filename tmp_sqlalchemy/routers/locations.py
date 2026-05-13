import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_confirmed_user
from ..db import get_db_session
from ..schemas import (
    BaseResponse,
    LocationCreateRequest,
    LocationUpdateRequest,
    ResponseWithId,
)
from ..services.locations import create_location, delete_location, update_location
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/location")


@router.post("", status_code=201, response_model=ResponseWithId)
@log_async_func(logger.info)
async def create(
    location: LocationCreateRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any] | None:
    """Add new location into the database.

    Args:
        location: location create request payload from client
        current_confirmed_user: current authorized and confirmed user

    Returns: location dict

    Raises:
        HTTPException: if location cannot be inserted in the database
    """
    created_location = await create_location(
        db_session, current_confirmed_user.id, **location.model_dump()
    )

    return {
        "detail": "Location created.",
        "id": str(created_location["id"]),
    }


@router.put("/{id}", response_model=BaseResponse)
@log_async_func(logger.info)
async def update(
    id: uuid.UUID,
    location: LocationUpdateRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any]:
    """Update a location in the database.

    Args:
        id: uuid of location
        location: location update request payload from client
        current_confirmed_user: current authorized and confirmed user

    Returns: location dict

    Raises:
        HTTPException: if location cannot be updated in the database
    """
    await update_location(
        db_session,
        id,
        current_confirmed_user.id,
        **location.model_dump(exclude_unset=True),
    )
    return {"detail": "Location updated"}


@router.delete("/{id}", response_model=BaseResponse)
@log_async_func(logger.info)
async def delete(
    id: uuid.UUID,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> None:
    """Delete a location from the database.

    Args:
        id: uuid of location
        current_confirmed_user: current authorized and confirmed user

    Returns: None

    Raises:
        HTTPException: if location cannot be deleted from the database
    """
    await delete_location(db_session, id, current_confirmed_user.id)
    return {"detail": "Location deleted"}
