"""Glucose Measurement Context characteristic implementation."""

from __future__ import annotations

import logging
from enum import IntEnum, IntFlag

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .glucose_measurement import GlucoseMeasurementCharacteristic
from .utils import BitFieldUtils, DataParser, IEEE11073Parser

logger = logging.getLogger(__name__)


class ExtendedFlagsResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Extended flags parsing result."""

    extended_flags: int | None
    offset: int


class CarbohydrateResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Carbohydrate information parsing result."""

    carbohydrate_id: CarbohydrateType | None
    carbohydrate_kg: float | None
    offset: int


class MealResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Meal information parsing result."""

    meal: MealType | None
    offset: int


class TesterHealthResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Tester and health information parsing result."""

    tester: GlucoseTester | None
    health: HealthType | None
    offset: int


class ExerciseResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Exercise information parsing result."""

    exercise_duration_seconds: int | None
    exercise_intensity_percent: int | None
    offset: int


class MedicationResult(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Medication information parsing result."""

    medication_id: MedicationType | None
    medication_kg: float | None
    offset: int


class GlucoseMeasurementContextBits:
    """Glucose Measurement Context bit field constants."""

    # pylint: disable=too-few-public-methods

    TESTER_START_BIT = 4  # Tester value starts at bit 4
    TESTER_BIT_WIDTH = 4  # Tester value uses 4 bits
    HEALTH_START_BIT = 0  # Health value starts at bit 0
    HEALTH_BIT_WIDTH = 4  # Health value uses 4 bits


class CarbohydrateType(IntEnum):
    """Carbohydrate type enumeration as per Bluetooth SIG specification."""

    BREAKFAST = 1
    LUNCH = 2
    DINNER = 3
    SNACK = 4
    DRINK = 5
    SUPPER = 6
    BRUNCH = 7

    def __str__(self) -> str:
        """Return human-readable carbohydrate type name."""
        names = {
            self.BREAKFAST: "Breakfast",
            self.LUNCH: "Lunch",
            self.DINNER: "Dinner",
            self.SNACK: "Snack",
            self.DRINK: "Drink",
            self.SUPPER: "Supper",
            self.BRUNCH: "Brunch",
        }
        return names.get(self, "Reserved for Future Use")


class MealType(IntEnum):
    """Meal type enumeration as per Bluetooth SIG specification."""

    PREPRANDIAL = 1
    POSTPRANDIAL = 2
    FASTING = 3
    CASUAL = 4
    BEDTIME = 5

    def __str__(self) -> str:
        """Return human-readable meal type name."""
        names = {
            self.PREPRANDIAL: "Preprandial (before meal)",
            self.POSTPRANDIAL: "Postprandial (after meal)",
            self.FASTING: "Fasting",
            self.CASUAL: "Casual (snacks, drinks, etc.)",
            self.BEDTIME: "Bedtime",
        }
        return names.get(self, "Reserved for Future Use")


class GlucoseTester(IntEnum):
    """Glucose tester type enumeration as per Bluetooth SIG specification."""

    SELF = 1
    HEALTH_CARE_PROFESSIONAL = 2
    LAB_TEST = 3
    NOT_AVAILABLE = 15

    def __str__(self) -> str:
        """Return human-readable tester type name."""
        names = {
            self.SELF: "Self",
            self.HEALTH_CARE_PROFESSIONAL: "Health Care Professional",
            self.LAB_TEST: "Lab test",
            self.NOT_AVAILABLE: "Tester value not available",
        }
        return names.get(self, "Reserved for Future Use")


class HealthType(IntEnum):
    """Health type enumeration as per Bluetooth SIG specification."""

    MINOR_HEALTH_ISSUES = 1
    MAJOR_HEALTH_ISSUES = 2
    DURING_MENSES = 3
    UNDER_STRESS = 4
    NO_HEALTH_ISSUES = 5
    NOT_AVAILABLE = 15

    def __str__(self) -> str:
        """Return human-readable health type name."""
        names = {
            self.MINOR_HEALTH_ISSUES: "Minor health issues",
            self.MAJOR_HEALTH_ISSUES: "Major health issues",
            self.DURING_MENSES: "During menses",
            self.UNDER_STRESS: "Under stress",
            self.NO_HEALTH_ISSUES: "No health issues",
            self.NOT_AVAILABLE: "Health value not available",
        }
        return names.get(self, "Reserved for Future Use")


