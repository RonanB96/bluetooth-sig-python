"""VOC Concentration characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .templates import SimpleUint16Characteristic


# Special value constants for VOC Concentration characteristic
class VOCConcentrationValues:  # pylint: disable=too-few-public-methods
    """Special values for VOC Concentration characteristic per Bluetooth SIG
    specification."""

    VALUE_65534_OR_GREATER = 0xFFFE  # Indicates value is 65534 or greater
    VALUE_UNKNOWN = 0xFFFF  # Indicates value is not known


@dataclass
class VOCConcentrationCharacteristic(SimpleUint16Characteristic):
    """Volatile Organic Compounds concentration characteristic (0x2BE7).

    Uses uint16 format as per SIG specification.
    Unit: ppb (parts per billion)
    Range: 0-65533
    (VOCConcentrationValues.VALUE_65534_OR_GREATER = ≥65534,
     VOCConcentrationValues.VALUE_UNKNOWN = unknown)
    """

    _characteristic_name: str = "VOC Concentration"
    _manual_unit: str | None = field(default="ppb", init=False)  # Unit as per SIG specification
    min_value: int = 0
    max_value: int = VOCConcentrationValues.VALUE_65534_OR_GREATER - 1  # 65533

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
        """Parse VOC concentration value with special value handling."""
        raw_value = super().decode_value(data)

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
