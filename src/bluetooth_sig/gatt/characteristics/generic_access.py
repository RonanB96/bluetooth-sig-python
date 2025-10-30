"""Generic Access Service characteristics."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic (0x2A00).

    org.bluetooth.characteristic.gap.device_name

    Device Name characteristic.
    """

    _characteristic_name: str = "Device Name"
    _manual_value_type = "string"  # Override since decode_value returns str

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
        """Parse device name string.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            Decoded device name string.

        """
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode device name value back to bytes.

        Args:
            data: Device name as string

        Returns:
            Encoded bytes representing the device name (UTF-8)

        """
        # Encode as UTF-8 bytes
        return bytearray(data.encode("utf-8"))


class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic (0x2A01).

    org.bluetooth.characteristic.gap.appearance

    Appearance characteristic.
    """

    _characteristic_name: str = "Appearance"
    _manual_value_type = "int"  # Override since decode_value returns int

    min_length = 2  # Appearance(2) fixed length
    max_length = 2  # Appearance(2) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Parse appearance value (uint16).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            Parsed appearance as integer.

        """
        return DataParser.parse_int16(data, 0, signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode appearance value back to bytes.

        Args:
            data: Appearance value as integer

        Returns:
            Encoded bytes representing the appearance

        """
        appearance = int(data)
        return DataParser.encode_int16(appearance, signed=False)


class ServiceChangedCharacteristic(BaseCharacteristic):
    """Service Changed characteristic (0x2A05).

    org.bluetooth.characteristic.gatt.service_changed

    Service Changed characteristic.
    """

    _characteristic_name: str = "Service Changed"
    _manual_value_type = "bytes"  # Raw bytes for handle range

    min_length = 4  # Start Handle(2) + End Handle(2)
    max_length = 4  # Fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> dict[str, int]:
        """Parse service changed value.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            Dict with start_handle and end_handle.

        """
        start_handle = DataParser.parse_int16(data, 0, signed=False)
        end_handle = DataParser.parse_int16(data, 2, signed=False)
        return {"start_handle": start_handle, "end_handle": end_handle}

    def encode_value(self, data: dict[str, int]) -> bytearray:
        """Encode service changed value back to bytes.

        Args:
            data: Dict with start_handle and end_handle

        Returns:
            Encoded bytes

        """
        start_handle = int(data["start_handle"])
        end_handle = int(data["end_handle"])
        result = bytearray()
        result.extend(DataParser.encode_int16(start_handle, signed=False))
        result.extend(DataParser.encode_int16(end_handle, signed=False))
        return result
