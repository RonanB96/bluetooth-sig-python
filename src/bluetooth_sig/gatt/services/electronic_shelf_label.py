"""ElectronicShelfLabel Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ElectronicShelfLabelService(BaseGattService):
    """Electronic Shelf Label Service implementation (0x1857).

    Provides control and configuration of electronic shelf label
    (ESL) devices including display, LED, and sensor management.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ESL_ADDRESS: True,
        CharacteristicName.ESL_CONTROL_POINT: False,
        CharacteristicName.ESL_CURRENT_ABSOLUTE_TIME: False,
        CharacteristicName.ESL_DISPLAY_INFORMATION: False,
        CharacteristicName.ESL_IMAGE_INFORMATION: False,
        CharacteristicName.ESL_LED_INFORMATION: False,
        CharacteristicName.ESL_RESPONSE_KEY_MATERIAL: False,
        CharacteristicName.ESL_SENSOR_INFORMATION: False,
        CharacteristicName.AP_SYNC_KEY_MATERIAL: False,
    }
