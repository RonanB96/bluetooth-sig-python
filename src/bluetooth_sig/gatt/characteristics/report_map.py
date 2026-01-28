"""Report Map characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ReportMapData(msgspec.Struct, frozen=True):
    """Parsed data from Report Map characteristic.

    Attributes:
        data: Report map data bytes (up to 512 octets)
    """

    data: bytes


class ReportMapCharacteristic(BaseCharacteristic[ReportMapData]):
    """Report Map characteristic (0x2A4B).

    org.bluetooth.characteristic.report_map

    Report Map characteristic.
    """

    min_length = 1
    expected_type = bytes

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ReportMapData:
        """Parse report map data.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.
            validate: Whether to validate ranges (default True)

        Returns:
            ReportMapData containing the report map bytes.
        """
        return ReportMapData(data=bytes(data))

    def _encode_value(self, data: ReportMapData) -> bytearray:
        """Encode report map back to bytes.

        Args:
            data: ReportMapData instance to encode

        Returns:
            Encoded bytes
        """
        return bytearray(data.data)
