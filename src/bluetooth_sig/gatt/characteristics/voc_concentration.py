"""VOC Concentration characteristic implementation."""

from __future__ import annotations

from typing import cast

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import Uint16Template


# Special value constants for VOC Concentration characteristic
class VOCConcentrationValues:  # pylint: disable=too-few-public-methods
    """Special values for VOC Concentration characteristic per Bluetooth SIG specification."""

    VALUE_65534_OR_GREATER = 0xFFFE  # Indicates value is 65534 or greater
    VALUE_UNKNOWN = 0xFFFF  # Indicates value is not known


class VOCConcentrationCharacteristic(BaseCharacteristic):
    """Volatile Organic Compounds concentration characteristic (0x2BE7).

    Uses uint16 format as per SIG specification.
    Unit: ppb (parts per billion)
    Range: 0-65533
    (VOCConcentrationValues.VALUE_65534_OR_GREATER = ≥65534,
     VOCConcentrationValues.VALUE_UNKNOWN = unknown)
    """

    _template = Uint16Template()

    _manual_unit: str | None = "ppb"  # Unit as per SIG specification

    # Validation attributes
    expected_length: int = 2
    min_value: int = 0
    max_value: int = VOCConcentrationValues.VALUE_65534_OR_GREATER - 1  # Max valid value before special values
    expected_type: type = int

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Parse VOC concentration value with special value handling."""
        raw_value = cast(int, super().decode_value(data))

        # Handle special values per SIG specification
        if raw_value == VOCConcentrationValues.VALUE_65534_OR_GREATER:
            # Value is 65534 or greater - return a large value
            return 65534
        if raw_value == VOCConcentrationValues.VALUE_UNKNOWN:
            # Value is not known - could raise exception or return None
            # For now, return a sentinel value that tests can check
            raise ValueError("VOC concentration value is not known")

        return raw_value

    def encode_value(self, data: int) -> bytearray:
        """Encode VOC concentration with special value handling."""
        if data < 0:
            raise ValueError("VOC concentration cannot be negative")
        if data >= VOCConcentrationValues.VALUE_65534_OR_GREATER:
            # Encode as "65534 or greater" per SIG specification
            return super().encode_value(VOCConcentrationValues.VALUE_65534_OR_GREATER)

        return super().encode_value(data)
