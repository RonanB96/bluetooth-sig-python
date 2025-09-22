"""Health Thermometer Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class HealthThermometerService(BaseGattService):
    """Health Thermometer Service implementation (0x1809).

    Used for medical temperature measurement devices.
    Contains the Temperature Measurement characteristic for medical-grade temperature readings.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TEMPERATURE_MEASUREMENT: True,  # required
    }
