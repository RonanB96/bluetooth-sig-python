"""Sensor translation for GATT characteristics."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

from .uuid_registry import UuidRegistry


class DeviceClass(Enum):
    """Device classes for Home Assistant sensors."""

    BATTERY = "battery"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"


class StateClass(Enum):
    """State classes for Home Assistant sensors."""

    MEASUREMENT = "measurement"


@dataclass
class SensorInfo:
    """Information about a sensor characteristic."""

    name: str
    device_class: DeviceClass
    state_class: StateClass
    unit_of_measurement: Optional[str] = None
    suggested_display_precision: Optional[int] = None


class GattSensorTranslator:  # pylint: disable=too-few-public-methods
    """Translator for GATT characteristics to Home Assistant sensors."""

    def __init__(self):
        """Initialize the translator."""
        self._registry = UuidRegistry()

    def get_sensor_characteristics(self) -> Dict[str, Tuple[str, SensorInfo]]:
        """Get all sensor characteristics and their information.

        Returns:
            Dict mapping UUID to tuple of (characteristic name, sensor info)
        """
        sensors = {}

        # Battery Level
        battery_uuid = "2A19"
        battery_info = self._registry.get_characteristic_info(battery_uuid)
        if battery_info:
            sensors[battery_uuid] = (
                battery_info.name,
                SensorInfo(
                    name=battery_info.name,
                    device_class=DeviceClass.BATTERY,
                    state_class=StateClass.MEASUREMENT,
                    unit_of_measurement="%",
                    suggested_display_precision=0,
                ),
            )

        # Temperature
        temp_uuid = "2A6E"
        if temp_info := self._registry.get_characteristic_info(temp_uuid):
            sensors[temp_uuid] = (
                temp_info.name,
                SensorInfo(
                    name=temp_info.name,
                    device_class=DeviceClass.TEMPERATURE,
                    state_class=StateClass.MEASUREMENT,
                    unit_of_measurement="°C",
                    suggested_display_precision=1,
                ),
            )

        # Humidity
        humidity_uuid = "2A6F"
        humidity_info = self._registry.get_characteristic_info(humidity_uuid)
        if humidity_info:
            sensors[humidity_uuid] = (
                humidity_info.name,
                SensorInfo(
                    name=humidity_info.name,
                    device_class=DeviceClass.HUMIDITY,
                    state_class=StateClass.MEASUREMENT,
                    unit_of_measurement="%",
                    suggested_display_precision=1,
                ),
            )

        # Pressure
        pressure_uuid = "2A6D"
        pressure_info = self._registry.get_characteristic_info(pressure_uuid)
        if pressure_info:
            sensors[pressure_uuid] = (
                pressure_info.name,
                SensorInfo(
                    name=pressure_info.name,
                    device_class=DeviceClass.PRESSURE,
                    state_class=StateClass.MEASUREMENT,
                    unit_of_measurement="hPa",
                    suggested_display_precision=1,
                ),
            )

        return sensors


# Create a global instance for convenience
gatt_sensor_translator = GattSensorTranslator()
