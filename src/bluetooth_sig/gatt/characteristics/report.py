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


class ReportCharacteristic(BaseCharacteristic[ReportData]):
    """Report characteristic (0x2A4D).

    org.bluetooth.characteristic.report

    Report characteristic.
    """

    _python_type: type | str | None = "ReportData"

    min_length = 1
    expected_type = bytes

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ReportData:
        """Parse report data.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.
            validate: Whether to validate ranges (default True)

        Returns:
            ReportData containing the report bytes.
        """
        return ReportData(data=bytes(data))

    def _encode_value(self, data: ReportData) -> bytearray:
        """Encode report data back to bytes.

        Args:
            data: ReportData instance to encode

        Returns:
            Encoded bytes
        """
        return bytearray(data.data)
