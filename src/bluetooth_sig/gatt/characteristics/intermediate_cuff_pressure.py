"""Intermediate Cuff Pressure characteristic implementation."""

from __future__ import annotations

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


class IntermediateCuffPressureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Intermediate Cuff Pressure characteristic."""

    current_cuff_pressure: float
    unit: PressureUnit
    optional_fields: BloodPressureOptionalFields = BloodPressureOptionalFields()
    flags: BloodPressureFlags = BloodPressureFlags(0)

    def __post_init__(self) -> None:
        """Validate intermediate cuff pressure data."""
        if self.unit not in (PressureUnit.MMHG, PressureUnit.KPA):
            raise ValueError(f"Cuff pressure unit must be MMHG or KPA, got {self.unit}")

        if self.unit == PressureUnit.MMHG:
            valid_range = (0, BLOOD_PRESSURE_MAX_MMHG)
        else:  # kPa
            valid_range = (0, BLOOD_PRESSURE_MAX_KPA)

        if not valid_range[0] <= self.current_cuff_pressure <= valid_range[1]:
            raise ValueError(
                f"Current cuff pressure {self.current_cuff_pressure} {self.unit.value} is outside valid range "
                f"({valid_range[0]}-{valid_range[1]} {self.unit.value})"
            )


class IntermediateCuffPressureCharacteristic(BaseBloodPressureCharacteristic):
    """Intermediate Cuff Pressure characteristic (0x2A36).

    Used to transmit intermediate cuff pressure values during a blood
    pressure measurement process.

    SIG Specification Pattern:
    This characteristic can use Blood Pressure Feature (0x2A49) to interpret
    which status flags are supported by the device.
    """

    _is_base_class = False  # This is a concrete characteristic class

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> IntermediateCuffPressureData:  # pylint: disable=too-many-locals
        """Parse intermediate cuff pressure data according to Bluetooth specification.

        Format: Flags(1) + Current Cuff Pressure(2) + Unused(2) + Unused(2) + [Timestamp(7)] +
        [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)].
        All pressure values are IEEE-11073 16-bit SFLOAT. Unused fields are set to NaN.

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing access to Blood Pressure Feature characteristic
                for validating which measurement status flags are supported

        Returns:
            IntermediateCuffPressureData containing parsed cuff pressure data with metadata

        SIG Pattern:
        When context is available, can validate that measurement status flags are
        within the device's supported features as indicated by Blood Pressure Feature.

        """
        if len(data) < 7:
            raise ValueError("Intermediate Cuff Pressure data must be at least 7 bytes")

        flags = self._parse_blood_pressure_flags(data)

        # Parse required fields
        current_cuff_pressure = IEEE11073Parser.parse_sfloat(data, 1)
        unit = self._parse_blood_pressure_unit(flags)

        # Skip unused fields (bytes 3-6, should be NaN but we don't validate here)

        # Parse optional fields
        timestamp, pulse_rate, user_id, measurement_status = self._parse_optional_fields(data, flags)

        # Create immutable struct with all values
        return IntermediateCuffPressureData(
            current_cuff_pressure=current_cuff_pressure,
            unit=unit,
            optional_fields=BloodPressureOptionalFields(
                timestamp=timestamp,
                pulse_rate=pulse_rate,
                user_id=user_id,
                measurement_status=measurement_status,
            ),
            flags=flags,
        )

    def encode_value(self, data: IntermediateCuffPressureData) -> bytearray:
        """Encode IntermediateCuffPressureData back to bytes.

        Args:
            data: IntermediateCuffPressureData instance to encode

        Returns:
            Encoded bytes representing the intermediate cuff pressure

        """
        result = bytearray()

        flags = self._encode_blood_pressure_flags(data, data.optional_fields)
        result.append(flags)

        result.extend(IEEE11073Parser.encode_sfloat(data.current_cuff_pressure))
        # Add unused fields as NaN
        result.extend(IEEE11073Parser.encode_sfloat(float("nan")))
        result.extend(IEEE11073Parser.encode_sfloat(float("nan")))

        self._encode_optional_fields(result, data.optional_fields)

        return result
