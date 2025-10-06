"""Environmental Sensing Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class EnvironmentalSensingService(BaseGattService):
    """Environmental Sensing Service implementation (0x181A).

    Used for environmental monitoring devices including weather stations,
    air quality sensors, and comprehensive environmental monitoring systems.
    Supports a wide range of environmental measurements including:
    - Traditional weather measurements (temperature, humidity, pressure)
    - Air quality metrics (gas concentrations, particulate matter)
    - Advanced environmental conditions (wind, elevation, trends)

    Contains comprehensive characteristics for environmental sensing including:
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
    - CO2 Concentration - Optional
    - VOC Concentration - Optional
    - Non-Methane VOC Concentration - Optional
    - Ammonia Concentration - Optional
    - Methane Concentration - Optional
    - Nitrogen Dioxide Concentration - Optional
    - Ozone Concentration - Optional
    - PM1 Concentration - Optional
    - PM2.5 Concentration - Optional
    - PM10 Concentration - Optional
    - Sulfur Dioxide Concentration - Optional
    - Elevation - Optional
    - Barometric Pressure Trend - Optional
    - Pollen Concentration - Optional
    - Rainfall - Optional
    """

    # All characteristics are optional in this service
    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        # Traditional environmental sensors
        CharacteristicName.TEMPERATURE: False,
        CharacteristicName.HUMIDITY: False,
        CharacteristicName.PRESSURE: False,
        CharacteristicName.DEW_POINT: False,
        CharacteristicName.HEAT_INDEX: False,
        CharacteristicName.WIND_CHILL: False,
        CharacteristicName.TRUE_WIND_SPEED: False,
        CharacteristicName.TRUE_WIND_DIRECTION: False,
        CharacteristicName.APPARENT_WIND_SPEED: False,
        CharacteristicName.APPARENT_WIND_DIRECTION: False,
        # Gas sensor characteristics for air quality monitoring
        CharacteristicName.CO2_CONCENTRATION: False,
        CharacteristicName.VOC_CONCENTRATION: False,
        CharacteristicName.NON_METHANE_VOC_CONCENTRATION: False,
        CharacteristicName.AMMONIA_CONCENTRATION: False,
        CharacteristicName.METHANE_CONCENTRATION: False,
        CharacteristicName.NITROGEN_DIOXIDE_CONCENTRATION: False,
        CharacteristicName.OZONE_CONCENTRATION: False,
        CharacteristicName.PM1_CONCENTRATION: False,
        CharacteristicName.PM25_CONCENTRATION: False,
        CharacteristicName.PM10_CONCENTRATION: False,
        CharacteristicName.SULFUR_DIOXIDE_CONCENTRATION: False,
        # Environmental condition characteristics
        CharacteristicName.ELEVATION: False,
        CharacteristicName.BAROMETRIC_PRESSURE_TREND: False,
        CharacteristicName.POLLEN_CONCENTRATION: False,
        CharacteristicName.RAINFALL: False,
    }
