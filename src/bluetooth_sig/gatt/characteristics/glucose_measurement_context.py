"""Glucose Measurement Context characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class GlucoseMeasurementContextCharacteristic(BaseCharacteristic):
    """Glucose Measurement Context characteristic (0x2A34).

    Used to transmit additional context for glucose measurements including
    carbohydrate intake, exercise, medication, and HbA1c information.
    """

    _characteristic_name: str = "Glucose Measurement Context"

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse glucose measurement context data according to Bluetooth specification.

        Format: Flags(1) + Sequence Number(2) + [Extended Flags(1)] + [Carbohydrate ID(1) + Carb(2)] +
                [Meal(1)] + [Tester-Health(1)] + [Exercise Duration(2) + Exercise Intensity(1)] +
                [Medication ID(1) + Medication(2)] + [HbA1c(2)]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed glucose context data with metadata

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

        result = {
            "sequence_number": sequence_number,
            "flags": flags,
        }

        # Parse all optional fields based on flags
        offset = self._parse_extended_flags(data, flags, result, offset)
        offset = self._parse_carbohydrate_info(data, flags, result, offset)
        offset = self._parse_meal_info(data, flags, result, offset)
        offset = self._parse_tester_health_info(data, flags, result, offset)
        offset = self._parse_exercise_info(data, flags, result, offset)
        offset = self._parse_medication_info(data, flags, result, offset)
        self._parse_hba1c_info(data, flags, result, offset)

        return result


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
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
            carb_value = self._parse_ieee11073_sfloat(carb_raw)
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
            medication_value = self._parse_ieee11073_sfloat(medication_raw)
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
            hba1c_value = self._parse_ieee11073_sfloat(hba1c_raw)
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
