"""Glucose Measurement Context characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

from ..constants import UINT8_MAX, UINT16_MAX
from .base import BaseCharacteristic
from .utils import BitFieldUtils, DataParser, IEEE11073Parser


class GlucoseMeasurementContextBits:
    """Glucose Measurement Context bit field constants."""

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

    @classmethod
    def get_name(cls, value: CarbohydrateType) -> str:
        """Get human-readable name for carbohydrate type value.

        Args:
            value: Carbohydrate type value

        Returns:
            Human-readable description

        Raises:
            ValueError: If value is outside valid range
        """
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(
                f"Carbohydrate type value {value} is out of valid range (0-UINT8_MAX)"
            )

        try:
            return str(cls(value))
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return "Reserved for Future Use"


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

    @classmethod
    def get_name(cls, value: MealType) -> str:
        """Get human-readable name for meal type value.

        Args:
            value: Meal type value

        Returns:
            Human-readable description

        Raises:
            ValueError: If value is outside valid range
        """
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(
                f"Meal type value {value} is out of valid range (0-UINT8_MAX)"
            )

        try:
            return str(cls(value))
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return "Reserved for Future Use"


class TesterType(IntEnum):
    """Tester type enumeration as per Bluetooth SIG specification."""

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

    @classmethod
    def get_name(cls, value: TesterType) -> str:
        """Get human-readable name for tester type value.

        Args:
            value: Tester type value

        Returns:
            Human-readable description

        Raises:
            ValueError: If value is outside valid range
        """
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(
                f"Tester type value {value} is out of valid range (0-UINT8_MAX)"
            )

        try:
            return str(cls(value))
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return "Reserved for Future Use"


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

    @classmethod
    def get_name(cls, value: HealthType) -> str:
        """Get human-readable name for health type value.

        Args:
            value: Health type value

        Returns:
            Human-readable description

        Raises:
            ValueError: If value is outside valid range
        """
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(
                f"Health type value {value} is out of valid range (0-UINT8_MAX)"
            )

        try:
            return str(cls(value))
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return "Reserved for Future Use"


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

    @classmethod
    def get_name(cls, value: MedicationType) -> str:
        """Get human-readable name for medication type value.

        Args:
            value: Medication type value

        Returns:
            Human-readable description

        Raises:
            ValueError: If value is outside valid range
        """
        if not 0 <= value <= UINT8_MAX:
            raise ValueError(
                f"Medication type value {value} is out of valid range (0-UINT8_MAX)"
            )

        try:
            return str(cls(value))
        except ValueError:
            # Values not in enum are reserved per Bluetooth SIG spec
            return "Reserved for Future Use"


class GlucoseMeasurementContextExtendedFlags:
    """Glucose Measurement Context Extended Flags constants as per Bluetooth SIG specification.

    Currently all bits are reserved for future use.
    """

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


@dataclass
class GlucoseMeasurementContextData:  # pylint: disable=too-many-instance-attributes # Medical measurement context with many optional fields
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
    tester: TesterType | None = None
    health: HealthType | None = None
    exercise_duration: int | None = None
    exercise_intensity: int | None = None
    medication_id: MedicationType | None = None
    medication_kg: float | None = None
    hba1c: float | None = None

    def __post_init__(self) -> None:
        """Validate glucose measurement context data."""
        if not 0 <= self.flags <= UINT8_MAX:
            raise ValueError("Flags must be a uint8 value (0-UINT8_MAX)")
        if not 0 <= self.sequence_number <= UINT16_MAX:
            raise ValueError("Sequence number must be a uint16 value (0-UINT16_MAX)")


@dataclass
class GlucoseMeasurementContextCharacteristic(BaseCharacteristic):
    """Glucose Measurement Context characteristic (0x2A34).

    Used to transmit additional context for glucose measurements including
    carbohydrate intake, exercise, medication, and HbA1c information.
    """

    _characteristic_name: str = "Glucose Measurement Context"

    min_length: int | None = 3  # Flags(1) + Sequence(2) minimum
    max_length: int | None = (
        19  # + ExtendedFlags(1) + Carb(3) + Meal(1) + TesterHealth(1) + Exercise(3) + Medication(3) + HbA1c(2) maximum
    )
    allow_variable_length: bool = True  # Variable optional fields

    def decode_value(
        self, data: bytearray, ctx: Any | None = None
    ) -> GlucoseMeasurementContextData:
        """Parse glucose measurement context data according to Bluetooth specification.

        Format: Flags(1) + Sequence Number(2) + [Extended Flags(1)] + [Carbohydrate ID(1) + Carb(2)] +
                [Meal(1)] + [Tester-Health(1)] + [Exercise Duration(2) + Exercise Intensity(1)] +
                [Medication ID(1) + Medication(2)] + [HbA1c(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            GlucoseMeasurementContextData containing parsed glucose context data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 3:
            raise ValueError(
                "Glucose Measurement Context data must be at least 3 bytes"
            )

        flags_raw = data[0]
        flags = GlucoseMeasurementContextFlags(flags_raw)
        offset = 1

        # Parse sequence number (2 bytes)
        sequence_number = DataParser.parse_int16(data, offset, signed=False)
        offset += 2

        # Create dataclass with required fields
        result = GlucoseMeasurementContextData(
            sequence_number=sequence_number,
            flags=flags,
        )

        # Parse all optional fields based on flags
        offset = self._parse_extended_flags(data, flags, result, offset)
        offset = self._parse_carbohydrate_info(data, flags, result, offset)
        offset = self._parse_meal_info(data, flags, result, offset)
        offset = self._parse_tester_health_info(data, flags, result, offset)
        offset = self._parse_exercise_info(data, flags, result, offset)
        offset = self._parse_medication_info(data, flags, result, offset)
        self._parse_hba1c_info(data, flags, result, offset)

        return result

    def encode_value(self, data: GlucoseMeasurementContextData) -> bytearray:
        """Encode glucose measurement context value back to bytes.

        Args:
            data: GlucoseMeasurementContextData containing glucose measurement context data

        Returns:
            Encoded bytes representing the measurement context
        """
        sequence_number = data.sequence_number
        if not 0 <= sequence_number <= 0xFFFF:
            raise ValueError(f"Sequence number {sequence_number} exceeds uint16 range")

        # Build flags based on available optional data (use provided flags)
        flags = data.flags

        # Simplified implementation - just encode sequence number with provided flags
        result = bytearray([flags])
        result.extend(DataParser.encode_int16(sequence_number, signed=False))

        # Additional context fields would be added based on flags (simplified)
        return result

    def _parse_extended_flags(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional extended flags field."""
        if (
            GlucoseMeasurementContextFlags.EXTENDED_FLAGS_PRESENT in flags
            and len(data) >= offset + 1
        ):
            extended_flags = data[offset]
            result.extended_flags = extended_flags
            offset += 1
        return offset

    def _parse_carbohydrate_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional carbohydrate information field."""
        if (
            GlucoseMeasurementContextFlags.CARBOHYDRATE_PRESENT in flags
            and len(data) >= offset + 3
        ):
            carb_id = data[offset]
            carb_value = IEEE11073Parser.parse_sfloat(data, offset + 1)
            result.carbohydrate_id = CarbohydrateType(carb_id)
            result.carbohydrate_kg = carb_value
            offset += 3
        return offset

    def _parse_meal_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional meal information field."""
        if (
            GlucoseMeasurementContextFlags.MEAL_PRESENT in flags
            and len(data) >= offset + 1
        ):
            meal = data[offset]
            result.meal = MealType(meal)
            offset += 1
        return offset

    def _parse_tester_health_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional tester and health information field."""
        if (
            GlucoseMeasurementContextFlags.TESTER_HEALTH_PRESENT in flags
            and len(data) >= offset + 1
        ):
            tester_health = data[offset]
            tester = BitFieldUtils.extract_bit_field(
                tester_health,
                GlucoseMeasurementContextBits.TESTER_START_BIT,
                GlucoseMeasurementContextBits.TESTER_BIT_WIDTH,
            )  # Bits 4-7 (4 bits)
            health = BitFieldUtils.extract_bit_field(
                tester_health,
                GlucoseMeasurementContextBits.HEALTH_START_BIT,
                GlucoseMeasurementContextBits.HEALTH_BIT_WIDTH,
            )  # Bits 0-3 (4 bits)
            result.tester = TesterType(tester)
            result.health = HealthType(health)
            offset += 1
        return offset

    def _parse_exercise_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional exercise information field."""
        if (
            GlucoseMeasurementContextFlags.EXERCISE_PRESENT in flags
            and len(data) >= offset + 3
        ):
            exercise_duration = DataParser.parse_int16(data, offset, signed=False)
            exercise_intensity = data[offset + 2]
            result.exercise_duration = exercise_duration
            result.exercise_intensity = exercise_intensity
            offset += 3
        return offset

    def _parse_medication_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional medication information field."""
        if (
            GlucoseMeasurementContextFlags.MEDICATION_PRESENT in flags
            and len(data) >= offset + 3
        ):
            medication_id = data[offset]
            medication_value = IEEE11073Parser.parse_sfloat(data, offset + 1)
            result.medication_id = MedicationType(medication_id)
            result.medication_kg = medication_value
            offset += 3
        return offset

    def _parse_hba1c_info(
        self,
        data: bytearray,
        flags: GlucoseMeasurementContextFlags,
        result: GlucoseMeasurementContextData,
        offset: int,
    ) -> int:
        """Parse optional HbA1c information field."""
        if (
            GlucoseMeasurementContextFlags.HBA1C_PRESENT in flags
            and len(data) >= offset + 2
        ):
            hba1c_value = IEEE11073Parser.parse_sfloat(data, offset)
            result.hba1c = hba1c_value
            offset += 2
        return offset

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "various"  # Multiple units in context data
