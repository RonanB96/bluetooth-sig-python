"""Pulse Oximetry Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class PulseOximetryMeasurementCharacteristic(BaseCharacteristic):
    """PLX Continuous Measurement characteristic (0x2A5F).

    Used to transmit SpO2 (blood oxygen saturation) and pulse rate measurements.
    """

    _characteristic_name: str = "PLX Continuous Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse pulse oximetry measurement data according to Bluetooth specification.

        Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Timestamp(7)] + [Measurement Status(2)] + [Device Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed pulse oximetry data with metadata
        """
        if len(data) < 5:
            raise ValueError("Pulse Oximetry Measurement data must be at least 5 bytes")

        flags = data[0]

        # Parse SpO2 and Pulse Rate (IEEE-11073 16-bit SFLOAT)
        spo2_raw = struct.unpack("<H", data[1:3])[0]
        pulse_rate_raw = struct.unpack("<H", data[3:5])[0]

        spo2 = self._sfloat_to_float(spo2_raw)
        pulse_rate = self._sfloat_to_float(pulse_rate_raw)

        result = {"spo2": spo2, "pulse_rate": pulse_rate, "flags": flags}

        offset = 5

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x01) and len(data) >= offset + 7:
            timestamp_data = data[offset : offset + 7]
            year, month, day, hours, minutes, seconds = struct.unpack(
                "<HBBBBB", timestamp_data
            )
            result["timestamp"] = {
                "year": year,
                "month": month,
                "day": day,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
            }
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
            pai_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["pulse_amplitude_index"] = self._sfloat_to_float(pai_raw)

        return result

    def _sfloat_to_float(self, sfloat_val: int) -> float:
        """Convert IEEE-11073 16-bit SFLOAT to Python float (simplified)."""
        if sfloat_val == 0x07FF:  # NaN
            return float("nan")
        elif sfloat_val == 0x0800:  # NRes (Not a valid result)
            return float("nan")
        elif sfloat_val == 0x07FE:  # +INFINITY
            return float("inf")
        elif sfloat_val == 0x0802:  # -INFINITY
            return float("-inf")
        else:
            # Extract mantissa and exponent
            mantissa = sfloat_val & 0x0FFF
            exponent = (sfloat_val >> 12) & 0x0F

            # Handle negative mantissa
            if mantissa & 0x0800:
                mantissa = mantissa - 0x1000

            # Handle negative exponent
            if exponent & 0x08:
                exponent = exponent - 0x10

            return mantissa * (10**exponent)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "%"  # SpO2 is in percentage

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "blood_oxygen"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
