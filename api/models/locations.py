import logging

from .base import BaseTable

logger = logging.getLogger(__name__)


class LocationsTable(BaseTable):
    """Locations database model."""

    def __init__(self) -> None:
        super().__init__(table="locations")


locations_table = LocationsTable()
