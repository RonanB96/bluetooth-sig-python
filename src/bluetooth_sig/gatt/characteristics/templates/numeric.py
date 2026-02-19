"""Basic integer templates for unsigned and signed integer parsing.

Covers Uint8, Sint8, Uint16, Sint16, Uint24, Uint32 templates.
"""

from __future__ import annotations

from ...constants import (
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    SINT16_MIN,
    UINT8_MAX,
    UINT16_MAX,
    UINT24_MAX,
    UINT32_MAX,
)
from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError
from ..utils.extractors import (
    SINT8,
    SINT16,
    UINT8,
    UINT16,
    UINT24,
    UINT32,
    RawExtractor,
)
from ..utils.translators import (
    IDENTITY,
    ValueTranslator,
)
from .base import CodingTemplate


class Uint8Template(CodingTemplate[int]):
    """Template for 8-bit unsigned integer parsing (0-255)."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def extractor(self) -> RawExtractor:
        """Get uint8 extractor."""
        return UINT8

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 8-bit unsigned integer."""
        if validate and len(data) < offset + 1:
            raise InsufficientDataError("uint8", data[offset:], 1)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode uint8 value to bytes."""
        if validate and not 0 <= value <= UINT8_MAX:
            raise ValueError(f"Value {value} out of range for uint8 (0-{UINT8_MAX})")
        return self.extractor.pack(value)


class Sint8Template(CodingTemplate[int]):
    """Template for 8-bit signed integer parsing (-128 to 127)."""

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def extractor(self) -> RawExtractor:
        """Get sint8 extractor."""
        return SINT8

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 8-bit signed integer."""
        if validate and len(data) < offset + 1:
            raise InsufficientDataError("sint8", data[offset:], 1)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode sint8 value to bytes."""
        if validate and not SINT8_MIN <= value <= SINT8_MAX:
            raise ValueError(f"Value {value} out of range for sint8 ({SINT8_MIN} to {SINT8_MAX})")
        return self.extractor.pack(value)


class Uint16Template(CodingTemplate[int]):
    """Template for 16-bit unsigned integer parsing (0-65535)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def extractor(self) -> RawExtractor:
        """Get uint16 extractor."""
        return UINT16

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 16-bit unsigned integer."""
        if validate and len(data) < offset + 2:
            raise InsufficientDataError("uint16", data[offset:], 2)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode uint16 value to bytes."""
        if validate and not 0 <= value <= UINT16_MAX:
            raise ValueError(f"Value {value} out of range for uint16 (0-{UINT16_MAX})")
        return self.extractor.pack(value)


class Sint16Template(CodingTemplate[int]):
    """Template for 16-bit signed integer parsing (-32768 to 32767)."""

    @property
    def data_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def extractor(self) -> RawExtractor:
        """Get sint16 extractor."""
        return SINT16

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 16-bit signed integer."""
        if validate and len(data) < offset + 2:
            raise InsufficientDataError("sint16", data[offset:], 2)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode sint16 value to bytes."""
        if validate and not SINT16_MIN <= value <= SINT16_MAX:
            raise ValueError(f"Value {value} out of range for sint16 ({SINT16_MIN} to {SINT16_MAX})")
        return self.extractor.pack(value)


class Uint24Template(CodingTemplate[int]):
    """Template for 24-bit unsigned integer parsing (0-16777215)."""

    @property
    def data_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    @property
    def extractor(self) -> RawExtractor:
        """Get uint24 extractor."""
        return UINT24

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 24-bit unsigned integer."""
        if validate and len(data) < offset + 3:
            raise InsufficientDataError("uint24", data[offset:], 3)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode uint24 value to bytes."""
        if validate and not 0 <= value <= UINT24_MAX:
            raise ValueError(f"Value {value} out of range for uint24 (0-{UINT24_MAX})")
        return self.extractor.pack(value)


class Uint32Template(CodingTemplate[int]):
    """Template for 32-bit unsigned integer parsing."""

    @property
    def data_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def extractor(self) -> RawExtractor:
        """Get uint32 extractor."""
        return UINT32

    @property
    def translator(self) -> ValueTranslator[int]:
        """Return identity translator for no scaling."""
        return IDENTITY

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> int:
        """Parse 32-bit unsigned integer."""
        if validate and len(data) < offset + 4:
            raise InsufficientDataError("uint32", data[offset:], 4)
        return self.extractor.extract(data, offset)

    def encode_value(self, value: int, *, validate: bool = True) -> bytearray:
        """Encode uint32 value to bytes."""
        if validate and not 0 <= value <= UINT32_MAX:
            raise ValueError(f"Value {value} out of range for uint32 (0-{UINT32_MAX})")
        return self.extractor.pack(value)
