"""Blood Pressure Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BloodPressureService(BaseGattService):
    """Blood Pressure Service implementation.

    Contains characteristics related to blood pressure measurement:
    - Blood Pressure Measurement - Required
    - Intermediate Cuff Pressure - Optional
    - Blood Pressure Feature - Optional
    """

    _service_name: str = "Blood Pressure"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BLOOD_PRESSURE_MEASUREMENT: True,
        CharacteristicName.INTERMEDIATE_CUFF_PRESSURE: False,
        CharacteristicName.BLOOD_PRESSURE_FEATURE: True,
        CharacteristicName.BLOOD_PRESSURE_RECORD: False,
        CharacteristicName.RECORD_ACCESS_CONTROL_POINT: False,
        CharacteristicName.ENHANCED_BLOOD_PRESSURE_MEASUREMENT: False,
        CharacteristicName.ENHANCED_INTERMEDIATE_CUFF_PRESSURE: False,
    }
