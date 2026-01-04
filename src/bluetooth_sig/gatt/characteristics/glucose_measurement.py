"""Glucose Measurement characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum, IntFlag

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic, GlucoseFeatureData, GlucoseFeatures
from .utils import BitFieldUtils, DataParser, IEEE11073Parser


class GlucoseMeasurementBits:
    """Glucose measurement bit field constants."""

    # pylint: disable=missing-class-docstring,too-few-public-methods

    # Glucose Measurement bit field constants
    GLUCOSE_TYPE_SAMPLE_MASK = 0x0F  # 4-bit mask for type and sample location
    GLUCOSE_TYPE_START_BIT = 4  # Glucose type in high 4 bits
    GLUCOSE_TYPE_BIT_WIDTH = 4
    GLUCOSE_SAMPLE_LOCATION_START_BIT = 0  # Sample location in low 4 bits
    GLUCOSE_SAMPLE_LOCATION_BIT_WIDTH = 4


class GlucoseType(IntEnum):
    """Glucose sample type enumeration as per Bluetooth SIG specification."""

    CAPILLARY_WHOLE_BLOOD = 1
    CAPILLARY_PLASMA = 2
    VENOUS_WHOLE_BLOOD = 3
    VENOUS_PLASMA = 4
    ARTERIAL_WHOLE_BLOOD = 5
    ARTERIAL_PLASMA = 6
    UNDETERMINED_WHOLE_BLOOD = 7
    UNDETERMINED_PLASMA = 8
    INTERSTITIAL_FLUID = 9
    CONTROL_SOLUTION = 10
    # Values 11-15 (0xB-0xF) are Reserved for Future Use

    def __str__(self) -> str:
        """Return human-readable glucose type name."""
        names = {
            self.CAPILLARY_WHOLE_BLOOD: "Capillary Whole blood",
            self.CAPILLARY_PLASMA: "Capillary Plasma",
            self.VENOUS_WHOLE_BLOOD: "Venous Whole blood",
            self.VENOUS_PLASMA: "Venous Plasma",
            self.ARTERIAL_WHOLE_BLOOD: "Arterial Whole blood",
            self.ARTERIAL_PLASMA: "Arterial Plasma",
            self.UNDETERMINED_WHOLE_BLOOD: "Undetermined Whole blood",
            self.UNDETERMINED_PLASMA: "Undetermined Plasma",
            self.INTERSTITIAL_FLUID: "Interstitial Fluid (ISF)",
            self.CONTROL_SOLUTION: "Control Solution",
        }
        return names[self]


class SampleLocation(IntEnum):
    """Sample location enumeration as per Bluetooth SIG specification."""

    # Value 0 is Reserved for Future Use
    FINGER = 1
    ALTERNATE_SITE_TEST = 2
    EARLOBE = 3
    CONTROL_SOLUTION = 4
    # Values 5-14 (0x5-0xE) are Reserved for Future Use
    NOT_AVAILABLE = 15

    def __str__(self) -> str:
        """Return human-readable sample location name."""
        names = {
            self.FINGER: "Finger",
            self.ALTERNATE_SITE_TEST: "Alternate Site Test (AST)",
            self.EARLOBE: "Earlobe",
            self.CONTROL_SOLUTION: "Control solution",
            self.NOT_AVAILABLE: "Sample Location value not available",
        }
        return names[self]


class GlucoseMeasurementFlags(IntFlag):
    """Glucose Measurement flags as per Bluetooth SIG specification."""

    TIME_OFFSET_PRESENT = 0x01
    GLUCOSE_CONCENTRATION_UNITS_MMOL_L = 0x02
    TYPE_SAMPLE_LOCATION_PRESENT = 0x04
    SENSOR_STATUS_ANNUNCIATION_PRESENT = 0x08


class GlucoseMeasurementData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed glucose measurement data."""

    sequence_number: int
    base_time: datetime
    glucose_concentration: float
    unit: str
    flags: GlucoseMeasurementFlags
    time_offset_minutes: int | None = None
    glucose_type: GlucoseType | None = None
    sample_location: SampleLocation | None = None
    sensor_status: int | None = None

    min_length: int = 12  # Aligned with GlucoseMeasurementCharacteristic
    max_length: int = 17  # Aligned with GlucoseMeasurementCharacteristic

    def __post_init__(self) -> None:
        """Validate glucose measurement data."""
        if self.unit not in ("mg/dL", "mmol/L"):
            raise ValueError(f"Glucose unit must be 'mg/dL' or 'mmol/L', got {self.unit}")

        # Validate concentration range based on unit
        if self.unit == "mg/dL":
            # Allow any non-negative value (no SIG-specified range)
            if self.glucose_concentration < 0:
                raise ValueError(f"Glucose concentration must be non-negative, got {self.glucose_concentration}")
        else:  # mmol/L
            # Allow any non-negative value (no SIG-specified range)
            if self.glucose_concentration < 0:
                raise ValueError(f"Glucose concentration must be non-negative, got {self.glucose_concentration}")

    @staticmethod
    def is_reserved_range(value: int) -> bool:
        """Check if glucose type or sample location is in reserved range."""
        return value in {0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}


