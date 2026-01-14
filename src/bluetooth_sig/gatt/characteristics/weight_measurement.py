"""Weight Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntFlag

import msgspec

from bluetooth_sig.types.units import HeightUnit, MeasurementSystem, WeightUnit

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class WeightMeasurementFlags(IntFlag):
    """Weight Measurement flags as per Bluetooth SIG specification."""

    IMPERIAL_UNITS = 0x01
    TIMESTAMP_PRESENT = 0x02
    USER_ID_PRESENT = 0x04
    BMI_PRESENT = 0x08
    HEIGHT_PRESENT = 0x10


class WeightMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed weight measurement data."""

    weight: float
    weight_unit: WeightUnit
    measurement_units: MeasurementSystem
    flags: WeightMeasurementFlags
    timestamp: datetime | None = None
    user_id: int | None = None
    bmi: float | None = None
    height: float | None = None
    height_unit: HeightUnit | None = None

    def __post_init__(self) -> None:  # pylint: disable=too-many-branches
        """Validate weight measurement data after initialization."""
        # Validate weight_unit consistency
        if self.measurement_units == MeasurementSystem.METRIC and self.weight_unit != WeightUnit.KG:
            raise ValueError(f"Metric units require weight_unit={WeightUnit.KG!r}, got {self.weight_unit!r}")
        if self.measurement_units == MeasurementSystem.IMPERIAL and self.weight_unit != WeightUnit.LB:
            raise ValueError(f"Imperial units require weight_unit={WeightUnit.LB!r}, got {self.weight_unit!r}")

        # Validate weight range
        if self.measurement_units == MeasurementSystem.METRIC:
            # Allow any non-negative weight (no SIG-specified range)
            if self.weight < 0:
                raise ValueError(f"Weight in kg must be non-negative, got {self.weight}")
        else:  # imperial
            # Allow any non-negative weight (no SIG-specified range)
            if self.weight < 0:
                raise ValueError(f"Weight in lb must be non-negative, got {self.weight}")

        # Validate height_unit consistency if height present
        if self.height is not None:
            if self.measurement_units == MeasurementSystem.METRIC and self.height_unit != HeightUnit.METERS:
                raise ValueError(f"Metric units require height_unit={HeightUnit.METERS!r}, got {self.height_unit!r}")
            if self.measurement_units == MeasurementSystem.IMPERIAL and self.height_unit != HeightUnit.INCHES:
                raise ValueError(f"Imperial units require height_unit={HeightUnit.INCHES!r}, got {self.height_unit!r}")

            # Validate height range
            if self.measurement_units == MeasurementSystem.METRIC:
                # Allow any non-negative height (no SIG-specified range)
                if self.height < 0:
                    raise ValueError(f"Height in m must be non-negative, got {self.height}")
            else:  # imperial
                # Allow any non-negative height (no SIG-specified range)
                if self.height < 0:
                    raise ValueError(f"Height in in must be non-negative, got {self.height}")

        # Validate BMI if present
        if self.bmi is not None:
            # Allow any non-negative BMI (no SIG-specified range)
            if self.bmi < 0:
                raise ValueError(f"BMI must be non-negative, got {self.bmi}")

        # Validate user_id if present
        if self.user_id is not None:
            if not 0 <= self.user_id <= 255:
                raise ValueError(f"User ID must be 0-255, got {self.user_id}")


