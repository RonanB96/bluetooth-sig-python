"""Blood Pressure Measurement characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.types.units import PressureUnit

from ..context import CharacteristicContext
from .blood_pressure_common import (
    BLOOD_PRESSURE_MAX_KPA,
    BLOOD_PRESSURE_MAX_MMHG,
    BaseBloodPressureCharacteristic,
    BloodPressureFlags,
    BloodPressureOptionalFields,
)
from .utils import IEEE11073Parser


class BloodPressureMeasurementStatus(IntFlag):
    """Blood Pressure Measurement Status flags as per Bluetooth SIG specification."""

    BODY_MOVEMENT_DETECTED = 0x0001
    CUFF_TOO_LOOSE = 0x0002
    IRREGULAR_PULSE_DETECTED = 0x0004
    PULSE_RATE_OUT_OF_RANGE = 0x0008
    IMPROPER_MEASUREMENT_POSITION = 0x0010


class BloodPressureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Blood Pressure Measurement characteristic."""

    systolic: float
    diastolic: float
    mean_arterial_pressure: float
    unit: PressureUnit
    optional_fields: BloodPressureOptionalFields = BloodPressureOptionalFields()
    flags: BloodPressureFlags = BloodPressureFlags(0)

    def __post_init__(self) -> None:
        """Validate blood pressure data."""
        if self.unit not in (PressureUnit.MMHG, PressureUnit.KPA):
            raise ValueError(f"Blood pressure unit must be MMHG or KPA, got {self.unit}")

        if self.unit == PressureUnit.MMHG:
            valid_range = (0, BLOOD_PRESSURE_MAX_MMHG)
        else:  # kPa
            valid_range = (0, BLOOD_PRESSURE_MAX_KPA)

        for name, value in [
            ("systolic", self.systolic),
            ("diastolic", self.diastolic),
            ("mean_arterial_pressure", self.mean_arterial_pressure),
        ]:
            if not valid_range[0] <= value <= valid_range[1]:
                raise ValueError(
                    f"{name} pressure {value} {self.unit.value} is outside valid range "
                    f"({valid_range[0]}-{valid_range[1]} {self.unit.value})"
                )


class BloodPressureMeasurementCharacteristic(BaseBloodPressureCharacteristic):
    """Blood Pressure Measurement characteristic (0x2A35).

    Used to transmit blood pressure measurements with systolic,
    diastolic and mean arterial pressure.

    SIG Specification Pattern:
    This characteristic can use Blood Pressure Feature (0x2A49) to interpret
    which status flags are supported by the device.
    """

    _is_base_class = False  # This is a concrete characteristic class

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BloodPressureData:  # pylint: disable=too-many-locals
        """Parse blood pressure measurement data according to Bluetooth specification.

        Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] +
        [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)].
        All pressure values are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing access to Blood Pressure Feature characteristic
                for validating which measurement status flags are supported

        Returns:
            BloodPressureData containing parsed blood pressure data with metadata

        SIG Pattern:
        When context is available, can validate that measurement status flags are
        within the device's supported features as indicated by Blood Pressure Feature.

        """
        if len(data) < 7:
            raise ValueError("Blood Pressure Measurement data must be at least 7 bytes")

        flags = self._parse_blood_pressure_flags(data)

        # Parse required fields
        systolic = IEEE11073Parser.parse_sfloat(data, 1)
        diastolic = IEEE11073Parser.parse_sfloat(data, 3)
        mean_arterial_pressure = IEEE11073Parser.parse_sfloat(data, 5)
        unit = self._parse_blood_pressure_unit(flags)

        # Parse optional fields
        timestamp, pulse_rate, user_id, measurement_status = self._parse_optional_fields(data, flags)

        # Create immutable struct with all values
        return BloodPressureData(  # pylint: disable=duplicate-code  # Similar structure in intermediate_cuff_pressure (same optional fields by spec)
            systolic=systolic,
            diastolic=diastolic,
            mean_arterial_pressure=mean_arterial_pressure,
            unit=unit,
            optional_fields=BloodPressureOptionalFields(
                timestamp=timestamp,
                pulse_rate=pulse_rate,
                user_id=user_id,
                measurement_status=measurement_status,
            ),
            flags=flags,
        )

    def encode_value(self, data: BloodPressureData) -> bytearray:
        """Encode BloodPressureData back to bytes.

        Args:
            data: BloodPressureData instance to encode

        Returns:
            Encoded bytes representing the blood pressure measurement

        """
        return self._encode_blood_pressure_base(
            data,
            data.optional_fields,
            [data.systolic, data.diastolic, data.mean_arterial_pressure],
        )