class GlucoseMeasurementCharacteristic(BaseCharacteristic[GlucoseMeasurementData]):
    """Glucose Measurement characteristic (0x2A18).

    Used to transmit glucose concentration measurements with timestamps
    and status. Core characteristic for glucose monitoring devices.
    """

    _manual_unit: str = "mg/dL or mmol/L"  # Unit depends on flags

    _optional_dependencies = [GlucoseFeatureCharacteristic]

    min_length: int = 12  # Ensured consistency with GlucoseMeasurementData
    max_length: int = 17  # Ensured consistency with GlucoseMeasurementData
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> GlucoseMeasurementData:  # pylint: disable=too-many-locals
        """Parse glucose measurement data according to Bluetooth specification.

        Format: Flags(1) + Sequence Number(2) + Base Time(7) + [Time Offset(2)] +
                Glucose Concentration(2) + [Type-Sample Location(1)] + [Sensor Status(2)].

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            GlucoseMeasurementData containing parsed glucose measurement data with metadata.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < 12:
            raise ValueError("Glucose Measurement data must be at least 12 bytes")

        flags = GlucoseMeasurementFlags(data[0])
        offset = 1

        # Parse sequence number (2 bytes)
        sequence_number = DataParser.parse_int16(data, offset, signed=False)
        offset += 2

        # Parse base time (7 bytes) - IEEE-11073 timestamp
        base_time = IEEE11073Parser.parse_timestamp(data, offset)
        offset += 7

        # Parse optional time offset (2 bytes) if present
        time_offset_minutes = None
        if GlucoseMeasurementFlags.TIME_OFFSET_PRESENT in flags and len(data) >= offset + 2:
            time_offset_minutes = DataParser.parse_int16(data, offset, signed=True)  # signed
            offset += 2

        # Parse glucose concentration (2 bytes) - IEEE-11073 SFLOAT
        glucose_concentration = 0.0
        unit = "mg/dL"
        if len(data) >= offset + 2:
            glucose_concentration = IEEE11073Parser.parse_sfloat(data, offset)
            # Determine unit based on flags
            unit = "mmol/L" if GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L in flags else "mg/dL"
            offset += 2

        # Parse optional type and sample location (1 byte) if present
        glucose_type = None
        sample_location = None
        if GlucoseMeasurementFlags.TYPE_SAMPLE_LOCATION_PRESENT in flags and len(data) >= offset + 1:
            type_sample = data[offset]
            glucose_type_val = BitFieldUtils.extract_bit_field(
                type_sample,
                GlucoseMeasurementBits.GLUCOSE_TYPE_START_BIT,
                GlucoseMeasurementBits.GLUCOSE_TYPE_BIT_WIDTH,
            )
            sample_location_val = BitFieldUtils.extract_bit_field(
                type_sample,
                GlucoseMeasurementBits.GLUCOSE_SAMPLE_LOCATION_START_BIT,
                GlucoseMeasurementBits.GLUCOSE_SAMPLE_LOCATION_BIT_WIDTH,
            )

            glucose_type = GlucoseType(glucose_type_val)
            sample_location = SampleLocation(sample_location_val)

            offset += 1

        # Parse optional sensor status annotation (2 bytes) if present
        sensor_status = None
        if GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT in flags and len(data) >= offset + 2:
            sensor_status = DataParser.parse_int16(data, offset, signed=False)

        # Validate sensor status against Glucose Feature if available
        if ctx is not None and sensor_status is not None:
            feature_char = self.get_context_characteristic(ctx, GlucoseFeatureCharacteristic)
            if feature_char and feature_char.parse_success and feature_char.value is not None:
                self._validate_sensor_status_against_feature(sensor_status, feature_char.value)

        # Create result with all parsed values
        return GlucoseMeasurementData(
            sequence_number=sequence_number,
            base_time=base_time,
            glucose_concentration=glucose_concentration,
            unit=unit,
            flags=flags,
            time_offset_minutes=time_offset_minutes,
            glucose_type=glucose_type,
            sample_location=sample_location,
            sensor_status=sensor_status,
        )

    def _encode_value(self, data: GlucoseMeasurementData) -> bytearray:  # pylint: disable=too-many-locals,too-many-branches # Complex medical data encoding
        """Encode glucose measurement value back to bytes.

        Args:
            data: GlucoseMeasurementData containing glucose measurement data

        Returns:
            Encoded bytes representing the glucose measurement

        """
        # Build flags based on available data
        flags = GlucoseMeasurementFlags(0)
        if data.time_offset_minutes is not None:
            flags |= GlucoseMeasurementFlags.TIME_OFFSET_PRESENT
        if data.unit == "mmol/L":
            flags |= GlucoseMeasurementFlags.GLUCOSE_CONCENTRATION_UNITS_MMOL_L
        if data.glucose_type is not None or data.sample_location is not None:
            flags |= GlucoseMeasurementFlags.TYPE_SAMPLE_LOCATION_PRESENT
        if data.sensor_status is not None:
            flags |= GlucoseMeasurementFlags.SENSOR_STATUS_ANNUNCIATION_PRESENT

        # Validate ranges
        if not 0 <= data.sequence_number <= 0xFFFF:
            raise ValueError(f"Sequence number {data.sequence_number} exceeds uint16 range")

        # Start with flags, sequence number, and base time
        result = bytearray([int(flags)])
        result.extend(DataParser.encode_int16(data.sequence_number, signed=False))
        result.extend(IEEE11073Parser.encode_timestamp(data.base_time))

        # Add optional time offset
        if data.time_offset_minutes is not None:
            if not SINT16_MIN <= data.time_offset_minutes <= SINT16_MAX:
                raise ValueError(f"Time offset {data.time_offset_minutes} exceeds sint16 range")
            result.extend(DataParser.encode_int16(data.time_offset_minutes, signed=True))

        # Add glucose concentration using IEEE-11073 SFLOAT
        result.extend(IEEE11073Parser.encode_sfloat(data.glucose_concentration))

        # Add optional type and sample location
        if data.glucose_type is not None or data.sample_location is not None:
            glucose_type = data.glucose_type or 0
            sample_location = data.sample_location or 0
            type_sample = BitFieldUtils.merge_bit_fields(
                (
                    glucose_type,
                    GlucoseMeasurementBits.GLUCOSE_TYPE_START_BIT,
                    GlucoseMeasurementBits.GLUCOSE_TYPE_BIT_WIDTH,
                ),
                (
                    sample_location,
                    GlucoseMeasurementBits.GLUCOSE_SAMPLE_LOCATION_START_BIT,
                    GlucoseMeasurementBits.GLUCOSE_SAMPLE_LOCATION_BIT_WIDTH,
                ),
            )
            result.append(type_sample)

        # Add optional sensor status
        if data.sensor_status is not None:
            if not 0 <= data.sensor_status <= 0xFFFF:
                raise ValueError(f"Sensor status {data.sensor_status} exceeds uint16 range")
            result.extend(DataParser.encode_int16(data.sensor_status, signed=False))

        return result

    def _validate_sensor_status_against_feature(self, sensor_status: int, feature_data: GlucoseFeatureData) -> None:
        """Validate sensor status bits against supported Glucose Features.

        Args:
            sensor_status: Raw sensor status bitmask from measurement
            feature_data: GlucoseFeatureData from Glucose Feature characteristic

        Raises:
            ValueError: If reported sensor status bits are not supported by device features

        """
        # Sensor status bits correspond to Glucose Feature bits
        # Check each status bit against corresponding feature support
        if (sensor_status & GlucoseFeatures.LOW_BATTERY_DETECTION) and not feature_data.low_battery_detection:
            raise ValueError("Low battery status reported but not supported by Glucose Feature")
        if (
            sensor_status & GlucoseFeatures.SENSOR_MALFUNCTION_DETECTION
        ) and not feature_data.sensor_malfunction_detection:
            raise ValueError("Sensor malfunction status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.SENSOR_SAMPLE_SIZE) and not feature_data.sensor_sample_size:
            raise ValueError("Sensor sample size status reported but not supported by Glucose Feature")
        if (
            sensor_status & GlucoseFeatures.SENSOR_STRIP_INSERTION_ERROR
        ) and not feature_data.sensor_strip_insertion_error:
            raise ValueError("Sensor strip insertion error status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.SENSOR_STRIP_TYPE_ERROR) and not feature_data.sensor_strip_type_error:
            raise ValueError("Sensor strip type error status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.SENSOR_RESULT_HIGH_LOW) and not feature_data.sensor_result_high_low:
            raise ValueError("Sensor result high-low status reported but not supported by Glucose Feature")
        if (
            sensor_status & GlucoseFeatures.SENSOR_TEMPERATURE_HIGH_LOW
        ) and not feature_data.sensor_temperature_high_low:
            raise ValueError("Sensor temperature high-low status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.SENSOR_READ_INTERRUPT) and not feature_data.sensor_read_interrupt:
            raise ValueError("Sensor read interrupt status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.GENERAL_DEVICE_FAULT) and not feature_data.general_device_fault:
            raise ValueError("General device fault status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.TIME_FAULT) and not feature_data.time_fault:
            raise ValueError("Time fault status reported but not supported by Glucose Feature")
        if (sensor_status & GlucoseFeatures.MULTIPLE_BOND_SUPPORT) and not feature_data.multiple_bond_support:
            raise ValueError("Multiple bond status reported but not supported by Glucose Feature")
