"""Pulse Oximetry Measurement characteristic implementation."""

import struct
from typing import Any

from .base import BaseCharacteristic
from .utils import IEEE11073Parser


class PulseOximetryContinuousMeasurementCharacteristic(BaseCharacteristic):
    """PLX Continuous Measurement characteristic (0x2A5F).

    Used to transmit SpO2 (blood oxygen saturation) and pulse rate measurements.
    """

    _characteristic_name: str = "PLX Continuous Measurement"

    def decode_value(self, data: bytearray) -> dict[str, Any]:  # pylint: disable=too-many-locals
        """Parse pulse oximetry measurement data according to Bluetooth specification.

        Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Timestamp(7)] +
        [Measurement Status(2)] + [Device Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed pulse oximetry data with metadata
        """
        if len(data) < 5:
            raise ValueError("Pulse Oximetry Measurement data must be at least 5 bytes")

        flags = data[0]

        # Parse SpO2 and pulse rate using IEEE-11073 SFLOAT format
        result = {
            "spo2": IEEE11073Parser.parse_sfloat(data, 1),
            "pulse_rate": IEEE11073Parser.parse_sfloat(data, 3),
            "unit": "%",  # SpO2 is always in percentage
        }

        offset = 5

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x01) and len(data) >= offset + 7:
            result["timestamp"] = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional measurement status (2 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 2:
            result["measurement_status"] = struct.unpack(
                "<H", data[offset : offset + 2]
            )[0]
            offset += 2

        # Parse optional device and sensor status (3 bytes) if present
        if (flags & 0x04) and len(data) >= offset + 3:
            device_status = struct.unpack("<I", data[offset : offset + 3] + b"\x00")[
                0
            ]  # Pad to 4 bytes
            result["device_status"] = device_status
            offset += 3

        # Parse optional pulse amplitude index (2 bytes) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            result["pulse_amplitude_index"] = IEEE11073Parser.parse_sfloat(data, offset)

        return result

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode pulse oximetry measurement value back to bytes.

        Args:
            data: Dictionary containing pulse oximetry measurement data

        Returns:
            Encoded bytes representing the measurement
        """
        if not isinstance(data, dict):
            raise TypeError("Pulse oximetry measurement data must be a dictionary")

        # Required fields for pulse oximetry
        required_fields = ["spo2", "pulse_rate"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Pulse oximetry data must contain '{field}' key")

        flags = data.get("flags", 0)
        spo2 = float(data["spo2"])
        pulse_rate = float(data["pulse_rate"])

        # Convert to IEEE-11073 SFLOAT format (simplified as uint16)
        spo2_raw = round(spo2 * 10)  # 0.1% resolution
        pulse_rate_raw = round(pulse_rate)  # 1 bpm resolution

        # Validate ranges
        if not 0 <= spo2_raw <= 0xFFFF:
            raise ValueError(f"SpO2 {spo2_raw} exceeds uint16 range")
        if not 0 <= pulse_rate_raw <= 0xFFFF:
            raise ValueError(f"Pulse rate {pulse_rate_raw} exceeds uint16 range")

        # Build result
        result = bytearray([int(flags)])
        result.extend(struct.pack("<H", spo2_raw))
        result.extend(struct.pack("<H", pulse_rate_raw))

        # Additional fields based on flags would be added (simplified)
        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "%"  # SpO2 is in percentage


# Alias for backward compatibility
PulseOximetryMeasurementCharacteristic = (
    PulseOximetryContinuousMeasurementCharacteristic
)
