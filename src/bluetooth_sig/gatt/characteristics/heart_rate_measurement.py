"""Heart Rate Measurement characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from .base import BaseCharacteristic
from .utils import DataParser


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
        if not flags & 0x02:  # Sensor Contact Supported bit not set
            return cls.NOT_SUPPORTED
        if flags & 0x04:  # Sensor Contact Detected bit set
            return cls.DETECTED
        return cls.NOT_DETECTED


@dataclass
class HeartRateData:
    """Parsed data from Heart Rate Measurement characteristic."""

    heart_rate: int  # BPM (0-65535)
    sensor_contact: SensorContactState
    energy_expended: int | None = None  # kJ
    rr_intervals: list[float] = field(default_factory=list)  # R-R intervals in seconds
    flags: int = 0  # Raw flags byte for reference

    def __post_init__(self) -> None:
        """Validate heart rate measurement data."""
        if not 0 <= self.heart_rate <= 65535:
            raise ValueError(f"Heart rate must be 0-65535 bpm, got {self.heart_rate}")
        if self.energy_expended is not None and not 0 <= self.energy_expended <= 65535:
            raise ValueError(
                f"Energy expended must be 0-65535 kJ, got {self.energy_expended}"
            )
        for interval in self.rr_intervals:
            if not 0.0 <= interval <= 65.535:  # Max RR interval in seconds
                raise ValueError(
                    f"RR interval must be 0.0-65.535 seconds, got {interval}"
                )


@dataclass
class HeartRateMeasurementCharacteristic(BaseCharacteristic):
    """Heart Rate Measurement characteristic (0x2A37).

    Used in Heart Rate Service to transmit heart rate measurements.
    """

    _characteristic_name: str = "Heart Rate Measurement"

    def decode_value(self, data: bytearray) -> HeartRateData:
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

        # Parse heart rate value
        if flags & 0x01:  # 16-bit heart rate value
            if len(data) < offset + 2:
                raise ValueError("Insufficient data for 16-bit heart rate value")
            heart_rate = DataParser.parse_int16(data, offset, signed=False)
            offset += 2
        else:  # 8-bit heart rate value
            heart_rate = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        # Determine sensor contact state
        sensor_contact = SensorContactState.from_flags(flags)

        # Parse optional energy expended (2 bytes) if present
        energy_expended = None
        if (flags & 0x08) and len(data) >= offset + 2:
            energy_expended = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Parse optional RR-Intervals if present
        rr_intervals: list[float] = []
        if (flags & 0x10) and len(data) >= offset + 2:
            while offset + 2 <= len(data):
                rr_interval_raw = DataParser.parse_int16(data, offset, signed=False)
                # RR-Interval is in 1/1024 second units
                rr_intervals.append(rr_interval_raw / 1024.0)
                offset += 2

        return HeartRateData(
            heart_rate=heart_rate,
            sensor_contact=sensor_contact,
            energy_expended=energy_expended,
            rr_intervals=rr_intervals,
            flags=flags,
        )

    def encode_value(self, data: HeartRateData) -> bytearray:
        """Encode HeartRateData back to bytes.

        Args:
            data: HeartRateData instance to encode

        Returns:
            Encoded bytes representing the heart rate measurement
        """
        # Build flags byte
        flags = 0

        # Determine if 16-bit heart rate value is needed
        if data.heart_rate > 255:
            flags |= 0x01  # 16-bit heart rate format

        # Set sensor contact flags
        if data.sensor_contact != SensorContactState.NOT_SUPPORTED:
            flags |= 0x02  # Sensor Contact Supported
            if data.sensor_contact == SensorContactState.DETECTED:
                flags |= 0x04  # Sensor Contact Detected

        # Set energy expended flag if present
        if data.energy_expended is not None:
            flags |= 0x08  # Energy Expended Present

        # Set RR-Intervals flag if present
        if data.rr_intervals:
            flags |= 0x10  # RR-Intervals Present

        # Start building the payload
        result = bytearray([flags])

        # Add heart rate value
        if flags & 0x01:  # 16-bit format
            result.extend(DataParser.encode_int16(data.heart_rate, signed=False))
        else:  # 8-bit format
            result.extend(DataParser.encode_int8(data.heart_rate, signed=False))

        # Add energy expended if present
        if data.energy_expended is not None:
            result.extend(DataParser.encode_int16(data.energy_expended, signed=False))

        # Add RR-Intervals if present
        for rr_interval in data.rr_intervals:
            # Convert seconds to 1/1024 second units
            rr_raw = round(rr_interval * 1024)
            rr_raw = min(rr_raw, 65535)  # Clamp to max value
            result.extend(DataParser.encode_int16(rr_raw, signed=False))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "bpm"
