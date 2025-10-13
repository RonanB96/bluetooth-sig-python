"""Heart Rate Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# TODO: Implement CharacteristicContext support
# This characteristic should access Heart Rate Control Point (0x2A39) from ctx.other_characteristics
# to provide calibration factors and control commands for enhanced heart rate monitoring


class HeartRateMeasurementFlags(IntFlag):
    """Heart Rate Measurement flags as per Bluetooth SIG specification."""

    HEART_RATE_VALUE_FORMAT_UINT16 = 0x01
    SENSOR_CONTACT_SUPPORTED = 0x02
    SENSOR_CONTACT_DETECTED = 0x04
    ENERGY_EXPENDED_PRESENT = 0x08
    RR_INTERVAL_PRESENT = 0x10


class SensorContactState(IntEnum):
    """Sensor contact state enumeration."""

    NOT_SUPPORTED = 0
    NOT_DETECTED = 1
    DETECTED = 2

    def __str__(self) -> str:
        return {0: "not_supported", 1: "not_detected", 2: "detected"}[self.value]

    def __eq__(self, other: object) -> bool:
        """Support comparison with string values for backward compatibility."""
        if isinstance(other, str):
            return str(self) == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Make enum hashable."""
        return super().__hash__()

    @classmethod
    def from_flags(cls, flags: int) -> SensorContactState:
        """Create enum from heart rate flags."""
        if not flags & HeartRateMeasurementFlags.SENSOR_CONTACT_SUPPORTED:  # Sensor Contact Supported bit not set
            return cls.NOT_SUPPORTED
        if flags & HeartRateMeasurementFlags.SENSOR_CONTACT_DETECTED:  # Sensor Contact Detected bit set
            return cls.DETECTED
        return cls.NOT_DETECTED


