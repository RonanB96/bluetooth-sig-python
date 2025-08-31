"""Environmental Sensing Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics.temperature import TemperatureCharacteristic
from ..characteristics.humidity import HumidityCharacteristic
from ..characteristics.pressure import PressureCharacteristic
from ..characteristics.uv_index import UVIndexCharacteristic
from ..characteristics.sensors import (
    IlluminanceCharacteristic, 
    SoundLevelCharacteristic,
    CarbonMonoxideConcentrationCharacteristic,
    PM25ConcentrationCharacteristic,
    ApparentWindDirectionCharacteristic,
    ApparentWindSpeedCharacteristic,
)


@dataclass
class EnvironmentalSensingService(BaseGattService):
    """Environmental Sensing Service implementation.

    Contains characteristics related to environmental data:
    - Temperature - Optional
    - Humidity - Optional
    - Pressure - Optional
    - UV Index - Optional
    - Illuminance - Optional
    - Sound Pressure Level - Optional
    - Carbon Monoxide Concentration - Optional
    - PM2.5 Concentration - Optional
    - Apparent Wind Direction - Optional
    - Apparent Wind Speed - Optional
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Temperature": TemperatureCharacteristic,
            "Humidity": HumidityCharacteristic,
            "Pressure": PressureCharacteristic,
            "UV Index": UVIndexCharacteristic,
            "Illuminance": IlluminanceCharacteristic,
            "Sound Pressure Level": SoundLevelCharacteristic,
            "Carbon Monoxide Concentration": CarbonMonoxideConcentrationCharacteristic,
            "PM2.5 Concentration": PM25ConcentrationCharacteristic,
            "Apparent Wind Direction": ApparentWindDirectionCharacteristic,
            "Apparent Wind Speed": ApparentWindSpeedCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {}  # All characteristics are optional
