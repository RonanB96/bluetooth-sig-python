"""Blood Pressure Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class BloodPressureMeasurementCharacteristic(BaseCharacteristic):
    """Blood Pressure Measurement characteristic (0x2A35).

    Used to transmit blood pressure measurements with systolic, diastolic and mean arterial pressure.
    """

    _characteristic_name: str = "Blood Pressure Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse blood pressure measurement data according to Bluetooth specification.

        Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] + [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)]
        All pressure values are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed blood pressure data with metadata
        """
        if len(data) < 7:
            raise ValueError("Blood Pressure Measurement data must be at least 7 bytes")

        flags = data[0]

        # Parse pressure values (IEEE-11073 16-bit SFLOAT)
        systolic_raw = struct.unpack("<H", data[1:3])[0]
        diastolic_raw = struct.unpack("<H", data[3:5])[0]
        map_raw = struct.unpack("<H", data[5:7])[0]

        # Convert SFLOAT to float (simplified conversion)
        systolic = self._sfloat_to_float(systolic_raw)
        diastolic = self._sfloat_to_float(diastolic_raw)
        mean_arterial_pressure = self._sfloat_to_float(map_raw)

        # Check pressure unit flag (bit 0)
        unit = "kPa" if (flags & 0x01) else "mmHg"

        result = {
            "systolic": systolic,
            "diastolic": diastolic,
            "mean_arterial_pressure": mean_arterial_pressure,
            "unit": unit,
            "flags": flags,
        }

        offset = 7

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 7:
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

        # Parse optional pulse rate (2 bytes) if present
        if (flags & 0x04) and len(data) >= offset + 2:
            pulse_rate_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            result["pulse_rate"] = self._sfloat_to_float(pulse_rate_raw)
            offset += 2

        # Parse optional user ID (1 byte) if present
        if (flags & 0x08) and len(data) >= offset + 1:
            result["user_id"] = data[offset]
            offset += 1

        # Parse optional measurement status (2 bytes) if present
        if (flags & 0x10) and len(data) >= offset + 2:
            result["measurement_status"] = struct.unpack(
                "<H", data[offset : offset + 2]
            )[0]

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
        return "mmHg/kPa"  # Unit depends on flags

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "pressure"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
