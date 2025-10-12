"""CSC Measurement characteristic implementation."""

from __future__ import annotations

from typing import Any

import msgspec

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .utils import DataParser

# TODO: Implement CharacteristicContext support
# This characteristic should access CSC Feature (0x2A5C) from ctx.other_characteristics
# to determine which measurement fields are supported and apply appropriate scaling


class CSCMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from CSC Measurement characteristic."""

    flags: int
    cumulative_wheel_revolutions: int | None = None
    last_wheel_event_time: float | None = None
    cumulative_crank_revolutions: int | None = None
    last_crank_event_time: float | None = None

    def __post_init__(self) -> None:
        """Validate CSC measurement data."""
        if not 0 <= self.flags <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")


class CSCMeasurementCharacteristic(BaseCharacteristic):
    """CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B).

    Used to transmit cycling speed and cadence data.
    """

    # Override automatic name resolution because "CSC" is an acronym
    _characteristic_name: str | None = "CSC Measurement"

    # CSC Measurement Flags (per Bluetooth SIG specification)
    WHEEL_REVOLUTION_DATA_PRESENT = 0x01
    CRANK_REVOLUTION_DATA_PRESENT = 0x02

    # Time resolution constants
    CSC_TIME_RESOLUTION = 1024.0  # 1/1024 second resolution for both wheel and crank event times

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> CSCMeasurementData:
        """Parse CSC measurement data according to Bluetooth specification.

        Format: Flags(1) + [Cumulative Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
        [Cumulative Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            CSCMeasurementData containing parsed CSC data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 1:
            raise ValueError("CSC Measurement data must be at least 1 byte")

        flags = data[0]
        offset = 1

        # Initialize result data
        cumulative_wheel_revolutions = None
        last_wheel_event_time = None
        cumulative_crank_revolutions = None
        last_crank_event_time = None

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & self.WHEEL_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 6:
            wheel_revolutions = DataParser.parse_int32(data, offset, signed=False)
            wheel_event_time_raw = DataParser.parse_int16(data, offset + 4, signed=False)
            # Wheel event time is in 1/CSC_TIME_RESOLUTION second units
            cumulative_wheel_revolutions = wheel_revolutions
            last_wheel_event_time = wheel_event_time_raw / self.CSC_TIME_RESOLUTION
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & self.CRANK_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 4:
            crank_revolutions = DataParser.parse_int16(data, offset, signed=False)
            crank_event_time_raw = DataParser.parse_int16(data, offset + 2, signed=False)
            # Crank event time is in 1/CSC_TIME_RESOLUTION second units
            cumulative_crank_revolutions = crank_revolutions
            last_crank_event_time = crank_event_time_raw / self.CSC_TIME_RESOLUTION

        return CSCMeasurementData(
            flags=flags,
            cumulative_wheel_revolutions=cumulative_wheel_revolutions,
            last_wheel_event_time=last_wheel_event_time,
            cumulative_crank_revolutions=cumulative_crank_revolutions,
            last_crank_event_time=last_crank_event_time,
        )

    def _encode_wheel_data(self, data: CSCMeasurementData) -> bytearray:
        """Encode wheel revolution data.

        Args:
            data: CSCMeasurementData containing wheel data

        Returns:
            Encoded wheel revolution bytes

        Raises:
            ValueError: If wheel data is invalid or out of range
        """
        if data.cumulative_wheel_revolutions is None or data.last_wheel_event_time is None:
            raise ValueError("CSC wheel revolution data marked present but missing values")

        wheel_revolutions = int(data.cumulative_wheel_revolutions)
        wheel_event_time = float(data.last_wheel_event_time)

        # Validate ranges
        if not 0 <= wheel_revolutions <= 0xFFFFFFFF:
            raise ValueError(f"Wheel revolutions {wheel_revolutions} exceeds uint32 range")

        wheel_event_time_raw = round(wheel_event_time * self.CSC_TIME_RESOLUTION)
        if not 0 <= wheel_event_time_raw <= 0xFFFF:
            raise ValueError(f"Wheel event time {wheel_event_time_raw} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int32(wheel_revolutions, signed=False))
        result.extend(DataParser.encode_int16(wheel_event_time_raw, signed=False))
        return result

    def _encode_crank_data(self, data: CSCMeasurementData) -> bytearray:
        """Encode crank revolution data.

        Args:
            data: CSCMeasurementData containing crank data

        Returns:
            Encoded crank revolution bytes

        Raises:
            ValueError: If crank data is invalid or out of range
        """
        if data.cumulative_crank_revolutions is None or data.last_crank_event_time is None:
            raise ValueError("CSC crank revolution data marked present but missing values")

        crank_revolutions = int(data.cumulative_crank_revolutions)
        crank_event_time = float(data.last_crank_event_time)

        # Validate ranges
        if not 0 <= crank_revolutions <= 0xFFFF:
            raise ValueError(f"Crank revolutions {crank_revolutions} exceeds uint16 range")

        crank_event_time_raw = round(crank_event_time * self.CSC_TIME_RESOLUTION)
        if not 0 <= crank_event_time_raw <= 0xFFFF:
            raise ValueError(f"Crank event time {crank_event_time_raw} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(crank_revolutions, signed=False))
        result.extend(DataParser.encode_int16(crank_event_time_raw, signed=False))
        return result

    def encode_value(self, data: CSCMeasurementData) -> bytearray:
        """Encode CSC measurement value back to bytes.

        Args:
            data: CSCMeasurementData containing CSC measurement data

        Returns:
            Encoded bytes representing the CSC measurement
        """
        # Build flags based on available data
        flags = data.flags
        has_wheel_data = data.cumulative_wheel_revolutions is not None and data.last_wheel_event_time is not None
        has_crank_data = data.cumulative_crank_revolutions is not None and data.last_crank_event_time is not None

        # Update flags to match available data
        if has_wheel_data:
            flags |= self.WHEEL_REVOLUTION_DATA_PRESENT
        if has_crank_data:
            flags |= self.CRANK_REVOLUTION_DATA_PRESENT

        # Start with flags byte
        result = bytearray([flags])

        # Add wheel revolution data if present
        if has_wheel_data:
            result.extend(self._encode_wheel_data(data))

        # Add crank revolution data if present
        if has_crank_data:
            result.extend(self._encode_crank_data(data))

        return result