class MedicationType(IntEnum):
    """Medication type enumeration as per Bluetooth SIG specification."""

    RAPID_ACTING_INSULIN = 1
    SHORT_ACTING_INSULIN = 2
    INTERMEDIATE_ACTING_INSULIN = 3
    LONG_ACTING_INSULIN = 4
    PRE_MIXED_INSULIN = 5

    def __str__(self) -> str:
        """Return human-readable medication type name."""
        names = {
            self.RAPID_ACTING_INSULIN: "Rapid acting insulin",
            self.SHORT_ACTING_INSULIN: "Short acting insulin",
            self.INTERMEDIATE_ACTING_INSULIN: "Intermediate acting insulin",
            self.LONG_ACTING_INSULIN: "Long acting insulin",
            self.PRE_MIXED_INSULIN: "Pre-mixed insulin",
        }
        return names.get(self, "Reserved for Future Use")


class GlucoseMeasurementContextExtendedFlags(IntEnum):
    """Glucose Measurement Context Extended Flags constants as per Bluetooth SIG specification.

    Currently all bits are reserved for future use.
    """

    # pylint: disable=too-few-public-methods

    RESERVED_BIT_0 = 0x01
    RESERVED_BIT_1 = 0x02
    RESERVED_BIT_2 = 0x04
    RESERVED_BIT_3 = 0x08
    RESERVED_BIT_4 = 0x10
    RESERVED_BIT_5 = 0x20
    RESERVED_BIT_6 = 0x40
    RESERVED_BIT_7 = 0x80

    @staticmethod
    def get_description(flags: int) -> str:
        """Get description of extended flags.

        Args:
            flags: Extended flags value (0-255)

        Returns:
            Description string indicating all bits are reserved

        """
        if flags == 0:
            return "No extended flags set"

        # All bits are currently reserved for future use
        bit_descriptions: list[str] = []
        for bit in range(8):
            bit_value = 1 << bit
            if flags & bit_value:
                bit_descriptions.append(f"Bit {bit} (Reserved for Future Use)")

        return "; ".join(bit_descriptions)


class GlucoseMeasurementContextFlags(IntFlag):
    """Glucose Measurement Context flags as per Bluetooth SIG specification."""

    EXTENDED_FLAGS_PRESENT = 0x01
    CARBOHYDRATE_PRESENT = 0x02
    MEAL_PRESENT = 0x04
    TESTER_HEALTH_PRESENT = 0x08
    EXERCISE_PRESENT = 0x10
    MEDICATION_PRESENT = 0x20
    HBA1C_PRESENT = 0x40
    RESERVED = 0x80


