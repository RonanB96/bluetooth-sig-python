"""RSC Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .rsc_feature import RSCFeatureCharacteristic
from .utils import DataParser


class RSCMeasurementFlags(IntFlag):
    """RSC Measurement flags as per Bluetooth SIG specification."""

    INSTANTANEOUS_STRIDE_LENGTH_PRESENT = 0x01
    TOTAL_DISTANCE_PRESENT = 0x02


class RSCMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from RSC Measurement characteristic."""

    instantaneous_speed: float  # m/s
    instantaneous_cadence: int  # steps per minute
    flags: RSCMeasurementFlags
    instantaneous_stride_length: float | None = None  # meters
    total_distance: float | None = None  # meters

    def __post_init__(self) -> None:
        """Validate RSC measurement data."""
        if not 0 <= self.flags <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")
        if not 0 <= self.instantaneous_cadence <= UINT8_MAX:
            raise ValueError("Cadence must be a uint8 value (0-UINT8_MAX)")


class RSCMeasurementCharacteristic(BaseCharacteristic[RSCMeasurementData]):
    """RSC (Running Speed and Cadence) Measurement characteristic (0x2A53).

    Used to transmit running speed and cadence data.
    """

    # Declare optional dependency on RSC Feature for validation
    # This ensures RSC Feature is parsed first when both are present
    _optional_dependencies = [RSCFeatureCharacteristic]

    min_length: int = 4  # Flags(1) + Speed(2) + Cadence(1)
    allow_variable_length: bool = True  # Optional stride length and total distance

    def _validate_against_feature(self, data: RSCMeasurementData, ctx: CharacteristicContext) -> None:
        """Validate RSC measurement data against supported features.

        Args:
            data: Parsed RSC measurement data to validate.
            ctx: CharacteristicContext containing other characteristics.

        Raises:
            ValueError: If measurement reports unsupported features.

        """
        # Get RSC Feature characteristic from context
        feature_data = self.get_context_characteristic(ctx, RSCFeatureCharacteristic)
        if feature_data is None:
            # No feature characteristic available, skip validation
            return

        # Validate optional fields against supported features
        if data.instantaneous_stride_length is not None and not feature_data.instantaneous_stride_length_supported:
            raise ValueError("Instantaneous stride length reported but not supported by device features")

        if data.total_distance is not None and not feature_data.total_distance_supported:
            raise ValueError("Total distance reported but not supported by device features")

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> RSCMeasurementData:
        """Parse RSC measurement data according to Bluetooth specification.

        Format: Flags(1) + Instantaneous Speed(2) + Instantaneous Cadence(1) +
        [Instantaneous Stride Length(2)] + [Total Distance(4)].

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            RSCMeasurementData containing parsed RSC data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 4:
            raise ValueError("RSC Measurement data must be at least 4 bytes")

        flags = RSCMeasurementFlags(data[0])

        # Parse instantaneous speed (uint16, 1/256 m/s units)
        speed_raw = DataParser.parse_int16(data, 1, signed=False)
        speed_ms = speed_raw / 256.0  # m/s

        # Parse instantaneous cadence (uint8, 1/min units)
        cadence = data[3]

        # Initialize optional fields
        instantaneous_stride_length = None
        total_distance = None

        offset = 4

        # Parse optional instantaneous stride length (2 bytes) if present
        if (RSCMeasurementFlags.INSTANTANEOUS_STRIDE_LENGTH_PRESENT in flags) and len(data) >= offset + 2:
            stride_length_raw = DataParser.parse_int16(data, offset, signed=False)
            instantaneous_stride_length = stride_length_raw / 100.0  # Convert to meters
            offset += 2

        # Parse optional total distance (4 bytes) if present
        if (RSCMeasurementFlags.TOTAL_DISTANCE_PRESENT in flags) and len(data) >= offset + 4:
            total_distance_raw = DataParser.parse_int32(data, offset, signed=False)
            total_distance = total_distance_raw / 10.0  # Convert to meters

        measurement_data = RSCMeasurementData(
            instantaneous_speed=speed_ms,
            instantaneous_cadence=cadence,
            flags=flags,
            instantaneous_stride_length=instantaneous_stride_length,
            total_distance=total_distance,
        )

        # Validate against feature characteristic if context is available
        if ctx is not None:
            self._validate_against_feature(measurement_data, ctx)

        return measurement_data

    def _encode_value(self, data: RSCMeasurementData) -> bytearray:
        """Encode RSC measurement value back to bytes.

        Args:
            data: RSCMeasurementData containing RSC measurement data

        Returns:
            Encoded bytes representing the RSC measurement

        """
        # Build flags based on available optional data
        flags = RSCMeasurementFlags(data.flags)
        has_stride_length = data.instantaneous_stride_length is not None
        has_total_distance = data.total_distance is not None

        # Update flags to match available data
        if has_stride_length:
            flags |= RSCMeasurementFlags.INSTANTANEOUS_STRIDE_LENGTH_PRESENT
        if has_total_distance:
            flags |= RSCMeasurementFlags.TOTAL_DISTANCE_PRESENT

        # Validate required fields
        speed_raw = round(data.instantaneous_speed * 256)  # Convert to 1/256 m/s units
        if not 0 <= speed_raw <= 0xFFFF:
            raise ValueError(f"Speed {data.instantaneous_speed} m/s exceeds uint16 range")

        if not 0 <= data.instantaneous_cadence <= UINT8_MAX:
            raise ValueError(f"Cadence {data.instantaneous_cadence} exceeds uint8 range")

        # Start with flags, speed, and cadence
        result = bytearray([int(flags)])
        result.extend(DataParser.encode_int16(speed_raw, signed=False))
        result.append(data.instantaneous_cadence)

        # Add optional stride length if present
        if has_stride_length:
            if data.instantaneous_stride_length is None:
                raise ValueError("Stride length is required but None")
            stride_length = float(data.instantaneous_stride_length)
            stride_length_raw = round(stride_length * 100)  # Convert to cm units
            if not 0 <= stride_length_raw <= 0xFFFF:
                raise ValueError(f"Stride length {stride_length} m exceeds uint16 range")
            result.extend(DataParser.encode_int16(stride_length_raw, signed=False))

        # Add optional total distance if present
        if has_total_distance:
            if data.total_distance is None:
                raise ValueError("Total distance is required but None")
            total_distance = float(data.total_distance)
            total_distance_raw = round(total_distance * 10)  # Convert to dm units
            if not 0 <= total_distance_raw <= 0xFFFFFFFF:
                raise ValueError(f"Total distance {total_distance} m exceeds uint32 range")
            result.extend(DataParser.encode_int32(total_distance_raw, signed=False))

        return result
