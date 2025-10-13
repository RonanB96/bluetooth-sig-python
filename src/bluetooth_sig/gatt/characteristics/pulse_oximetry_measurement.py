"""Pulse Oximetry Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag
from typing import Any

import msgspec

from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# TODO: Implement CharacteristicContext support
# This characteristic should access Pulse Oximetry Control Point (0x2A60) and Pulse Oximetry Features (0x2A61)
# from ctx.other_characteristics to determine supported measurement types and calibration data


class PulseOximetryFlags(IntFlag):
    """Pulse Oximetry measurement flags."""

    TIMESTAMP_PRESENT = 0x01
    MEASUREMENT_STATUS_PRESENT = 0x02
    DEVICE_STATUS_PRESENT = 0x04
    PULSE_AMPLITUDE_INDEX_PRESENT = 0x08


class PulseOximetryData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed pulse oximetry measurement data."""

    spo2: float
    pulse_rate: float
    timestamp: datetime | None = None
    measurement_status: int | None = None
    device_status: int | None = None
    pulse_amplitude_index: float | None = None


class PulseOximetryMeasurementCharacteristic(BaseCharacteristic):
    """PLX Continuous Measurement characteristic (0x2A5F).

    Used to transmit SpO2 (blood oxygen saturation) and pulse rate
    measurements.
    """

    _characteristic_name: str = "PLX Continuous Measurement"

    # Declarative validation (automatic)
    min_length: int | None = 5  # Flags(1) + SpO2(2) + PulseRate(2) minimum
    max_length: int | None = 16  # + Timestamp(7) + MeasurementStatus(2) + DeviceStatus(3) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> PulseOximetryData:  # pylint: disable=too-many-locals
        """Parse pulse oximetry measurement data according to Bluetooth
        specification.

        Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Timestamp(7)] +
        [Measurement Status(2)] + [Device Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            PulseOximetryData containing parsed pulse oximetry data
        """
        if len(data) < 5:
            raise ValueError("Pulse Oximetry Measurement data must be at least 5 bytes")

        flags = PulseOximetryFlags(data[0])

        # Parse SpO2 and pulse rate using IEEE-11073 SFLOAT format
        spo2 = IEEE11073Parser.parse_sfloat(data, 1)
        pulse_rate = IEEE11073Parser.parse_sfloat(data, 3)

        result = PulseOximetryData(spo2=spo2, pulse_rate=pulse_rate)

        offset = 5

        # Parse optional timestamp (7 bytes) if present
        if PulseOximetryFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            result.timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional measurement status (2 bytes) if present
        if PulseOximetryFlags.MEASUREMENT_STATUS_PRESENT in flags and len(data) >= offset + 2:
            result.measurement_status = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        # Parse optional device and sensor status (3 bytes) if present
        if PulseOximetryFlags.DEVICE_STATUS_PRESENT in flags and len(data) >= offset + 3:
            device_status = DataParser.parse_int32(
                data[offset : offset + 3] + b"\x00", 0, signed=False
            )  # Pad to 4 bytes
            result.device_status = device_status
            offset += 3

        # Parse optional pulse amplitude index (2 bytes) if present
        if PulseOximetryFlags.PULSE_AMPLITUDE_INDEX_PRESENT in flags and len(data) >= offset + 2:
            result.pulse_amplitude_index = IEEE11073Parser.parse_sfloat(data, offset)

        return result

    def encode_value(self, data: PulseOximetryData) -> bytearray:
        """Encode pulse oximetry measurement value back to bytes.

        Args:
            data: PulseOximetryData instance to encode

        Returns:
            Encoded bytes representing the measurement
        """
        # Convert to IEEE-11073 SFLOAT format (simplified as uint16)
        spo2_raw = round(data.spo2 * 10)  # 0.1% resolution
        pulse_rate_raw = round(data.pulse_rate)  # 1 bpm resolution

        # Validate ranges
        if not 0 <= spo2_raw <= 0xFFFF:
            raise ValueError(f"SpO2 {spo2_raw} exceeds uint16 range")
        if not 0 <= pulse_rate_raw <= 0xFFFF:
            raise ValueError(f"Pulse rate {pulse_rate_raw} exceeds uint16 range")

        # Build flags
        flags = PulseOximetryFlags(0)
        if data.timestamp is not None:
            flags |= PulseOximetryFlags.TIMESTAMP_PRESENT
        if data.measurement_status is not None:
            flags |= PulseOximetryFlags.MEASUREMENT_STATUS_PRESENT
        if data.device_status is not None:
            flags |= PulseOximetryFlags.DEVICE_STATUS_PRESENT
        if data.pulse_amplitude_index is not None:
            flags |= PulseOximetryFlags.PULSE_AMPLITUDE_INDEX_PRESENT

        # Build result
        result = bytearray([int(flags)])
        result.extend(DataParser.encode_int16(spo2_raw, signed=False))
        result.extend(DataParser.encode_int16(pulse_rate_raw, signed=False))

        # Additional fields based on flags would be added (simplified)
        return result
