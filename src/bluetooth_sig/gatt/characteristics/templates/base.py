# mypy: warn_unused_ignores=False
"""Base coding template abstract class and shared constants.

All coding templates MUST inherit from CodingTemplate defined here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from ....types.gatt_enums import AdjustReason, DayOfWeek  # noqa: F401  # Re-export for sub-modules
from ...context import CharacteristicContext
from ..utils.extractors import RawExtractor
from ..utils.translators import ValueTranslator

# =============================================================================
# TYPE VARIABLES
# =============================================================================

# Type variable for CodingTemplate generic - represents the decoded value type
T_co = TypeVar("T_co", covariant=True)

# Resolution constants for common measurement scales
_RESOLUTION_INTEGER = 1.0  # Integer resolution (10^0)
_RESOLUTION_TENTH = 0.1  # 0.1 resolution (10^-1)
_RESOLUTION_HUNDREDTH = 0.01  # 0.01 resolution (10^-2)


# =============================================================================
# LEVEL 4 BASE CLASS
# =============================================================================


class CodingTemplate(ABC, Generic[T_co]):
    """Abstract base class for coding templates.

    Templates are pure coding utilities that don't inherit from BaseCharacteristic.
    They provide coding strategies that can be injected into characteristics.
    All templates MUST inherit from this base class and implement the required methods.

    Generic over T_co, the type of value produced by _decode_value.
    Concrete templates specify their return type, e.g., CodingTemplate[int].

    Pipeline Integration:
        Simple templates (single-field) expose `extractor` and `translator` properties
        for the decode/encode pipeline. Complex templates return None for these properties.
    """

    @abstractmethod
    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> T_co:
        """Decode raw bytes to typed value.

        Args:
            data: Raw bytes to parse
            offset: Byte offset to start parsing from
            ctx: Optional context for parsing
            validate: Whether to validate ranges (default True)

        Returns:
            Parsed value of type T_co

        """

    @abstractmethod
    def encode_value(self, value: T_co, *, validate: bool = True) -> bytearray:  # type: ignore[misc]  # Covariant T_co in parameter is intentional for encode/decode symmetry
        """Encode typed value to raw bytes.

        Args:
            value: Typed value to encode
            validate: Whether to validate ranges (default True)

        Returns:
            Raw bytes representing the value

        """

    @property
    @abstractmethod
    def data_size(self) -> int:
        """Size of data in bytes that this template handles."""

    @property
    def extractor(self) -> RawExtractor | None:
        """Get the raw byte extractor for pipeline access.

        Returns None for complex templates where extraction isn't separable.
        """
        return None

    @property
    def translator(self) -> ValueTranslator[Any] | None:
        """Get the value translator for pipeline access.

        Returns None for complex templates where translation isn't separable.
        """
        return None
