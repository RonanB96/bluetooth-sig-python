"""Location and Navigation Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class LocationAndNavigationService(BaseGattService):
    """Location and Navigation Service implementation.

    Contains characteristics related to location and navigation data:
    - LN Feature - Required
    - Location and Speed - Optional
    - Navigation - Optional
    - Position Quality - Optional
    - LN Control Point - Optional
    """

    _service_name: str = "Location and Navigation"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.LN_FEATURE: True,
        CharacteristicName.LOCATION_AND_SPEED: False,
        CharacteristicName.NAVIGATION: False,
        CharacteristicName.POSITION_QUALITY: False,
        CharacteristicName.LN_CONTROL_POINT: False,
    }
