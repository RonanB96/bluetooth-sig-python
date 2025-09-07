"""Glucose Measurement Context characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic
from .utils import IEEE11073Parser


@dataclass
class GlucoseMeasurementContextData:  # pylint: disable=too-many-instance-attributes # Medical measurement context with many optional fields
    """Parsed data from Glucose Measurement Context characteristic.

    Used for both parsing and encoding - None values represent optional fields.
    """

    sequence_number: int
    flags: int
    # Optional fields - will be set by parsing methods
    carbohydrate_id: str | None = None
    carbohydrate_kg: float | None = None
    carbohydrate_type: str | None = None  # Added missing field
    meal: str | None = None
    meal_type: str | None = None  # Added missing field
    tester: str | None = None
    health: str | None = None
    exercise_duration: int | None = None
    exercise_duration_seconds: int | None = None  # Added missing field
    exercise_intensity: int | None = None
    exercise_intensity_percent: int | None = None  # Added missing field
    medication_id: str | None = None
    medication_kg: float | None = None
    hba1c: float | None = None
    hba1c_percent: float | None = None  # Added missing field

    def __post_init__(self):
        """Validate glucose measurement context data."""
        if not 0 <= self.flags <= 255:
            raise ValueError("Flags must be a uint8 value (0-255)")
        if not 0 <= self.sequence_number <= 65535:
            raise ValueError("Sequence number must be a uint16 value (0-65535)")


@dataclass
class GlucoseMeasurementContextCharacteristic(BaseCharacteristic):
    """Glucose Measurement Context characteristic (0x2A34).

    Used to transmit additional context for glucose measurements including
    carbohydrate intake, exercise, medication, and HbA1c information.
    """

    _characteristic_name: str = "Glucose Measurement Context"

    def decode_value(self, data: bytearray) -> GlucoseMeasurementContextData:
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

        flags = data[0]
        offset = 1

        # Parse sequence number (2 bytes)
        sequence_number = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2

        # Create result object
        result_data = {
            "sequence_number": sequence_number,
            "flags": flags,
        }

        # Parse all optional fields based on flags
        offset = self._parse_extended_flags(data, flags, result_data, offset)
        offset = self._parse_carbohydrate_info(data, flags, result_data, offset)
        offset = self._parse_meal_info(data, flags, result_data, offset)
        offset = self._parse_tester_health_info(data, flags, result_data, offset)
        offset = self._parse_exercise_info(data, flags, result_data, offset)
        offset = self._parse_medication_info(data, flags, result_data, offset)
        self._parse_hba1c_info(data, flags, result_data, offset)

        # Convert dict to dataclass
        return GlucoseMeasurementContextData(**result_data)

    def encode_value(self, data: GlucoseMeasurementContextData) -> bytearray:
        """Encode glucose measurement context value back to bytes.

        Args:
            data: GlucoseMeasurementContextData containing glucose measurement context data

        Returns:
            Encoded bytes representing the measurement context
        """
        if not isinstance(data, GlucoseMeasurementContextData):
            raise TypeError(
                f"Glucose measurement context data must be a GlucoseMeasurementContextData, "
                f"got {type(data).__name__}"
            )

        sequence_number = data.sequence_number
        if not 0 <= sequence_number <= 0xFFFF:
            raise ValueError(f"Sequence number {sequence_number} exceeds uint16 range")

        # Build flags based on available optional data (use provided flags)
        flags = data.flags

        # Simplified implementation - just encode sequence number with provided flags
        result = bytearray([flags])
        result.extend(struct.pack("<H", sequence_number))

        # Additional context fields would be added based on flags (simplified)
        return result

    def _parse_extended_flags(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional extended flags field."""
        if (flags & 0x01) and len(data) >= offset + 1:
            extended_flags = data[offset]
            result["extended_flags"] = extended_flags
            offset += 1
        return offset

    def _parse_carbohydrate_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional carbohydrate information field."""
        if (flags & 0x02) and len(data) >= offset + 3:
            carb_id = data[offset]
            carb_raw = struct.unpack("<H", data[offset + 1 : offset + 3])[0]
            carb_value = IEEE11073Parser.parse_sfloat(carb_raw)
            result.update(
                {
                    "carbohydrate_id": carb_id,
                    "carbohydrate_kg": carb_value,
                    "carbohydrate_type": self._get_carbohydrate_type_name(carb_id),
                }
            )
            offset += 3
        return offset

    def _parse_meal_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional meal information field."""
        if (flags & 0x04) and len(data) >= offset + 1:
            meal = data[offset]
            result.update(
                {
                    "meal": meal,
                    "meal_type": self._get_meal_type_name(meal),
                }
            )
            offset += 1
        return offset

    def _parse_tester_health_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional tester and health information field."""
        if (flags & 0x08) and len(data) >= offset + 1:
            tester_health = data[offset]
            tester = (tester_health >> 4) & 0x0F
            health = tester_health & 0x0F
            result.update(
                {
                    "tester": tester,
                    "health": health,
                    "tester_type": self._get_tester_type_name(tester),
                    "health_type": self._get_health_type_name(health),
                }
            )
            offset += 1
        return offset

    def _parse_exercise_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional exercise information field."""
        if (flags & 0x10) and len(data) >= offset + 3:
            exercise_duration = struct.unpack("<H", data[offset : offset + 2])[0]
            exercise_intensity = data[offset + 2]
            result.update(
                {
                    "exercise_duration_seconds": exercise_duration,
                    "exercise_intensity_percent": exercise_intensity,
                }
            )
            offset += 3
        return offset

    def _parse_medication_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional medication information field."""
        if (flags & 0x20) and len(data) >= offset + 3:
            medication_id = data[offset]
            medication_raw = struct.unpack("<H", data[offset + 1 : offset + 3])[0]
            medication_value = IEEE11073Parser.parse_sfloat(medication_raw)
            result.update(
                {
                    "medication_id": medication_id,
                    "medication_kg": medication_value,
                    "medication_type": self._get_medication_type_name(medication_id),
                }
            )
            offset += 3
        return offset

    def _parse_hba1c_info(
        self, data: bytearray, flags: int, result: dict[str, Any], offset: int
    ) -> int:
        """Parse optional HbA1c information field."""
        if (flags & 0x40) and len(data) >= offset + 2:
            hba1c_raw = struct.unpack("<H", data[offset : offset + 2])[0]
            hba1c_value = IEEE11073Parser.parse_sfloat(hba1c_raw)
            result.update(
                {
                    "hba1c_percent": hba1c_value,
                }
            )
            offset += 2
        return offset

    def _get_carbohydrate_type_name(self, carb_id: int) -> str:
        """Get human-readable carbohydrate type name."""
        types = {
            1: "Breakfast",
            2: "Lunch",
            3: "Dinner",
            4: "Snack",
            5: "Drink",
            6: "Supper",
            7: "Brunch",
        }
        return types.get(carb_id, "Reserved")

    def _get_meal_type_name(self, meal: int) -> str:
        """Get human-readable meal type name."""
        types = {
            1: "Preprandial (before meal)",
            2: "Postprandial (after meal)",
            3: "Fasting",
            4: "Casual (snacks, drinks, etc.)",
            5: "Bedtime",
        }
        return types.get(meal, "Reserved")

    def _get_tester_type_name(self, tester: int) -> str:
        """Get human-readable tester type name."""
        types = {
            1: "Self",
            2: "Health Care Professional",
            3: "Lab test",
            15: "Tester value not available",
        }
        return types.get(tester, "Reserved")

    def _get_health_type_name(self, health: int) -> str:
        """Get human-readable health type name."""
        types = {
            1: "Minor health issues",
            2: "Major health issues",
            3: "During menses",
            4: "Under stress",
            5: "No health issues",
            15: "Health value not available",
        }
        return types.get(health, "Reserved")

    def _get_medication_type_name(self, medication_id: int) -> str:
        """Get human-readable medication type name."""
        types = {
            1: "Rapid acting insulin",
            2: "Short acting insulin",
            3: "Intermediate acting insulin",
            4: "Long acting insulin",
            5: "Pre-mixed insulin",
        }
        return types.get(medication_id, "Reserved")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "various"  # Multiple units in context data
