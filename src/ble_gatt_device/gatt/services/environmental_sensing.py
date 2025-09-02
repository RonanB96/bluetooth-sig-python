"""Environmental Sensing Service implementation."""

from dataclasses import dataclass

from ..characteristics.ammonia_concentration import AmmoniaConcentrationCharacteristic
from ..characteristics.apparent_wind_direction import (
    ApparentWindDirectionCharacteristic,
)
from ..characteristics.apparent_wind_speed import ApparentWindSpeedCharacteristic
from ..characteristics.barometric_pressure_trend import (
    BarometricPressureTrendCharacteristic,
)
from ..characteristics.co2_concentration import CO2ConcentrationCharacteristic
from ..characteristics.dew_point import DewPointCharacteristic
from ..characteristics.elevation import ElevationCharacteristic
from ..characteristics.heat_index import HeatIndexCharacteristic
from ..characteristics.humidity import HumidityCharacteristic
from ..characteristics.methane_concentration import MethaneConcentrationCharacteristic
from ..characteristics.nitrogen_dioxide_concentration import (
    NitrogenDioxideConcentrationCharacteristic,
)
from ..characteristics.ozone_concentration import OzoneConcentrationCharacteristic
from ..characteristics.pm1_concentration import PM1ConcentrationCharacteristic
from ..characteristics.pm10_concentration import PM10ConcentrationCharacteristic
from ..characteristics.pm25_concentration import PM25ConcentrationCharacteristic
from ..characteristics.pollen_concentration import PollenConcentrationCharacteristic
from ..characteristics.pressure import PressureCharacteristic
from ..characteristics.rainfall import RainfallCharacteristic
from ..characteristics.sulfur_dioxide_concentration import (
    SulfurDioxideConcentrationCharacteristic,
)
from ..characteristics.temperature import TemperatureCharacteristic
from ..characteristics.true_wind_direction import TrueWindDirectionCharacteristic
from ..characteristics.true_wind_speed import TrueWindSpeedCharacteristic
from ..characteristics.tvoc_concentration import TVOCConcentrationCharacteristic
from ..characteristics.wind_chill import WindChillCharacteristic
from .base import BaseGattService


@dataclass
class EnvironmentalSensingService(BaseGattService):
    """Environmental Sensing Service implementation.

    Contains characteristics related to environmental and air quality data:
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
    - CO\\textsubscript{2} Concentration - Optional
    - TVOC Concentration - Optional
    - Ammonia Concentration - Optional
    - Methane Concentration - Optional
    - Nitrogen Dioxide Concentration - Optional
    - Ozone Concentration - Optional
    - PM1 Concentration - Optional
    - PM2.5 Concentration - Optional
    - PM10 Concentration - Optional
    - Sulfur Dioxide Concentration - Optional
    """

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            # Traditional environmental sensors
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
            # Gas sensor characteristics for air quality monitoring
            "CO\\textsubscript{2} Concentration": CO2ConcentrationCharacteristic,
            "VOC Concentration": TVOCConcentrationCharacteristic,
            "Ammonia Concentration": AmmoniaConcentrationCharacteristic,
            "Methane Concentration": MethaneConcentrationCharacteristic,
            "Nitrogen Dioxide Concentration": NitrogenDioxideConcentrationCharacteristic,
            "Ozone Concentration": OzoneConcentrationCharacteristic,
            "Particulate Matter - PM1 Concentration": PM1ConcentrationCharacteristic,
            "Particulate Matter - PM2.5 Concentration": PM25ConcentrationCharacteristic,
            "Particulate Matter - PM10 Concentration": PM10ConcentrationCharacteristic,
            "Sulfur Dioxide Concentration": SulfurDioxideConcentrationCharacteristic,
            # Environmental condition characteristics
            "Elevation": ElevationCharacteristic,
            "Barometric Pressure Trend": BarometricPressureTrendCharacteristic,
            "Pollen Concentration": PollenConcentrationCharacteristic,
            "Rainfall": RainfallCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {}  # All characteristics are optional
