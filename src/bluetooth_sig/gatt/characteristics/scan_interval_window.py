"""Scan Interval Window characteristic implementation."""

from __future__ import annotations

from ...types.scan_interval_window import ScanIntervalWindowData
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ScanIntervalWindowCharacteristic(BaseCharacteristic):
    """Scan Interval Window characteristic (0x2A4F).

    org.bluetooth.characteristic.scan_interval_window

    The Scan Interval Window characteristic is used to set the scan interval
    and scan window parameters for BLE scanning.

    This is a write-only characteristic containing:
    - Scan Interval: uint16 (2 bytes, little-endian, units of 0.625ms, range 0x0004-0x4000)
    - Scan Window: uint16 (2 bytes, little-endian, units of 0.625ms, range 0x0004-0x4000)

    The scan window must be less than or equal to the scan interval.
    """

    _characteristic_name = "Scan Interval Window"
    _manual_value_type = "ScanIntervalWindowData"  # Override since decode_value returns structured data

    expected_length = 4  # Scan Interval(2) + Scan Window(2)
    min_length = 4  # Scan Interval(2) + Scan Window(2)
    max_length = 4  # Fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ScanIntervalWindowData:
        """Parse scan interval window data.

        Args:
            data: Raw bytearray from BLE characteristic (4 bytes).
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            ScanIntervalWindowData with parsed scan parameters.

        """
        scan_interval = DataParser.parse_int16(data, 0, signed=False)
        scan_window = DataParser.parse_int16(data, 2, signed=False)

        return ScanIntervalWindowData(scan_interval=scan_interval, scan_window=scan_window)

    def encode_value(self, data: ScanIntervalWindowData) -> bytearray:
        """Encode scan interval window value back to bytes.

        Args:
            data: ScanIntervalWindowData instance

        Returns:
            Encoded bytes representing the scan parameters (4 bytes)

        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.scan_interval, signed=False))
        result.extend(DataParser.encode_int16(data.scan_window, signed=False))
        return result
