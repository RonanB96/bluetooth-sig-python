"""Body Sensor Location characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.gatt.context import CharacteristicContext

from .base import BaseCharacteristic


class BodySensorLocation(IntEnum):
    """Body sensor location enumeration (0x2A38)."""

    OTHER = 0
    CHEST = 1
    WRIST = 2
    FINGER = 3
    HAND = 4
    EAR_LOBE = 5
    FOOT = 6


class BodySensorLocationCharacteristic(BaseCharacteristic):
    """Body Sensor Location characteristic (0x2A38).

    Represents the location of a sensor on the human body.
    Used primarily with heart rate and other health monitoring devices.

    Spec: Bluetooth SIG Assigned Numbers, Body Sensor Location characteristic
    """

    # YAML has no range constraint; enforce valid enum bounds.
    min_value: int = BodySensorLocation.OTHER  # 0
    max_value: int = BodySensorLocation.FOOT  # 6

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BodySensorLocation:
        """Decode body sensor location from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Unused, for signature compatibility

        Returns:
            BodySensorLocation enum value

        Raises:
            ValueError: If data length is not exactly 1 byte or value is invalid

        """
        del ctx  # Unused parameter

        location_value = int(data[0])
        try:
            return BodySensorLocation(location_value)
        except ValueError as e:
            raise ValueError(f"Invalid Body Sensor Location value: {location_value} (valid range: 0-6)") from e

    def encode_value(self, data: BodySensorLocation) -> bytearray:
        """Encode body sensor location to bytes.

        Args:
            data: BodySensorLocation enum value

        Returns:
            Encoded bytes (1 byte)

        """
        return bytearray([data.value])
