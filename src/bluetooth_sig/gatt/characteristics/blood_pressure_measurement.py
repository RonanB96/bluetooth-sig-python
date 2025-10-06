"""Blood Pressure Measurement characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class BloodPressureFlags(IntFlag):
    """Blood Pressure Measurement flags as per Bluetooth SIG specification."""

    UNITS_KPA = 0x01
    TIMESTAMP_PRESENT = 0x02
    PULSE_RATE_PRESENT = 0x04
    USER_ID_PRESENT = 0x08
    MEASUREMENT_STATUS_PRESENT = 0x10


class BloodPressureMeasurementStatus(IntFlag):
    """Blood Pressure Measurement Status flags as per Bluetooth SIG
    specification."""

    BODY_MOVEMENT_DETECTED = 0x0001
    CUFF_TOO_LOOSE = 0x0002
    IRREGULAR_PULSE_DETECTED = 0x0004
    PULSE_RATE_OUT_OF_RANGE = 0x0008
    IMPROPER_MEASUREMENT_POSITION = 0x0010


@dataclass
class BloodPressureData:  # pylint: disable=too-many-instance-attributes
    """Parsed data from Blood Pressure Measurement characteristic."""

    systolic: float
    diastolic: float
    mean_arterial_pressure: float
    unit: str
    timestamp: datetime | None = None
    pulse_rate: float | None = None
    user_id: int | None = None
    measurement_status: int | None = None
    flags: int = 0

    def __post_init__(self) -> None:
        """Validate blood pressure data."""
        if self.unit not in ("mmHg", "kPa"):
            raise ValueError(f"Blood pressure unit must be 'mmHg' or 'kPa', got {self.unit}")

        if self.unit == "mmHg":
            valid_range = (0, 300)
        else:  # kPa
            valid_range = (0, 40)

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


class BloodPressureMeasurementCharacteristic(BaseCharacteristic):
    """Blood Pressure Measurement characteristic (0x2A35).

    Used to transmit blood pressure measurements with systolic,
    diastolic and mean arterial pressure.
    """

    _manual_value_type = "string"  # Override since decode_value returns dataclass

    min_length = 7  # Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) minimum
    max_length = 19  # + Timestamp(7) + PulseRate(2) + UserID(1) + MeasurementStatus(2) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(self, data: bytearray, _ctx: CharacteristicContext | None = None) -> BloodPressureData:  # pylint: disable=too-many-locals
        """Parse blood pressure measurement data according to Bluetooth
        specification.

        Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] +
        [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)]
        All pressure values are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing access to device features and other characteristics

        Returns:
            BloodPressureData containing parsed blood pressure data with metadata
        """
        if len(data) < 7:
            raise ValueError("Blood Pressure Measurement data must be at least 7 bytes")

        flags = data[0]

        result_data = BloodPressureData(
            systolic=IEEE11073Parser.parse_sfloat(data, 1),
            diastolic=IEEE11073Parser.parse_sfloat(data, 3),
            mean_arterial_pressure=IEEE11073Parser.parse_sfloat(data, 5),
            unit="kPa" if flags & BloodPressureFlags.UNITS_KPA else "mmHg",
            flags=flags,
        )

        offset = 7

        if (flags & BloodPressureFlags.TIMESTAMP_PRESENT) and len(data) >= offset + 7:
            result_data.timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if (flags & BloodPressureFlags.PULSE_RATE_PRESENT) and len(data) >= offset + 2:
            result_data.pulse_rate = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        if (flags & BloodPressureFlags.USER_ID_PRESENT) and len(data) >= offset + 1:
            result_data.user_id = data[offset]
            offset += 1

        if (flags & BloodPressureFlags.MEASUREMENT_STATUS_PRESENT) and len(data) >= offset + 2:
            result_data.measurement_status = DataParser.parse_int16(data, offset, signed=False)

        return result_data

    def encode_value(self, data: BloodPressureData) -> bytearray:
        """Encode BloodPressureData back to bytes.

        Args:
            data: BloodPressureData instance to encode

        Returns:
            Encoded bytes representing the blood pressure measurement
        """
        result = bytearray()

        flags = 0
        if data.unit == "kPa":
            flags |= BloodPressureFlags.UNITS_KPA
        if data.timestamp is not None:
            flags |= BloodPressureFlags.TIMESTAMP_PRESENT
        if data.pulse_rate is not None:
            flags |= BloodPressureFlags.PULSE_RATE_PRESENT
        if data.user_id is not None:
            flags |= BloodPressureFlags.USER_ID_PRESENT
        if data.measurement_status is not None:
            flags |= BloodPressureFlags.MEASUREMENT_STATUS_PRESENT

        result.append(flags)

        result.extend(IEEE11073Parser.encode_sfloat(data.systolic))
        result.extend(IEEE11073Parser.encode_sfloat(data.diastolic))
        result.extend(IEEE11073Parser.encode_sfloat(data.mean_arterial_pressure))

        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        if data.pulse_rate is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        if data.user_id is not None:
            result.append(data.user_id)

        if data.measurement_status is not None:
            result.extend(DataParser.encode_int16(data.measurement_status, signed=False))

        return result