class HeartRateData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Heart Rate Measurement characteristic."""

    heart_rate: int  # BPM (0-UINT16_MAX)
    sensor_contact: SensorContactState
    energy_expended: int | None = None  # kJ
    rr_intervals: tuple[float, ...] = ()  # R-R intervals in seconds, immutable tuple
    flags: int = 0  # Raw flags byte for reference

    def __post_init__(self) -> None:
        """Validate heart rate measurement data."""
        if not 0 <= self.heart_rate <= UINT16_MAX:
            raise ValueError(f"Heart rate must be 0-{UINT16_MAX} bpm, got {self.heart_rate}")
        if self.energy_expended is not None and not 0 <= self.energy_expended <= UINT16_MAX:
            raise ValueError(f"Energy expended must be 0-{UINT16_MAX} kJ, got {self.energy_expended}")
        for interval in self.rr_intervals:
            if not 0.0 <= interval <= 65.535:  # Max RR interval in seconds
                raise ValueError(f"RR interval must be 0.0-65.535 seconds, got {interval}")


class HeartRateMeasurementCharacteristic(BaseCharacteristic):
    """Heart Rate Measurement characteristic (0x2A37).

    Used in Heart Rate Service (spec: Heart Rate Service 1.0, Heart Rate Profile 1.0)
    to transmit instantaneous heart rate plus optional energy expended and
    RR-Interval metrics.

    Specification summary (flags byte bit assignments – see adopted spec & Errata 23224):
      Bit 0 (0x01): Heart Rate Value Format (0 = uint8, 1 = uint16)
      Bit 1 (0x02): Sensor Contact Supported
      Bit 2 (0x04): Sensor Contact Detected (valid only when Bit1 set)
      Bit 3 (0x08): Energy Expended Present (adds 2 bytes, little-endian, in kilo Joules)
      Bit 4 (0x10): RR-Interval(s) Present (sequence of 16‑bit values, units 1/1024 s)
      Bits 5-7: Reserved (must be 0)

    Parsing Rules:
      * Minimum length: 2 bytes (flags + at least one byte of heart rate value)
      * If Bit0 set, heart rate is 16 bits; else 8 bits
      * Energy Expended only parsed if flag set AND 2 bytes remain
      * RR-Intervals parsed greedily in pairs until buffer end when flag set
      * RR-Interval raw value converted to seconds: raw / 1024.0
      * Sensor contact state derived from Bits1/2 tri-state (not supported, not detected, detected)

    Validation:
      * Heart rate validated within 0..UINT16_MAX (spec does not strictly define upper physiological bound)
      * RR interval constrained to 0.0–65.535 s (fits 16-bit / 1024 scaling and guards against malformed data)
      * Energy expended 0..UINT16_MAX

    References:
      * Bluetooth SIG Heart Rate Service 1.0 (https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/)
      * Bluetooth SIG Heart Rate Profile 1.0 (https://www.bluetooth.com/specifications/specs/heart-rate-profile-1-0/)
      * Errata Correction 23224 (mandatory for compliance)
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> HeartRateData:
        """Parse heart rate measurement data according to Bluetooth specification.

        Format: Flags(1) + Heart Rate Value(1-2) + [Energy Expended(2)] + [RR-Intervals(2*n)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            HeartRateData containing parsed heart rate data with metadata
        """
        if len(data) < 2:
            raise ValueError("Heart Rate Measurement data must be at least 2 bytes")

        flags = data[0]
        offset = 1

        # Parse heart rate value (8-bit or 16-bit depending on flag)
        if flags & HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16:  # 16-bit heart rate value
            if len(data) < offset + 2:
                raise ValueError("Insufficient data for 16-bit heart rate value")
            heart_rate = DataParser.parse_int16(data, offset, signed=False)
            offset += 2
        else:  # 8-bit heart rate value
            heart_rate = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        sensor_contact = SensorContactState.from_flags(flags)

        # Optional Energy Expended
        energy_expended = None
        if (flags & HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT) and len(data) >= offset + 2:
            energy_expended = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Optional RR-Intervals
        rr_intervals: list[float] = []
        if (flags & HeartRateMeasurementFlags.RR_INTERVAL_PRESENT) and len(data) >= offset + 2:
            while offset + 2 <= len(data):
                rr_interval_raw = DataParser.parse_int16(data, offset, signed=False)
                rr_intervals.append(rr_interval_raw / 1024.0)
                offset += 2

        return HeartRateData(
            heart_rate=heart_rate,
            sensor_contact=sensor_contact,
            energy_expended=energy_expended,
            rr_intervals=tuple(rr_intervals),  # Convert list to tuple for immutable struct
            flags=flags,
        )

    def encode_value(self, data: HeartRateData) -> bytearray:
        """Encode HeartRateData back to bytes.

        The inverse of decode_value respecting the same flag semantics.

        Args:
            data: HeartRateData instance to encode

        Returns:
            Encoded bytes representing the heart rate measurement
        """
        flags = 0

        if data.heart_rate > UINT8_MAX:
            flags |= HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16

        if data.sensor_contact != SensorContactState.NOT_SUPPORTED:
            flags |= HeartRateMeasurementFlags.SENSOR_CONTACT_SUPPORTED
            if data.sensor_contact == SensorContactState.DETECTED:
                flags |= HeartRateMeasurementFlags.SENSOR_CONTACT_DETECTED

        if data.energy_expended is not None:
            flags |= HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT

        if data.rr_intervals:
            flags |= HeartRateMeasurementFlags.RR_INTERVAL_PRESENT

        result = bytearray([flags])

        if flags & HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16:
            result.extend(DataParser.encode_int16(data.heart_rate, signed=False))
        else:
            result.extend(DataParser.encode_int8(data.heart_rate, signed=False))

        if data.energy_expended is not None:
            result.extend(DataParser.encode_int16(data.energy_expended, signed=False))

        for rr_interval in data.rr_intervals:
            rr_raw = round(rr_interval * 1024)
            rr_raw = min(rr_raw, UINT16_MAX)
            result.extend(DataParser.encode_int16(rr_raw, signed=False))

        return result
