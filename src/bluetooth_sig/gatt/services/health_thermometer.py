"""Health Thermometer Service implementation."""

from dataclasses import dataclass

from ..characteristics.temperature_measurement import (
    TemperatureMeasurementCharacteristic,
)
from .base import BaseGattService


@dataclass
class HealthThermometerService(BaseGattService):
    """Health Thermometer Service implementation (0x1809).

    Used for medical temperature measurement devices.
    Contains the Temperature Measurement characteristic for medical-grade temperature readings.
    """

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Temperature Measurement": TemperatureMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Temperature Measurement": TemperatureMeasurementCharacteristic,
        }