class WeightMeasurementCharacteristic(BaseCharacteristic[WeightMeasurementData]):
    """Weight Measurement characteristic (0x2A9D).

    Used to transmit weight measurement data with optional fields.
    Supports metric/imperial units, timestamps, user ID, BMI, and
    height.
    """

    _characteristic_name: str = "Weight Measurement"
    _manual_unit: str = "kg"  # Primary unit for weight measurement

    min_length: int = 3  # Flags(1) + Weight(2) minimum
    max_length: int = 21  # + Timestamp(7) + UserID(1) + BMI(2) + Height(2) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> WeightMeasurementData:  # pylint: disable=too-many-locals
        """Parse weight measurement data according to Bluetooth specification.

        Format: Flags(1) + Weight(2) + [Timestamp(7)] + [User ID(1)] +
                [BMI(2)] + [Height(2)]

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            WeightMeasurementData containing parsed weight measurement data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 3:
            raise ValueError("Weight Measurement data must be at least 3 bytes")

        flags = WeightMeasurementFlags(data[0])
        offset = 1

        # Parse weight value (uint16 with 0.005 kg resolution)
        if len(data) < offset + 2:
            raise ValueError("Insufficient data for weight value")
        weight_raw = DataParser.parse_int16(data, offset, signed=False)
        offset += 2

        # Convert to appropriate unit based on flags
        if WeightMeasurementFlags.IMPERIAL_UNITS in flags:  # Imperial units (pounds)
            weight = weight_raw * 0.01  # 0.01 lb resolution for imperial
            weight_unit = WeightUnit.LB
            measurement_units = MeasurementSystem.IMPERIAL
        else:  # SI units (kilograms)
            weight = weight_raw * 0.005  # 0.005 kg resolution for metric
            weight_unit = WeightUnit.KG
            measurement_units = MeasurementSystem.METRIC

        # Parse optional timestamp (7 bytes) if present
        timestamp = None
        if WeightMeasurementFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        # Parse optional user ID (1 byte) if present
        user_id = None
        if WeightMeasurementFlags.USER_ID_PRESENT in flags and len(data) >= offset + 1:
            user_id = int(data[offset])
            offset += 1

        # Parse optional BMI (uint16 with 0.1 resolution) if present
        bmi = None
        if WeightMeasurementFlags.BMI_PRESENT in flags and len(data) >= offset + 2:
            bmi_raw = DataParser.parse_int16(data, offset, signed=False)
            bmi = bmi_raw * 0.1
            offset += 2

        # Parse optional height (uint16 with 0.001m resolution) if present
        height = None
        height_unit = None
        if WeightMeasurementFlags.HEIGHT_PRESENT in flags and len(data) >= offset + 2:
            height_raw = DataParser.parse_int16(data, offset, signed=False)
            if WeightMeasurementFlags.IMPERIAL_UNITS in flags:  # Imperial units (inches)
                height = height_raw * 0.1  # 0.1 inch resolution
                height_unit = HeightUnit.INCHES
            else:  # SI units (meters)
                height = height_raw * 0.001  # 0.001 m resolution
                height_unit = HeightUnit.METERS
            offset += 2

        # Create result with all parsed values
        return WeightMeasurementData(
            weight=weight,
            weight_unit=weight_unit,
            measurement_units=measurement_units,
            flags=flags,
            timestamp=timestamp,
            user_id=user_id,
            bmi=bmi,
            height=height,
            height_unit=height_unit,
        )

    def _encode_value(self, data: WeightMeasurementData) -> bytearray:  # pylint: disable=too-many-branches # Complex measurement data with many optional fields
        """Encode weight measurement value back to bytes.

        Args:
            data: WeightMeasurementData containing weight measurement data

        Returns:
            Encoded bytes representing the weight measurement

        """
        # Build flags based on available data
        flags = WeightMeasurementFlags(0)
        if data.measurement_units == MeasurementSystem.IMPERIAL:
            flags |= WeightMeasurementFlags.IMPERIAL_UNITS
        if data.timestamp is not None:
            flags |= WeightMeasurementFlags.TIMESTAMP_PRESENT
        if data.user_id is not None:
            flags |= WeightMeasurementFlags.USER_ID_PRESENT
        if data.bmi is not None:
            flags |= WeightMeasurementFlags.BMI_PRESENT
        if data.height is not None:
            flags |= WeightMeasurementFlags.HEIGHT_PRESENT

        # Convert weight to raw value based on units
        if WeightMeasurementFlags.IMPERIAL_UNITS in flags:  # Imperial units (pounds)
            weight_raw = round(data.weight / 0.01)  # 0.01 lb resolution
        else:  # SI units (kilograms)
            weight_raw = round(data.weight / 0.005)  # 0.005 kg resolution

        if not 0 <= weight_raw <= 0xFFFF:
            raise ValueError(f"Weight value {weight_raw} exceeds uint16 range")

        # Start with flags and weight
        result = bytearray([int(flags)])
        result.extend(DataParser.encode_int16(weight_raw, signed=False))

        # Add optional fields based on flags
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        if data.user_id is not None:
            if not 0 <= data.user_id <= UINT8_MAX:
                raise ValueError(f"User ID {data.user_id} exceeds uint8 range")
            result.append(data.user_id)

        if data.bmi is not None:
            bmi_raw = round(data.bmi / 0.1)  # 0.1 resolution
            if not 0 <= bmi_raw <= 0xFFFF:
                raise ValueError(f"BMI value {bmi_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(bmi_raw, signed=False))

        if data.height is not None:
            if WeightMeasurementFlags.IMPERIAL_UNITS in flags:  # Imperial units (inches)
                height_raw = round(data.height / 0.1)  # 0.1 inch resolution
            else:  # SI units (meters)
                height_raw = round(data.height / 0.001)  # 0.001 m resolution

            if not 0 <= height_raw <= 0xFFFF:
                raise ValueError(f"Height value {height_raw} exceeds uint16 range")
            result.extend(DataParser.encode_int16(height_raw, signed=False))

        return result