class GlucoseMeasurementContextData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Glucose Measurement Context characteristic.

    Used for both parsing and encoding - None values represent optional fields.
    """

    sequence_number: int
    flags: GlucoseMeasurementContextFlags
    # Optional fields - will be set by parsing methods
    extended_flags: int | None = None
    carbohydrate_id: CarbohydrateType | None = None
    carbohydrate_kg: float | None = None
    meal: MealType | None = None
    tester: GlucoseTester | None = None
    health: HealthType | None = None
    exercise_duration_seconds: int | None = None
    exercise_intensity_percent: int | None = None
    medication_id: MedicationType | None = None
    medication_kg: float | None = None
    hba1c_percent: float | None = None

    def __post_init__(self) -> None:
        """Validate glucose measurement context data."""
        if not 0 <= self.flags <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")
        if not 0 <= self.sequence_number <= UINT16_MAX:
            raise ValueError("Sequence number must be a uint16 value (0-UINT16_MAX)")


class GlucoseMeasurementContextCharacteristic(BaseCharacteristic[GlucoseMeasurementContextData]):
    """Glucose Measurement Context characteristic (0x2A34).

    Used to transmit additional context for glucose measurements
    including carbohydrate intake, exercise, medication, and HbA1c
    information.

    SIG Specification Pattern:
    This characteristic depends on Glucose Measurement (0x2A18) for sequence number
    matching. The sequence_number field in this context must match the sequence_number
    from a corresponding Glucose Measurement characteristic.
    """

    _characteristic_name: str = "Glucose Measurement Context"
    _manual_unit: str = "various"  # Multiple units in context data

    # Declare dependency on Glucose Measurement for sequence number matching (REQUIRED)
    _required_dependencies = [GlucoseMeasurementCharacteristic]

    min_length: int | None = 3  # Flags(1) + Sequence(2) minimum
    max_length: int | None = (
        19  # + ExtendedFlags(1) + Carb(3) + Meal(1) + TesterHealth(1) + Exercise(3) + Medication(3) + HbA1c(2) maximum
    )
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> GlucoseMeasurementContextData:  # pylint: disable=too-many-locals
        """Parse glucose measurement context data according to Bluetooth specification.

        Format: Flags(1) + Sequence Number(2) + [Extended Flags(1)] + [Carbohydrate ID(1) + Carb(2)] +
                [Meal(1)] + [Tester-Health(1)] + [Exercise Duration(2) + Exercise Intensity(1)] +
                [Medication ID(1) + Medication(2)] + [HbA1c(2)].

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context providing access to Glucose Measurement characteristic
                for sequence number validation.

        Returns:
            GlucoseMeasurementContextData containing parsed glucose context data.

        Raises:
            ValueError: If data format is invalid.

        SIG Pattern:
        When context is available, validates that this context's sequence_number matches
        a Glucose Measurement sequence_number, following the SIG specification pattern
        where contexts are paired with measurements via sequence number matching.

        """
        if len(data) < 3:
            raise ValueError("Glucose Measurement Context data must be at least 3 bytes")

        flags_raw = data[0]
        flags = GlucoseMeasurementContextFlags(flags_raw)
        offset = 1

        # Parse sequence number (2 bytes)
        sequence_number = DataParser.parse_int16(data, offset, signed=False)
        offset += 2

        # Validate sequence number matching with Glucose Measurement if context available
        # SIG Specification: "Contains the sequence number of the corresponding Glucose Measurement"
        if ctx is not None and isinstance(ctx, CharacteristicContext):
            glucose_meas = self.get_context_characteristic(ctx, GlucoseMeasurementCharacteristic)
            if glucose_meas and hasattr(glucose_meas, "sequence_number"):
                # Extract sequence number from GlucoseMeasurementData
                meas_seq = glucose_meas.sequence_number
                if meas_seq != sequence_number:
                    logger.warning(
                        "Glucose Measurement Context sequence number (%d) does not match "
                        "Glucose Measurement sequence number (%d)",
                        sequence_number,
                        meas_seq,
                    )

        # Parse all optional fields based on flags
        extended = self._parse_extended_flags(data, flags, offset)
        carb = self._parse_carbohydrate_info(data, flags, extended.offset)
        meal_result = self._parse_meal_info(data, flags, carb.offset)
        tester_health = self._parse_tester_health_info(data, flags, meal_result.offset)
        exercise = self._parse_exercise_info(data, flags, tester_health.offset)
        medication = self._parse_medication_info(data, flags, exercise.offset)
        hba1c_percent = self._parse_hba1c_info(data, flags, medication.offset)

        # Create struct with all parsed values
        return GlucoseMeasurementContextData(
            sequence_number=sequence_number,
            flags=flags,
            extended_flags=extended.extended_flags,
            carbohydrate_id=carb.carbohydrate_id,
            carbohydrate_kg=carb.carbohydrate_kg,
            meal=meal_result.meal,
            tester=tester_health.tester,
            health=tester_health.health,
            exercise_duration_seconds=exercise.exercise_duration_seconds,
            exercise_intensity_percent=exercise.exercise_intensity_percent,
            medication_id=medication.medication_id,
            medication_kg=medication.medication_kg,
            hba1c_percent=hba1c_percent,
        )

    def _encode_value(self, data: GlucoseMeasurementContextData) -> bytearray:
        """Encode glucose measurement context value back to bytes.

        Args:
            data: GlucoseMeasurementContextData containing glucose measurement context data

        Returns:
            Encoded bytes representing the measurement context

        """
        sequence_number = data.sequence_number
        if not 0 <= sequence_number <= 0xFFFF:
            raise ValueError(f"Sequence number {sequence_number} exceeds uint16 range")

        # Use the flags from the data structure
        flags = data.flags

        result = bytearray([flags])
        result.extend(DataParser.encode_int16(sequence_number, signed=False))

        # Encode optional extended flags
        if data.extended_flags is not None:
            result.append(data.extended_flags)

        # Encode optional carbohydrate information
        if data.carbohydrate_id is not None and data.carbohydrate_kg is not None:
            result.append(int(data.carbohydrate_id))
            result.extend(IEEE11073Parser.encode_sfloat(data.carbohydrate_kg))

        # Encode optional meal information
        if data.meal is not None:
            result.append(int(data.meal))

        # Encode optional tester/health information
        if data.tester is not None and data.health is not None:
            tester_health = (int(data.tester) << GlucoseMeasurementContextBits.TESTER_START_BIT) | (
                int(data.health) << GlucoseMeasurementContextBits.HEALTH_START_BIT
            )
            result.append(tester_health)

        # Encode optional exercise information
        if data.exercise_duration_seconds is not None and data.exercise_intensity_percent is not None:
            result.extend(DataParser.encode_int16(data.exercise_duration_seconds, signed=False))
            result.append(data.exercise_intensity_percent)

        # Encode optional medication information
        if data.medication_id is not None and data.medication_kg is not None:
            result.append(int(data.medication_id))
            result.extend(IEEE11073Parser.encode_sfloat(data.medication_kg))

        # Encode optional HbA1c information
        if data.hba1c_percent is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.hba1c_percent))

        return result

    def _parse_extended_flags(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> ExtendedFlagsResult:
        """Parse optional extended flags field."""
        extended_flags: int | None = None
        if GlucoseMeasurementContextFlags.EXTENDED_FLAGS_PRESENT in flags and len(data) >= offset + 1:
            extended_flags = int(data[offset])
            offset += 1
        return ExtendedFlagsResult(extended_flags=extended_flags, offset=offset)

    def _parse_carbohydrate_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> CarbohydrateResult:
        """Parse optional carbohydrate information field."""
        carbohydrate_id: CarbohydrateType | None = None
        carbohydrate_kg: float | None = None
        if GlucoseMeasurementContextFlags.CARBOHYDRATE_PRESENT in flags and len(data) >= offset + 3:
            carb_id = data[offset]
            carb_value = IEEE11073Parser.parse_sfloat(data, offset + 1)
            carbohydrate_id = CarbohydrateType(carb_id)
            carbohydrate_kg = carb_value
            offset += 3
        return CarbohydrateResult(carbohydrate_id=carbohydrate_id, carbohydrate_kg=carbohydrate_kg, offset=offset)

    def _parse_meal_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> MealResult:
        """Parse optional meal information field."""
        meal: MealType | None = None
        if GlucoseMeasurementContextFlags.MEAL_PRESENT in flags and len(data) >= offset + 1:
            meal = MealType(data[offset])
            offset += 1
        return MealResult(meal=meal, offset=offset)

    def _parse_tester_health_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> TesterHealthResult:
        """Parse optional tester and health information field."""
        tester: GlucoseTester | None = None
        health: HealthType | None = None
        if GlucoseMeasurementContextFlags.TESTER_HEALTH_PRESENT in flags and len(data) >= offset + 1:
            tester_health = data[offset]
            tester_raw = BitFieldUtils.extract_bit_field(
                tester_health,
                GlucoseMeasurementContextBits.TESTER_START_BIT,
                GlucoseMeasurementContextBits.TESTER_BIT_WIDTH,
            )  # Bits 4-7 (4 bits)
            health_raw = BitFieldUtils.extract_bit_field(
                tester_health,
                GlucoseMeasurementContextBits.HEALTH_START_BIT,
                GlucoseMeasurementContextBits.HEALTH_BIT_WIDTH,
            )  # Bits 0-3 (4 bits)
            tester = GlucoseTester(tester_raw)
            health = HealthType(health_raw)
            offset += 1
        return TesterHealthResult(tester=tester, health=health, offset=offset)

    def _parse_exercise_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> ExerciseResult:
        """Parse optional exercise information field."""
        exercise_duration_seconds: int | None = None
        exercise_intensity_percent: int | None = None
        if GlucoseMeasurementContextFlags.EXERCISE_PRESENT in flags and len(data) >= offset + 3:
            exercise_duration_seconds = DataParser.parse_int16(data, offset, signed=False)
            exercise_intensity_percent = int(data[offset + 2])
            offset += 3
        return ExerciseResult(
            exercise_duration_seconds=exercise_duration_seconds,
            exercise_intensity_percent=exercise_intensity_percent,
            offset=offset,
        )

    def _parse_medication_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> MedicationResult:
        """Parse optional medication information field."""
        medication_id: MedicationType | None = None
        medication_kg: float | None = None
        if GlucoseMeasurementContextFlags.MEDICATION_PRESENT in flags and len(data) >= offset + 3:
            medication_id = MedicationType(data[offset])
            medication_kg = IEEE11073Parser.parse_sfloat(data, offset + 1)
            offset += 3
        return MedicationResult(medication_id=medication_id, medication_kg=medication_kg, offset=offset)

    def _parse_hba1c_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        offset: int,
    ) -> float | None:
        """Parse optional HbA1c information field.

        Returns:
            HbA1c percentage or None

        """
        hba1c_percent: float | None = None
        if GlucoseMeasurementContextFlags.HBA1C_PRESENT in flags and len(data) >= offset + 2:
            hba1c_percent = IEEE11073Parser.parse_sfloat(data, offset)
        return hba1c_percent
