"""Enum template for IntEnum encoding/decoding with configurable byte size."""

from __future__ import annotations

from enum import IntEnum
from typing import TypeVar

from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError, ValueRangeError
from ..utils.extractors import (
    SINT8,
    SINT16,
    SINT32,
    UINT8,
    UINT16,
    UINT32,
    RawExtractor,
)
from ..utils.translators import (
    IDENTITY,
    ValueTranslator,
)
from .base import CodingTemplate

# Type variable for EnumTemplate - bound to IntEnum
T = TypeVar("T", bound=IntEnum)


class EnumTemplate(CodingTemplate[T]):
    """Template for IntEnum encoding/decoding with configurable byte size.

    Maps raw integer bytes to Python IntEnum instances through extraction and validation.
    Supports any integer-based enum with any extractor (UINT8, UINT16, SINT8, etc.).

    This template validates enum membership explicitly, supporting non-contiguous
    enum ranges (e.g., values 0, 2, 5, 10).

    Pipeline Integration:
        bytes → [extractor] → raw_int → [IDENTITY translator] → int → enum constructor

    Examples:
        >>> class Status(IntEnum):
        ...     IDLE = 0
        ...     ACTIVE = 1
        ...     ERROR = 2
        >>>
        >>> # Create template with factory method
        >>> template = EnumTemplate.uint8(Status)
        >>>
        >>> # Or with explicit extractor
        >>> template = EnumTemplate(Status, UINT8)
        >>>
        >>> # Decode from bytes
        >>> status = template.decode_value(bytearray([0x01]))  # Status.ACTIVE
        >>>
        >>> # Encode enum to bytes
        >>> data = template.encode_value(Status.ERROR)  # bytearray([0x02])
        >>>
        >>> # Encode int to bytes (also supported)
        >>> data = template.encode_value(2)  # bytearray([0x02])
    """

    def __init__(self, enum_class: type[T], extractor: RawExtractor) -> None:
        """Initialize with enum class and extractor.

        Args:
            enum_class: IntEnum subclass to encode/decode
            extractor: Raw extractor defining byte size and signedness
                      (e.g., UINT8, UINT16, SINT8, etc.)
        """
        self._enum_class = enum_class
        self._extractor = extractor

    @property
    def data_size(self) -> int:
        """Return byte size required for encoding."""
        return self._extractor.byte_size

    @property
    def extractor(self) -> RawExtractor:
        """Return extractor for pipeline access."""
        return self._extractor

    @property
    def translator(self) -> ValueTranslator[int]:
        """Get IDENTITY translator for enums (no scaling needed)."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> T:
        """Decode bytes to enum instance.

        Args:
            data: Raw bytes from BLE characteristic
            offset: Starting offset in data buffer
            ctx: Optional context for parsing
            validate: Whether to validate enum membership (default True)

        Returns:
            Enum instance of type T

        Raises:
            InsufficientDataError: If data too short for required byte size
            ValueRangeError: If raw value not a valid enum member and validate=True
        """
        # Check data length
        if validate and len(data) < offset + self.data_size:
            raise InsufficientDataError(self._enum_class.__name__, data[offset:], self.data_size)

        # Extract raw integer value
        raw_value = self._extractor.extract(data, offset)

        # Validate enum membership and construct
        try:
            return self._enum_class(raw_value)
        except ValueError as e:
            # Get valid range from enum members
            valid_values = [member.value for member in self._enum_class]
            min_val = min(valid_values)
            max_val = max(valid_values)
            raise ValueRangeError(self._enum_class.__name__, raw_value, min_val, max_val) from e

    def encode_value(self, value: T | int, *, validate: bool = True) -> bytearray:
        """Encode enum instance or int to bytes.

        Args:
            value: Enum instance or integer value to encode
            validate: Whether to validate enum membership (default True)

        Returns:
            Encoded bytes

        Raises:
            ValueError: If value not a valid enum member and validate=True
        """
        # Convert to int if enum instance
        int_value = value.value if isinstance(value, self._enum_class) else int(value)

        # Validate membership
        if validate:
            valid_values = [member.value for member in self._enum_class]
            if int_value not in valid_values:
                min_val = min(valid_values)
                max_val = max(valid_values)
                raise ValueError(
                    f"{self._enum_class.__name__} value {int_value} is invalid. "
                    f"Valid range: {min_val}-{max_val}, valid values: {sorted(valid_values)}"
                )

        # Pack to bytes
        return self._extractor.pack(int_value)

    @classmethod
    def uint8(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 1-byte unsigned enum.

        Args:
            enum_class: IntEnum subclass with values 0-255

        Returns:
            Configured EnumTemplate instance

        Example::
            >>> class Status(IntEnum):
            ...     IDLE = 0
            ...     ACTIVE = 1
            >>> template = EnumTemplate.uint8(Status)
        """
        return cls(enum_class, UINT8)

    @classmethod
    def uint16(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 2-byte unsigned enum.

        Args:
            enum_class: IntEnum subclass with values 0-65535

        Returns:
            Configured EnumTemplate instance

        Example::
            >>> class ExtendedStatus(IntEnum):
            ...     STATE_1 = 0x0100
            ...     STATE_2 = 0x0200
            >>> template = EnumTemplate.uint16(ExtendedStatus)
        """
        return cls(enum_class, UINT16)

    @classmethod
    def uint32(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 4-byte unsigned enum.

        Args:
            enum_class: IntEnum subclass with values 0-4294967295

        Returns:
            Configured EnumTemplate instance
        """
        return cls(enum_class, UINT32)

    @classmethod
    def sint8(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 1-byte signed enum.

        Args:
            enum_class: IntEnum subclass with values -128 to 127

        Returns:
            Configured EnumTemplate instance

        Example::
            >>> class Temperature(IntEnum):
            ...     FREEZING = -10
            ...     NORMAL = 0
            ...     HOT = 10
            >>> template = EnumTemplate.sint8(Temperature)
        """
        return cls(enum_class, SINT8)

    @classmethod
    def sint16(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 2-byte signed enum.

        Args:
            enum_class: IntEnum subclass with values -32768 to 32767

        Returns:
            Configured EnumTemplate instance
        """
        return cls(enum_class, SINT16)

    @classmethod
    def sint32(cls, enum_class: type[T]) -> EnumTemplate[T]:
        """Create EnumTemplate for 4-byte signed enum.

        Args:
            enum_class: IntEnum subclass with values -2147483648 to 2147483647

        Returns:
            Configured EnumTemplate instance
        """
        return cls(enum_class, SINT32)
