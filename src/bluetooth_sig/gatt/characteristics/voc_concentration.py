"""VOC Concentration characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .templates import SimpleUint16Characteristic


@dataclass
class VOCConcentrationCharacteristic(SimpleUint16Characteristic):
    """Volatile Organic Compounds concentration characteristic (0x2BE7).

    Uses uint16 format as per SIG specification.
    Unit: ppb (parts per billion)
    Range: 0-65533 (0xFFFE = ≥65534, 0xFFFF = unknown)
    """

    _characteristic_name: str = "VOC Concentration"
    min_value: int = 0
    max_value: int = 65533  # 0xFFFE and 0xFFFF are special values

    @property
    def unit(self) -> str:
        """Return unit as per SIG specification."""
        return "ppb"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
        """Parse VOC concentration value with special value handling."""
        raw_value = super().decode_value(data)

        # Handle special values per SIG specification
        if raw_value == 0xFFFE:
            # Value is 65534 or greater - return a large value
            return 65534
        if raw_value == 0xFFFF:
            # Value is not known - could raise exception or return None
            # For now, return a sentinel value that tests can check
            raise ValueError("VOC concentration value is not known")

        return raw_value

    def encode_value(self, data: int) -> bytearray:
        """Encode VOC concentration with special value handling."""
        if data < 0:
            raise ValueError("VOC concentration cannot be negative")
        if data >= 65534:
            # Encode as "65534 or greater" per SIG specification
            return super().encode_value(0xFFFE)

        return super().encode_value(data)
