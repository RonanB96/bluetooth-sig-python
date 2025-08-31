"""Environmental Sensing Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.apparent_wind_direction import (
    ApparentWindDirectionCharacteristic,
)
from ..characteristics.apparent_wind_speed import ApparentWindSpeedCharacteristic
from ..characteristics.dew_point import DewPointCharacteristic
from ..characteristics.heat_index import HeatIndexCharacteristic
from ..characteristics.humidity import HumidityCharacteristic
from ..characteristics.pressure import PressureCharacteristic
from ..characteristics.temperature import TemperatureCharacteristic
from ..characteristics.true_wind_direction import TrueWindDirectionCharacteristic
from ..characteristics.true_wind_speed import TrueWindSpeedCharacteristic
from ..characteristics.wind_chill import WindChillCharacteristic
from .base import BaseGattService


@dataclass
class EnvironmentalSensingService(BaseGattService):
    """Environmental Sensing Service implementation.

    Contains characteristics related to environmental data:
    - Temperature - Optional
    - Humidity - Optional
    - Pressure - Optional
    - Dew Point - Optional
    - Heat Index - Optional
    - Wind Chill - Optional
    - True Wind Speed - Optional
    - True Wind Direction - Optional
    - Apparent Wind Speed - Optional
    - Apparent Wind Direction - Optional
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Temperature": TemperatureCharacteristic,
            "Humidity": HumidityCharacteristic,
            "Pressure": PressureCharacteristic,
            "Dew Point": DewPointCharacteristic,
            "Heat Index": HeatIndexCharacteristic,
            "Wind Chill": WindChillCharacteristic,
            "True Wind Speed": TrueWindSpeedCharacteristic,
            "True Wind Direction": TrueWindDirectionCharacteristic,
            "Apparent Wind Speed": ApparentWindSpeedCharacteristic,
            "Apparent Wind Direction": ApparentWindDirectionCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {}  # All characteristics are optional
