"""Glucose Measurement characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class GlucoseMeasurementCharacteristic(BaseCharacteristic):
    """Glucose Measurement characteristic (0x2A18).

    Used to transmit glucose concentration measurements with timestamps and status.
    Core characteristic for glucose monitoring devices.
    """

    _characteristic_name: str = "Glucose Measurement"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(
        self, data: bytearray
    ) -> dict[str, Any]:  # pylint: disable=too-many-locals
        """Parse glucose measurement data according to Bluetooth specification.

        Format: Flags(1) + Sequence Number(2) + Base Time(7) + [Time Offset(2)] +
                Glucose Concentration(2) + [Type-Sample Location(1)] + [Sensor Status(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed glucose measurement data with metadata

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 12:
            raise ValueError("Glucose Measurement data must be at least 12 bytes")

        flags = data[0]
        offset = 1

        # Parse sequence number (2 bytes)
        sequence_number = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2

        # Parse base time (7 bytes) - IEEE-11073 timestamp
        base_time = self._parse_ieee11073_timestamp(data, offset)
        offset += 7

        result = {
            "sequence_number": sequence_number,
            "base_time": base_time,
            "flags": flags,
        }

        # Parse optional time offset (2 bytes) if present
        if (flags & 0x01) and len(data) >= offset + 2:
            time_offset = struct.unpack("<h", data[offset : offset + 2])[0]  # signed
            result["time_offset_minutes"] = time_offset
            offset += 2

        # Parse glucose concentration (2 bytes) - IEEE-11073 SFLOAT
        if len(data) >= offset + 2:
            glucose_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            glucose_value = self._parse_ieee11073_sfloat(glucose_raw)

            # Determine unit based on flags
            unit = "mmol/L" if (flags & 0x02) else "mg/dL"  # mmol/L vs mg/dL

            result.update(
                {
                    "glucose_concentration": glucose_value,
                    "unit": unit,
                }
            )
            offset += 2

        # Parse optional type and sample location (1 byte) if present
        if (flags & 0x04) and len(data) >= offset + 1:
            type_sample = data[offset]
            glucose_type = (type_sample >> 4) & 0x0F
            sample_location = type_sample & 0x0F
            result.update(
                {
                    "glucose_type": glucose_type,
                    "sample_location": sample_location,
                }
            )
            offset += 1

        # Parse optional sensor status annotation (2 bytes) if present
        if (flags & 0x08) and len(data) >= offset + 2:
            sensor_status = struct.unpack("<H", data[offset : offset + 2])[0]
            result["sensor_status"] = sensor_status

        return result

    def _get_glucose_type_name(self, glucose_type: int) -> str:
        """Get human-readable glucose type name."""
        types = {
            1: "Capillary Whole blood",
            2: "Capillary Plasma",
            3: "Venous Whole blood",
            4: "Venous Plasma",
            5: "Arterial Whole blood",
            6: "Arterial Plasma",
            7: "Undetermined Whole blood",
            8: "Undetermined Plasma",
            9: "Interstitial Fluid (ISF)",
            10: "Control Solution",
        }
        return types.get(glucose_type, "Reserved")

    def _get_sample_location_name(self, sample_location: int) -> str:
        """Get human-readable sample location name."""
        locations = {
            1: "Finger",
            2: "Alternate Site Test (AST)",
            3: "Earlobe",
            4: "Control solution",
            15: "Sample Location value not available",
        }
        return locations.get(sample_location, "Reserved")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mg/dL or mmol/L"  # Unit depends on flags
