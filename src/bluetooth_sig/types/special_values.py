"""Special value types for GATT characteristic parsing.

Special values are reserved raw integer values that indicate
exceptional conditions like "unknown", "invalid", "overflow", etc.
rather than actual measured data.

Pipeline integration:
    bytes → extract_raw() → check_special() → translate() → result
                               ↓ short-circuit
                         SpecialValueResult

When a special value is detected, the pipeline short-circuits and
returns a SpecialValueResult instead of translating the raw value.
"""

from __future__ import annotations

import msgspec

from .units import SpecialValueType


class SpecialValueRule(msgspec.Struct, frozen=True, kw_only=True):
    """A rule matching a raw value to its special meaning.

    Attributes:
        raw_value: The raw integer that triggers this rule
        meaning: Human-readable description (e.g., "Value is unknown")
        value_type: Category of special value
        threshold: For OVERFLOW/UNDERFLOW, the boundary value to return

    """

    raw_value: int
    meaning: str
    value_type: SpecialValueType = SpecialValueType.UNKNOWN
    threshold: float | None = None

    def to_result(self) -> SpecialValueResult:
        """Convert rule to a result when matched.

        Returns:
            SpecialValueResult with this rule's values

        """
        return SpecialValueResult(
            raw_value=self.raw_value,
            meaning=self.meaning,
            value_type=self.value_type,
            threshold=self.threshold,
        )


class SpecialValueResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result when a special value is detected during parsing.

    Contains the raw value that was detected, its meaning, type,
    and optionally a threshold value for overflow/underflow cases.

    Attributes:
        raw_value: The raw integer that triggered the special value
        meaning: Human-readable description
        value_type: Category of special value
        threshold: For OVERFLOW/UNDERFLOW, the boundary value

    """

    raw_value: int
    meaning: str
    value_type: SpecialValueType
    threshold: float | None = None

    @property
    def effective_value(self) -> float | None:
        """Return threshold for overflow/underflow, None otherwise.

        For OVERFLOW/UNDERFLOW special values, returns the threshold
        as a meaningful boundary value. For other types, returns None
        since the value doesn't represent actual data.

        Returns:
            Threshold value for overflow/underflow, None for other types

        """
        if self.value_type in (SpecialValueType.OVERFLOW, SpecialValueType.UNDERFLOW):
            return self.threshold
        return None


__all__ = [
    "SpecialValueRule",
    "SpecialValueResult",
]
