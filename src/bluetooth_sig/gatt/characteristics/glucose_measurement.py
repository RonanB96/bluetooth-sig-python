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

    def parse_value(self, data: bytearray) -> dict[str, Any]:  # pylint: disable=too-many-locals
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

    def encode_value(self, data: dict[str, Any]) -> bytearray:  # pylint: disable=too-many-locals,too-many-branches # Complex medical data encoding
        """Encode glucose measurement value back to bytes.

        Args:
            data: Dictionary containing glucose measurement data

        Returns:
            Encoded bytes representing the glucose measurement
        """
        if not isinstance(data, dict):
            raise TypeError("Glucose measurement data must be a dictionary")

        required_fields = ["sequence_number", "base_time", "glucose_concentration"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Glucose measurement data must contain '{field}' key")

        sequence_number = int(data["sequence_number"])
        base_time = data["base_time"]
        glucose_concentration = float(data["glucose_concentration"])

        time_offset = data.get("time_offset")
        type_sample_location = data.get("type_sample_location")
        sensor_status = data.get("sensor_status")

        # Build flags based on available data
        flags = 0
        if time_offset is not None:
            flags |= 0x01  # Time offset present
        if type_sample_location is not None:
            flags |= 0x02  # Type and sample location present
        if glucose_concentration >= 0:  # Glucose concentration units
            flags |= 0x04  # Units flag (simplified)
        if sensor_status is not None:
            flags |= 0x08  # Sensor status annunciation present

        # Validate ranges
        if not 0 <= sequence_number <= 0xFFFF:
            raise ValueError(f"Sequence number {sequence_number} exceeds uint16 range")

        # Convert glucose concentration to SFLOAT (simplified as uint16)
        glucose_raw = round(glucose_concentration * 100)  # Simplified conversion
        if not 0 <= glucose_raw <= 0xFFFF:
            raise ValueError(
                f"Glucose concentration {glucose_raw} exceeds uint16 range"
            )

        # Start with flags, sequence number, and base time
        result = bytearray([flags])
        result.extend(struct.pack("<H", sequence_number))
        result.extend(self._encode_ieee11073_timestamp(base_time))

        # Add optional time offset
        if time_offset is not None:
            offset_val = int(time_offset)
            if not -32768 <= offset_val <= 32767:
                raise ValueError(f"Time offset {offset_val} exceeds sint16 range")
            result.extend(struct.pack("<h", offset_val))

        # Add glucose concentration (simplified as uint16)
        result.extend(struct.pack("<H", glucose_raw))

        # Add optional type and sample location
        if type_sample_location is not None:
            type_location = int(type_sample_location)
            if not 0 <= type_location <= 255:
                raise ValueError(
                    f"Type sample location {type_location} exceeds uint8 range"
                )
            result.append(type_location)

        # Add optional sensor status
        if sensor_status is not None:
            status = int(sensor_status)
            if not 0 <= status <= 0xFFFF:
                raise ValueError(f"Sensor status {status} exceeds uint16 range")
            result.extend(struct.pack("<H", status))

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
