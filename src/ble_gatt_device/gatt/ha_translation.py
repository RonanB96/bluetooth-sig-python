"""GATT to Home Assistant sensor translation layer.

This module demonstrates the proper architecture for Home Assistant integration.
The GATT layer provides only Bluetooth functionality + metadata properties.
This translation layer converts GATT data to Home Assistant-compatible format.
"""

from typing import Any, Dict

from .characteristics.base import BaseCharacteristic


class GATTSensorTranslator:
    """Translates GATT characteristic data to Home Assistant sensor format.

    This is the proper architecture pattern:
    - GATT Layer: Pure Bluetooth functionality + metadata properties
    - Translation Layer: Converts GATT data to HA format (THIS CLASS)
    - HA Integration Layer: Uses translation layer to create HA entities

    Dependencies flow: HA → Translation → GATT (never reverse)
    """

    @staticmethod
    def translate_to_ha_sensor(
        characteristic: BaseCharacteristic, raw_data: bytearray
    ) -> Dict[str, Any]:
        """Translate a GATT characteristic to Home Assistant sensor data.

        Args:
            characteristic: GATT characteristic instance
            raw_data: Raw BLE data from the characteristic

        Returns:
            Dict containing HA-compatible sensor data
        """
        try:
            # Parse value using GATT layer
            parsed_value = characteristic.parse_value(raw_data)

            # Extract metadata from GATT characteristic
            return {
                "value": parsed_value,
                "unit_of_measurement": characteristic.unit,
                "device_class": characteristic.device_class,
                "state_class": characteristic.state_class,
                "name": characteristic.name,
                "unique_id": f"ble_gatt_{characteristic.CHAR_UUID}",
                "attributes": {
                    "characteristic_uuid": characteristic.CHAR_UUID,
                    "characteristic_name": characteristic.name,
                    "characteristic_type": characteristic.value_type,
                },
            }
        except (ValueError, AttributeError, KeyError) as e:
            return {
                "value": None,
                "error": str(e),
                "characteristic_uuid": characteristic.CHAR_UUID,
                "characteristic_name": characteristic.name,
            }

    @staticmethod
    def get_sensor_configuration(characteristic: BaseCharacteristic) -> Dict[str, Any]:
        """Get Home Assistant sensor configuration for a GATT characteristic.

        Args:
            characteristic: GATT characteristic instance

        Returns:
            Dict containing HA sensor configuration
        """
        return {
            "name": characteristic.name,
            "unique_id": f"ble_gatt_{characteristic.CHAR_UUID}",
            "device_class": characteristic.device_class,
            "state_class": characteristic.state_class,
            "unit_of_measurement": characteristic.unit,
            "icon": GATTSensorTranslator._get_icon_for_device_class(
                characteristic.device_class
            ),
        }

    @staticmethod
    def _get_icon_for_device_class(device_class: str) -> str:
        """Get appropriate icon for Home Assistant device class."""
        icon_map = {
            "temperature": "mdi:thermometer",
            "humidity": "mdi:water-percent",
            "pressure": "mdi:gauge",
            "battery": "mdi:battery",
            "illuminance": "mdi:brightness-6",
            "heart_rate": "mdi:heart-pulse",
            "blood_oxygen": "mdi:lungs",
            "sound_pressure": "mdi:volume-high",
            "speed": "mdi:speedometer",
            "irradiance": "mdi:weather-sunny",
        }
        return icon_map.get(device_class, "mdi:bluetooth")

    @staticmethod
    def batch_translate_characteristics(
        characteristics: Dict[str, BaseCharacteristic],
        characteristic_data: Dict[str, bytearray],
    ) -> Dict[str, Dict[str, Any]]:
        """Translate multiple GATT characteristics to HA sensor format.

        Args:
            characteristics: Dict mapping UUID to characteristic instances
            characteristic_data: Dict mapping UUID to raw BLE data

        Returns:
            Dict mapping UUID to HA sensor data
        """
        translated_sensors = {}

        for uuid, characteristic in characteristics.items():
            if uuid in characteristic_data:
                sensor_data = GATTSensorTranslator.translate_to_ha_sensor(
                    characteristic, characteristic_data[uuid]
                )
                translated_sensors[uuid] = sensor_data

        return translated_sensors


# Example usage demonstrating proper architecture:
def example_home_assistant_integration():
    """Example showing proper HA integration architecture."""
    # This would be called from HA integration layer
    # HA Layer → Translation Layer → GATT Layer

    # 1. GATT layer provides characteristics (pure Bluetooth logic)
    # from ble_gatt_device.gatt.characteristics import BatteryLevelCharacteristic
    # characteristic = BatteryLevelCharacteristic(uuid="2A19", properties=set())

    # 2. Translation layer converts to HA format (THIS MODULE)
    # raw_data = bytearray([75])  # 75% battery
    # ha_sensor_data = GATTSensorTranslator.translate_to_ha_sensor(characteristic, raw_data)

    # 3. HA integration layer uses translation layer output
    # Creates HA entities using ha_sensor_data

    # Implementation would go here when integrated with Home Assistant
