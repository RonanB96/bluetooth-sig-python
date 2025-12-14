"""Indoor Positioning Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class IndoorPositioningService(BaseGattService):
    """Indoor Positioning Service implementation.

    Contains characteristics related to indoor positioning:
    - Latitude - Mandatory
    - Longitude - Mandatory
    - Local North Coordinate - Optional
    - Local East Coordinate - Optional
    - Floor Number - Optional
    - Altitude - Optional
    - Uncertainty - Optional
    - Location Name - Optional
    - Indoor Positioning Configuration - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.LATITUDE: True,  # mandatory
        CharacteristicName.LONGITUDE: True,  # mandatory
        CharacteristicName.FLOOR_NUMBER: False,  # optional
        CharacteristicName.LOCATION_NAME: False,  # optional
        CharacteristicName.INDOOR_POSITIONING_CONFIGURATION: False,  # optional
        CharacteristicName.LOCAL_NORTH_COORDINATE: False,  # optional
        CharacteristicName.LOCAL_EAST_COORDINATE: False,  # optional
        CharacteristicName.ALTITUDE: False,  # optional
        CharacteristicName.UNCERTAINTY: False,  # optional
    }
