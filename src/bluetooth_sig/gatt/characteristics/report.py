"""Report characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ReportData(msgspec.Struct, frozen=True):
    """Parsed data from Report characteristic.

    Attributes:
        data: Report data bytes (variable length)
    """

    data: bytes


class ReportCharacteristic(BaseCharacteristic):
    """Report characteristic (0x2A4D).

    org.bluetooth.characteristic.report

    Report characteristic.
    """

    min_length = 1
    expected_type = bytes

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ReportData:
        """Parse report data.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.

        Returns:
            ReportData containing the report bytes.
        """
        return ReportData(data=bytes(data))

    def encode_value(self, data: ReportData) -> bytearray:
        """Encode report data back to bytes.

        Args:
            data: ReportData instance to encode

        Returns:
            Encoded bytes
        """
        return bytearray(data.data)
