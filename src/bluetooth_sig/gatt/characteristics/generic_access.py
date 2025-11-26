"""Generic Access Service characteristics."""

from __future__ import annotations

import msgspec

from ...registry import appearance_values_registry
from ...types.appearance import AppearanceData
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import Utf8StringTemplate
from .utils import DataParser


class ServiceChangedData(msgspec.Struct, frozen=True, kw_only=True):
    """Service Changed characteristic data.

    Attributes:
        start_handle: Starting handle of the affected service range
        end_handle: Ending handle of the affected service range
    """

    start_handle: int
    end_handle: int


class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic (0x2A00).

    org.bluetooth.characteristic.gap.device_name

    Device Name characteristic.
    """

    _template = Utf8StringTemplate()


class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic (0x2A01).

    org.bluetooth.characteristic.gap.appearance

    Appearance characteristic with human-readable device type information.
    """

    _manual_value_type = "AppearanceData"  # Override since decode_value returns structured data

    min_length = 2  # Appearance(2) fixed length
    max_length = 2  # Appearance(2) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> AppearanceData:
        """Parse appearance value with human-readable info.

        Args:
            data: Raw bytearray from BLE characteristic (2 bytes).
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            AppearanceData with raw value and optional human-readable info.

        Example:
            >>> char = AppearanceCharacteristic()
            >>> result = char.decode_value(bytearray([0x41, 0x03]))  # 833
            >>> print(result.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
            >>> print(result.raw_value)  # 833
            >>> print(int(result))  # 833

        """
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        appearance_info = appearance_values_registry.get_appearance_info(raw_value)

        return AppearanceData(
            raw_value=raw_value,
            info=appearance_info,
        )

    def encode_value(self, data: AppearanceData) -> bytearray:
        """Encode appearance value back to bytes.

        Args:
            data: Appearance value as AppearanceData

        Returns:
            Encoded bytes representing the appearance

        """
        return DataParser.encode_int16(data.raw_value, signed=False)


class ServiceChangedCharacteristic(BaseCharacteristic):
    """Service Changed characteristic (0x2A05).

    org.bluetooth.characteristic.gatt.service_changed

    Service Changed characteristic.
    """

    _manual_value_type = "ServiceChangedData"  # Override since decode_value returns structured data

    min_length = 4  # Start Handle(2) + End Handle(2)
    max_length = 4  # Fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ServiceChangedData:
        """Parse service changed value.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            ServiceChangedData with start_handle and end_handle.

        Raises:
            ValueError: If data length is not exactly 4 bytes.

        """
        if len(data) != 4:
            raise ValueError(f"Service Changed characteristic requires 4 bytes, got {len(data)}")

        start_handle = DataParser.parse_int16(data, 0, signed=False)
        end_handle = DataParser.parse_int16(data, 2, signed=False)
        return ServiceChangedData(start_handle=start_handle, end_handle=end_handle)

    def encode_value(self, data: ServiceChangedData) -> bytearray:
        """Encode service changed value back to bytes.

        Args:
            data: ServiceChangedData with start_handle and end_handle

        Returns:
            Encoded bytes

        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.start_handle, signed=False))
        result.extend(DataParser.encode_int16(data.end_handle, signed=False))
        return result
