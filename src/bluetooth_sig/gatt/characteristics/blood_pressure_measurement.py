"""Blood Pressure Measurement characteristic implementation."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import datetime

from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# TODO: Implement CharacteristicContext support
# This characteristic should access Blood Pressure Feature (0x2A49) from ctx.other_characteristics
# to provide calibration factors and device capability information


@dataclass
class BloodPressureData:  # pylint: disable=too-many-instance-attributes
    """Parsed data from Blood Pressure Measurement characteristic."""

    systolic: float  # Systolic pressure
    diastolic: float  # Diastolic pressure
    mean_arterial_pressure: float  # Mean arterial pressure
    unit: str  # "mmHg" or "kPa"
    timestamp: datetime | None = None  # Optional timestamp
    pulse_rate: float | None = None  # Optional pulse rate
    user_id: int | None = None  # Optional user ID
    measurement_status: int | None = None  # Optional measurement status
    flags: int = 0  # Raw flags byte for reference

    def __post_init__(self) -> None:
        """Validate blood pressure data."""
        if self.unit not in ("mmHg", "kPa"):
            raise ValueError(
                f"Blood pressure unit must be 'mmHg' or 'kPa', got {self.unit}"
            )

        # Validate pressure ranges based on unit
        if self.unit == "mmHg":
            valid_range = (0, 300)  # Typical medical range for mmHg
        else:  # kPa
            valid_range = (0, 40)  # Equivalent range in kPa

        for name, value in [
            ("systolic", self.systolic),
            ("diastolic", self.diastolic),
            ("mean_arterial_pressure", self.mean_arterial_pressure),
        ]:
            if not valid_range[0] <= value <= valid_range[1]:
                raise ValueError(
                    f"{name} pressure {value} {self.unit} is outside valid range "
                    f"({valid_range[0]}-{valid_range[1]} {self.unit})"
                )


@dataclass
class BloodPressureMeasurementCharacteristic(BaseCharacteristic):
    """Blood Pressure Measurement characteristic (0x2A35).

    Used to transmit blood pressure measurements with systolic, diastolic and mean arterial pressure.
    """

    _characteristic_name: str = "Blood Pressure Measurement"

    def decode_value(self, data: bytearray) -> BloodPressureData:  # pylint: disable=too-many-locals
        """Parse blood pressure measurement data according to Bluetooth specification.

        Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] +
        [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)]
        All pressure values are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            BloodPressureData containing parsed blood pressure data with metadata
        """
        if len(data) < 7:
            raise ValueError("Blood Pressure Measurement data must be at least 7 bytes")

        flags = data[0]

        # Parse pressure values using IEEE-11073 SFLOAT format
        # Create basic result
        result_data = BloodPressureData(
            systolic=IEEE11073Parser.parse_sfloat(data, 1),
            diastolic=IEEE11073Parser.parse_sfloat(data, 3),
            mean_arterial_pressure=IEEE11073Parser.parse_sfloat(data, 5),
            unit="kPa" if flags & 0x01 else "mmHg",  # Units flag
            flags=flags,
        )

        offset = 7

        # Parse optional timestamp (7 bytes) if present
        if (flags & 0x02) and len(data) >= offset + 7:
            result_data.timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional pulse rate (2 bytes) if present
        if (flags & 0x04) and len(data) >= offset + 2:
            result_data.pulse_rate = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Parse optional user ID (1 byte) if present
        if (flags & 0x08) and len(data) >= offset + 1:
            result_data.user_id = data[offset]
            offset += 1

        # Parse optional measurement status (2 bytes) if present
        if (flags & 0x10) and len(data) >= offset + 2:
            result_data.measurement_status = struct.unpack(
                "<H", data[offset : offset + 2]
            )[0]

        return result_data

    def encode_value(self, data: BloodPressureData) -> bytearray:
        """Encode BloodPressureData back to bytes.

        Args:
            data: BloodPressureData instance to encode

        Returns:
            Encoded bytes representing the blood pressure measurement
        """
        result = bytearray()

        # Construct flags based on what data is present
        flags = 0
        if data.unit == "kPa":
            flags |= 0x01  # Units flag
        if data.timestamp is not None:
            flags |= 0x02  # Timestamp present
        if data.pulse_rate is not None:
            flags |= 0x04  # Pulse rate present
        if data.user_id is not None:
            flags |= 0x08  # User ID present
        if data.measurement_status is not None:
            flags |= 0x10  # Measurement status present

        result.append(flags)

        # Encode pressure values as IEEE-11073 SFLOAT
        result.extend(IEEE11073Parser.encode_sfloat(data.systolic))
        result.extend(IEEE11073Parser.encode_sfloat(data.diastolic))
        result.extend(IEEE11073Parser.encode_sfloat(data.mean_arterial_pressure))

        # Add optional fields
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        if data.pulse_rate is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        if data.user_id is not None:
            result.append(data.user_id)

        if data.measurement_status is not None:
            result.extend(
                DataParser.encode_int16(data.measurement_status, signed=False)
            )

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mmHg/kPa"  # Unit depends on flags
