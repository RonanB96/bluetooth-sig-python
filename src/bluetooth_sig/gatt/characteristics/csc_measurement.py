"""CSC Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .csc_feature import CSCFeatureCharacteristic, CSCFeatureData
from .utils import DataParser


class CSCMeasurementFlags(IntFlag):
    """CSC Measurement flags as per Bluetooth SIG specification."""

    WHEEL_REVOLUTION_DATA_PRESENT = 0x01
    CRANK_REVOLUTION_DATA_PRESENT = 0x02


class CSCMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from CSC Measurement characteristic."""

    flags: CSCMeasurementFlags
    cumulative_wheel_revolutions: int | None = None
    last_wheel_event_time: float | None = None
    cumulative_crank_revolutions: int | None = None
    last_crank_event_time: float | None = None

    def __post_init__(self) -> None:
        """Validate CSC measurement data."""
        if not 0 <= int(self.flags) <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")


class CSCMeasurementCharacteristic(BaseCharacteristic):
    """CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B).

    Used to transmit cycling speed and cadence data.
    """

    # Override automatic name resolution because "CSC" is an acronym
    _characteristic_name: str | None = "CSC Measurement"

    # Time resolution constants
    CSC_TIME_RESOLUTION = 1024.0  # 1/1024 second resolution for both wheel and crank event times

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CSCMeasurementData:
        """Parse CSC measurement data according to Bluetooth specification.

        Format: Flags(1) + [Cumulative Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
        [Cumulative Crank Revolutions(2)] + [Last Crank Event Time(2)]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            CSCMeasurementData containing parsed CSC data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 1:
            raise ValueError("CSC Measurement data must be at least 1 byte")

        flags = CSCMeasurementFlags(data[0])
        offset = 1

        # Initialize result data
        cumulative_wheel_revolutions = None
        last_wheel_event_time = None
        cumulative_crank_revolutions = None
        last_crank_event_time = None

        # Parse optional wheel revolution data (6 bytes total) if present
        if (flags & CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 6:
            wheel_revolutions = DataParser.parse_int32(data, offset, signed=False)
            wheel_event_time_raw = DataParser.parse_int16(data, offset + 4, signed=False)
            # Wheel event time is in 1/CSC_TIME_RESOLUTION second units
            cumulative_wheel_revolutions = wheel_revolutions
            last_wheel_event_time = wheel_event_time_raw / self.CSC_TIME_RESOLUTION
            offset += 6

        # Parse optional crank revolution data (4 bytes total) if present
        if (flags & CSCMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT) and len(data) >= offset + 4:
            crank_revolutions = DataParser.parse_int16(data, offset, signed=False)
            crank_event_time_raw = DataParser.parse_int16(data, offset + 2, signed=False)
            # Crank event time is in 1/CSC_TIME_RESOLUTION second units
            cumulative_crank_revolutions = crank_revolutions
            last_crank_event_time = crank_event_time_raw / self.CSC_TIME_RESOLUTION

        # Validate flags against CSC Feature if available
        if ctx is not None:
            feature_char = self.get_context_characteristic(ctx, CSCFeatureCharacteristic)
            if feature_char and feature_char.parse_success and feature_char.value is not None:
                self._validate_against_feature(flags, feature_char.value)

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
            flags |= CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT
        if has_crank_data:
            flags |= CSCMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT

        # Start with flags byte
        result = bytearray([int(flags)])

        # Add wheel revolution data if present
        if has_wheel_data:
            result.extend(self._encode_wheel_data(data))

        # Add crank revolution data if present
        if has_crank_data:
            result.extend(self._encode_crank_data(data))

        return result

    def _validate_against_feature(self, flags: int, feature_data: CSCFeatureData) -> None:
        """Validate measurement flags against CSC Feature characteristic.

        Args:
            flags: Measurement flags indicating which data is present
            feature_data: CSCFeatureData from CSC Feature characteristic

        Raises:
            ValueError: If reported measurement fields are not supported by device features

        """
        # Validate that reported measurement fields are supported
        wheel_flag = int(CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT)
        if (flags & wheel_flag) and not feature_data.wheel_revolution_data_supported:
            raise ValueError("Wheel revolution data reported but not supported by CSC Feature")
        crank_flag = int(CSCMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT)
        if (flags & crank_flag) and not feature_data.crank_revolution_data_supported:
            raise ValueError("Crank revolution data reported but not supported by CSC Feature")
