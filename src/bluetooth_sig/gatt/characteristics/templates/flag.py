"""Flag template for IntFlag encoding/decoding with configurable byte size."""

from __future__ import annotations

from enum import IntFlag
from typing import TypeVar

from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError, ValueRangeError
from ..utils.extractors import (
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

# Type variable for FlagTemplate - bound to IntFlag
F = TypeVar("F", bound=IntFlag)


class FlagTemplate(CodingTemplate[F]):
    """Template for IntFlag encoding/decoding with configurable byte size.

    Maps raw integer bytes to Python IntFlag instances through extraction and
    validation.  Unlike EnumTemplate (which expects exact enum membership),
    FlagTemplate accepts any bitwise OR combination of the defined flag members.

    Pipeline Integration:
        bytes → [extractor] → raw_int → [IDENTITY translator] → int → flag constructor

    Examples:
        >>> class ContactStatus(IntFlag):
        ...     CONTACT_0 = 0x01
        ...     CONTACT_1 = 0x02
        ...     CONTACT_2 = 0x04
        >>>
        >>> template = FlagTemplate.uint8(ContactStatus)
        >>>
        >>> # Decode from bytes — any combination is valid
        >>> flags = template.decode_value(bytearray([0x05]))
        >>> # ContactStatus.CONTACT_0 | ContactStatus.CONTACT_2
        >>>
        >>> # Encode flags to bytes
        >>> data = template.encode_value(ContactStatus.CONTACT_0 | ContactStatus.CONTACT_2)  # bytearray([0x05])
    """

    def __init__(self, flag_class: type[F], extractor: RawExtractor) -> None:
        """Initialise with flag class and extractor.

        Args:
            flag_class: IntFlag subclass to encode/decode.
            extractor: Raw extractor defining byte size and signedness.

        """
        self._flag_class = flag_class
        self._extractor = extractor
        # Pre-compute the bitmask of all defined members for validation.
        self._valid_mask: int = 0
        for member in flag_class:
            self._valid_mask |= member.value

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
        """Get IDENTITY translator for flags (no scaling needed)."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> F:
        """Decode bytes to flag instance.

        Args:
            data: Raw bytes from BLE characteristic.
            offset: Starting offset in data buffer.
            ctx: Optional context for parsing.
            validate: Whether to validate against defined flag bits (default True).

        Returns:
            Flag instance of type F.

        Raises:
            InsufficientDataError: If data too short for required byte size.
            ValueRangeError: If raw value contains undefined bits and ``validate=True``.

        """
        if validate and len(data) < offset + self.data_size:
            raise InsufficientDataError(self._flag_class.__name__, data[offset:], self.data_size)

        raw_value = self._extractor.extract(data, offset)

        if validate and (raw_value & ~self._valid_mask):
            raise ValueRangeError(
                self._flag_class.__name__,
                raw_value,
                0,
                self._valid_mask,
            )

        return self._flag_class(raw_value)

    def encode_value(self, value: F | int, *, validate: bool = True) -> bytearray:
        """Encode flag instance or int to bytes.

        Args:
            value: Flag instance or integer value to encode.
            validate: Whether to validate against defined flag bits (default True).

        Returns:
            Encoded bytes.

        Raises:
            ValueError: If value contains undefined bits and ``validate=True``.

        """
        int_value = value.value if isinstance(value, self._flag_class) else int(value)

        if validate and (int_value & ~self._valid_mask):
            raise ValueError(
                f"{self._flag_class.__name__} value 0x{int_value:02X} contains "
                f"undefined bits (valid mask: 0x{self._valid_mask:02X})"
            )

        return self._extractor.pack(int_value)

    # -----------------------------------------------------------------
    # Factory methods
    # -----------------------------------------------------------------

    @classmethod
    def uint8(cls, flag_class: type[F]) -> FlagTemplate[F]:
        """Create FlagTemplate for 1-byte unsigned flag field.

        Args:
            flag_class: IntFlag subclass with bit values in 0-255.

        Returns:
            Configured FlagTemplate instance.

        Example::
            >>> class Status(IntFlag):
            ...     BIT_0 = 0x01
            ...     BIT_1 = 0x02
            >>> template = FlagTemplate.uint8(Status)

        """
        return cls(flag_class, UINT8)

    @classmethod
    def uint16(cls, flag_class: type[F]) -> FlagTemplate[F]:
        """Create FlagTemplate for 2-byte unsigned flag field.

        Args:
            flag_class: IntFlag subclass with bit values in 0-65535.

        Returns:
            Configured FlagTemplate instance.

        """
        return cls(flag_class, UINT16)

    @classmethod
    def uint32(cls, flag_class: type[F]) -> FlagTemplate[F]:
        """Create FlagTemplate for 4-byte unsigned flag field.

        Args:
            flag_class: IntFlag subclass with bit values in 0-4294967295.

        Returns:
            Configured FlagTemplate instance.

        """
        return cls(flag_class, UINT32)
