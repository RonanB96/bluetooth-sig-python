"""Environmental Sensing Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics.temperature import TemperatureCharacteristic
from ..characteristics.humidity import HumidityCharacteristic
from ..characteristics.pressure import PressureCharacteristic


@dataclass
class EnvironmentalSensingService(BaseGattService):
    """Environmental Sensing Service implementation.

    Contains characteristics related to environmental data:
    - Temperature - Optional
    - Humidity - Optional
    - Pressure - Optional
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Temperature": TemperatureCharacteristic,
            "Humidity": HumidityCharacteristic,
            "Pressure": PressureCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {}  # All characteristics are optional
