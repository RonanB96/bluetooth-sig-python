"""Shared constants and types for blood pressure characteristics."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag
from typing import Any, ClassVar, Protocol

import msgspec

from bluetooth_sig.types.units import PressureUnit

from .base import BaseCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .utils import DataParser, IEEE11073Parser

# Bluetooth SIG Blood Pressure Service specification constants
BLOOD_PRESSURE_MAX_MMHG = 300  # Maximum blood pressure in mmHg
BLOOD_PRESSURE_MAX_KPA = 40  # Maximum blood pressure in kPa


class BloodPressureFlags(IntFlag):
    """Blood Pressure flags as per Bluetooth SIG specification."""

    UNITS_KPA = 0x01
    TIMESTAMP_PRESENT = 0x02
    PULSE_RATE_PRESENT = 0x04
    USER_ID_PRESENT = 0x08
    MEASUREMENT_STATUS_PRESENT = 0x10


class BloodPressureOptionalFields(msgspec.Struct, frozen=True, kw_only=True):
    """Optional fields common to blood pressure characteristics."""

    timestamp: datetime | None = None
    pulse_rate: float | None = None
    user_id: int | None = None
    measurement_status: int | None = None


class BloodPressureDataProtocol(Protocol):
    """Protocol for blood pressure data structs with unit field."""

    @property
    def unit(self) -> PressureUnit:
        """Pressure unit for blood pressure measurement."""


class BaseBloodPressureCharacteristic(BaseCharacteristic[Any]):
    """Base class for blood pressure characteristics with common parsing logic."""

    _is_base_class = True  # Exclude from characteristic discovery

    _manual_value_type = "string"  # Override since decode_value returns dataclass

    # Declare optional dependency on Blood Pressure Feature for status interpretation
    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [BloodPressureFeatureCharacteristic]

    min_length = 7  # Flags(1) + Pressure values minimum
    max_length = 19  # + Timestamp(7) + PulseRate(2) + UserID(1) + MeasurementStatus(2) maximum
    allow_variable_length: bool = True  # Variable optional fields

    @staticmethod
    def _parse_blood_pressure_flags(data: bytearray) -> BloodPressureFlags:
        """Parse blood pressure flags from data."""
        return BloodPressureFlags(data[0])

    @staticmethod
    def _parse_blood_pressure_unit(flags: BloodPressureFlags) -> PressureUnit:
        """Parse pressure unit from flags."""
        return PressureUnit.KPA if flags & BloodPressureFlags.UNITS_KPA else PressureUnit.MMHG

    @staticmethod
    def _parse_optional_fields(
        data: bytearray, flags: BloodPressureFlags, start_offset: int = 7
    ) -> tuple[datetime | None, float | None, int | None, int | None]:
        """Parse optional fields from blood pressure data.

        Returns:
            Tuple of (timestamp, pulse_rate, user_id, measurement_status)
        """
        timestamp: datetime | None = None
        pulse_rate: float | None = None
        user_id: int | None = None
        measurement_status: int | None = None
        offset = start_offset

        if (flags & BloodPressureFlags.TIMESTAMP_PRESENT) and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if (flags & BloodPressureFlags.PULSE_RATE_PRESENT) and len(data) >= offset + 2:
            pulse_rate = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        if (flags & BloodPressureFlags.USER_ID_PRESENT) and len(data) >= offset + 1:
            user_id = data[offset]
            offset += 1

        if (flags & BloodPressureFlags.MEASUREMENT_STATUS_PRESENT) and len(data) >= offset + 2:
            measurement_status = DataParser.parse_int16(data, offset, signed=False)

        return timestamp, pulse_rate, user_id, measurement_status

    @staticmethod
    def _encode_blood_pressure_flags(
        data: BloodPressureDataProtocol,
        optional_fields: BloodPressureOptionalFields,
    ) -> int:
        """Encode flags from blood pressure data struct and optional fields."""
        flags = 0
        if data.unit == PressureUnit.KPA:
            flags |= BloodPressureFlags.UNITS_KPA
        if optional_fields.timestamp is not None:
            flags |= BloodPressureFlags.TIMESTAMP_PRESENT
        if optional_fields.pulse_rate is not None:
            flags |= BloodPressureFlags.PULSE_RATE_PRESENT
        if optional_fields.user_id is not None:
            flags |= BloodPressureFlags.USER_ID_PRESENT
        if optional_fields.measurement_status is not None:
            flags |= BloodPressureFlags.MEASUREMENT_STATUS_PRESENT
        return flags

    @staticmethod
    def _encode_optional_fields(result: bytearray, optional_fields: BloodPressureOptionalFields) -> None:
        """Encode optional fields to result bytearray."""
        if optional_fields.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(optional_fields.timestamp))

        if optional_fields.pulse_rate is not None:
            result.extend(IEEE11073Parser.encode_sfloat(optional_fields.pulse_rate))

        if optional_fields.user_id is not None:
            result.append(optional_fields.user_id)

        if optional_fields.measurement_status is not None:
            result.extend(DataParser.encode_int16(optional_fields.measurement_status, signed=False))

    def _encode_blood_pressure_base(
        self,
        data: BloodPressureDataProtocol,
        optional_fields: BloodPressureOptionalFields,
        pressure_values: list[float],
    ) -> bytearray:
        """Common encoding logic for blood pressure characteristics.

        Args:
            data: Blood pressure data with unit field
            optional_fields: Optional fields to encode
            pressure_values: List of pressure values to encode (1-3 SFLOAT values)

        Returns:
            Encoded bytearray
        """
        result = bytearray()

        flags = self._encode_blood_pressure_flags(data, optional_fields)
        result.append(flags)

        for value in pressure_values:
            result.extend(IEEE11073Parser.encode_sfloat(value))

        self._encode_optional_fields(result, optional_fields)

        return result
