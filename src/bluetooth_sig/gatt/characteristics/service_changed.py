"""Service Changed characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ServiceChangedData(msgspec.Struct, frozen=True, kw_only=True):
    """Service Changed characteristic data.

    Attributes:
        start_handle: Starting handle of the affected service range
        end_handle: Ending handle of the affected service range
    """

    start_handle: int
    end_handle: int


class ServiceChangedCharacteristic(BaseCharacteristic[ServiceChangedData]):
    """Service Changed characteristic (0x2A05).

    org.bluetooth.characteristic.gatt.service_changed

    Service Changed characteristic.
    """

    expected_length = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ServiceChangedData:
        """Parse service changed value.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            ServiceChangedData with start_handle and end_handle.
        """
        start_handle = DataParser.parse_int16(data, 0, signed=False)
        end_handle = DataParser.parse_int16(data, 2, signed=False)
        return ServiceChangedData(start_handle=start_handle, end_handle=end_handle)

    def _encode_value(self, data: ServiceChangedData) -> bytearray:
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
