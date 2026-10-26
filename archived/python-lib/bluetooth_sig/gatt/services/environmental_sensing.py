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
    - Advanced environmental conditions (wind, magnetic, elevation, trends)

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
    - Gust Factor - Optional
    - UV Index - Optional
    - Irradiance - Optional
    - Elevation - Optional
    - Barometric Pressure Trend - Optional
    - Pollen Concentration - Optional
    - Rainfall - Optional
    - Magnetic Declination - Optional
    - Magnetic Flux Density - 2D - Optional
    - Magnetic Flux Density - 3D - Optional
    - Ammonia Concentration - Optional
    - Carbon Monoxide Concentration - Optional
    - Methane Concentration - Optional
    - Nitrogen Dioxide Concentration - Optional
    - Non-Methane Volatile Organic Compounds Concentration - Optional
    - Ozone Concentration - Optional
    - Particulate Matter - PM1 Concentration - Optional
    - Particulate Matter - PM2.5 Concentration - Optional
    - Particulate Matter - PM10 Concentration - Optional
    - Sulfur Dioxide Concentration - Optional
    - Sulfur Hexafluoride Concentration - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.DESCRIPTOR_VALUE_CHANGED: False,
        # ESS Measurement permitted characteristics (at least one required if service is present)
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
        CharacteristicName.GUST_FACTOR: False,
        CharacteristicName.UV_INDEX: False,
        CharacteristicName.IRRADIANCE: False,
        # Environmental condition characteristics
        CharacteristicName.ELEVATION: False,
        CharacteristicName.BAROMETRIC_PRESSURE_TREND: False,
        CharacteristicName.POLLEN_CONCENTRATION: False,
        CharacteristicName.RAINFALL: False,
        CharacteristicName.MAGNETIC_DECLINATION: False,
        CharacteristicName.MAGNETIC_FLUX_DENSITY_2D: False,
        CharacteristicName.MAGNETIC_FLUX_DENSITY_3D: False,
        # Gas sensor characteristics for air quality monitoring
        CharacteristicName.AMMONIA_CONCENTRATION: False,
        CharacteristicName.CARBON_MONOXIDE_CONCENTRATION: False,
        CharacteristicName.METHANE_CONCENTRATION: False,
        CharacteristicName.NITROGEN_DIOXIDE_CONCENTRATION: False,
        CharacteristicName.NON_METHANE_VOC_CONCENTRATION: False,
        CharacteristicName.OZONE_CONCENTRATION: False,
        CharacteristicName.PM1_CONCENTRATION: False,
        CharacteristicName.PM25_CONCENTRATION: False,
        CharacteristicName.PM10_CONCENTRATION: False,
        CharacteristicName.SULFUR_DIOXIDE_CONCENTRATION: False,
        CharacteristicName.SULFUR_HEXAFLUORIDE_CONCENTRATION: False,
    }
