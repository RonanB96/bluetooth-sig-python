"""Raw byte extractors for the BLE encoding/decoding pipeline.

This module provides the extraction layer that ONLY converts bytes to raw integers
(and back). Extractors have a single responsibility: byte layout interpretation.

The extraction layer is the first stage of the decode pipeline:
    bytes → [Extractor] → raw_int → [Translator] → typed_value

Per Bluetooth SIG specifications, all multi-byte values use little-endian encoding
unless explicitly stated otherwise.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from .data_parser import DataParser


class RawExtractor(ABC):
    """Protocol for raw byte extraction.

    Extractors handle ONLY byte layout: extracting raw integers from bytes
    and packing raw integers back to bytes. They do not apply scaling,
    handle special values, or perform validation beyond bounds checking.

    The separation enables:
    - Interception of raw values for special value handling
    - Composition with translators for scaling
    - Reuse across templates and characteristics
    """

    __slots__ = ()

    @property
    @abstractmethod
    def byte_size(self) -> int:
        """Number of bytes this extractor reads/writes."""

    @property
    @abstractmethod
    def signed(self) -> bool:
        """Whether the integer type is signed."""

    @abstractmethod
    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract raw integer from bytes.

        Args:
            data: Source bytes to extract from.
            offset: Byte offset to start reading from.

        Returns:
            Raw integer value (not scaled or interpreted).

        Raises:
            InsufficientDataError: If data is too short for extraction.
        """

    @abstractmethod
    def pack(self, raw: int) -> bytearray:
        """Pack raw integer to bytes.

        Args:
            raw: Raw integer value to encode.

        Returns:
            Packed bytes in little-endian format.

        Raises:
            ValueRangeError: If raw value exceeds type bounds.
        """


class Uint8Extractor(RawExtractor):
    """Extract/pack unsigned 8-bit integers (0 to 255)."""

    __slots__ = ()

    @property
    def byte_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def signed(self) -> bool:
        """Unsigned type."""
        return False

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract uint8 from bytes."""
        return DataParser.parse_int8(data, offset, signed=False)

    def pack(self, raw: int) -> bytearray:
        """Pack uint8 to bytes."""
        return DataParser.encode_int8(raw, signed=False)


class Sint8Extractor(RawExtractor):
    """Extract/pack signed 8-bit integers (-128 to 127)."""

    __slots__ = ()

    @property
    def byte_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def signed(self) -> bool:
        """Signed type."""
        return True

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract sint8 from bytes."""
        return DataParser.parse_int8(data, offset, signed=True)

    def pack(self, raw: int) -> bytearray:
        """Pack sint8 to bytes."""
        return DataParser.encode_int8(raw, signed=True)


class Uint16Extractor(RawExtractor):
    """Extract/pack unsigned 16-bit integers (0 to 65535)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def signed(self) -> bool:
        """Unsigned type."""
        return False

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract uint16 from bytes."""
        return DataParser.parse_int16(data, offset, signed=False, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack uint16 to bytes."""
        return DataParser.encode_int16(raw, signed=False, endian=self._endian)


class Sint16Extractor(RawExtractor):
    """Extract/pack signed 16-bit integers (-32768 to 32767)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 2 bytes."""
        return 2

    @property
    def signed(self) -> bool:
        """Signed type."""
        return True

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract sint16 from bytes."""
        return DataParser.parse_int16(data, offset, signed=True, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack sint16 to bytes."""
        return DataParser.encode_int16(raw, signed=True, endian=self._endian)


class Uint24Extractor(RawExtractor):
    """Extract/pack unsigned 24-bit integers (0 to 16777215)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    @property
    def signed(self) -> bool:
        """Unsigned type."""
        return False

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract uint24 from bytes."""
        return DataParser.parse_int24(data, offset, signed=False, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack uint24 to bytes."""
        return DataParser.encode_int24(raw, signed=False, endian=self._endian)


class Sint24Extractor(RawExtractor):
    """Extract/pack signed 24-bit integers (-8388608 to 8388607)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 3 bytes."""
        return 3

    @property
    def signed(self) -> bool:
        """Signed type."""
        return True

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract sint24 from bytes."""
        return DataParser.parse_int24(data, offset, signed=True, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack sint24 to bytes."""
        return DataParser.encode_int24(raw, signed=True, endian=self._endian)


class Uint32Extractor(RawExtractor):
    """Extract/pack unsigned 32-bit integers (0 to 4294967295)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def signed(self) -> bool:
        """Unsigned type."""
        return False

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract uint32 from bytes."""
        return DataParser.parse_int32(data, offset, signed=False, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack uint32 to bytes."""
        return DataParser.encode_int32(raw, signed=False, endian=self._endian)


class Sint32Extractor(RawExtractor):
    """Extract/pack signed 32-bit integers (-2147483648 to 2147483647)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def signed(self) -> bool:
        """Signed type."""
        return True

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract sint32 from bytes."""
        return DataParser.parse_int32(data, offset, signed=True, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack sint32 to bytes."""
        return DataParser.encode_int32(raw, signed=True, endian=self._endian)


class Uint48Extractor(RawExtractor):
    """Extract/pack unsigned 48-bit integers (0 to 281474976710655)."""

    __slots__ = ("_endian",)

    def __init__(self, endian: Literal["little", "big"] = "little") -> None:
        """Initialize with endianness.

        Args:
            endian: Byte order, defaults to little-endian per BLE spec.
        """
        self._endian: Literal["little", "big"] = endian

    @property
    def byte_size(self) -> int:
        """Size: 6 bytes."""
        return 6

    @property
    def signed(self) -> bool:
        """Unsigned type."""
        return False

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract uint48 from bytes."""
        return DataParser.parse_int48(data, offset, signed=False, endian=self._endian)

    def pack(self, raw: int) -> bytearray:
        """Pack uint48 to bytes."""
        return DataParser.encode_int48(raw, signed=False, endian=self._endian)


class Float32Extractor(RawExtractor):
    """Extract/pack IEEE-754 32-bit floats.

    Unlike integer extractors, this returns the raw bits as an integer
    to enable special value detection (NaN patterns, etc.) before
    translation to float.
    """

    __slots__ = ()

    @property
    def byte_size(self) -> int:
        """Size: 4 bytes."""
        return 4

    @property
    def signed(self) -> bool:
        """Floats are inherently signed."""
        return True

    def extract(self, data: bytes | bytearray, offset: int = 0) -> int:
        """Extract float32 as raw bits for special value checking.

        Returns the raw 32-bit integer representation of the float,
        which allows special value detection (NaN patterns, etc.).
        """
        raw_bytes = data[offset : offset + 4]
        return int.from_bytes(raw_bytes, byteorder="little", signed=False)

    def pack(self, raw: int) -> bytearray:
        """Pack raw bits to float32 bytes."""
        return bytearray(raw.to_bytes(4, byteorder="little", signed=False))

    def extract_float(self, data: bytes | bytearray, offset: int = 0) -> float:
        """Extract as actual float value (convenience method)."""
        return DataParser.parse_float32(bytearray(data), offset)

    def pack_float(self, value: float) -> bytearray:
        """Pack float value to bytes (convenience method)."""
        return DataParser.encode_float32(value)


# Singleton instances for common extractors (immutable, thread-safe)
UINT8 = Uint8Extractor()
SINT8 = Sint8Extractor()
UINT16 = Uint16Extractor()
SINT16 = Sint16Extractor()
UINT24 = Uint24Extractor()
SINT24 = Sint24Extractor()
UINT32 = Uint32Extractor()
SINT32 = Sint32Extractor()
UINT48 = Uint48Extractor()
FLOAT32 = Float32Extractor()

# Mapping from GSS type strings to extractor instances
_EXTRACTOR_MAP: dict[str, RawExtractor] = {
    "uint8": UINT8,
    "sint8": SINT8,
    "uint16": UINT16,
    "sint16": SINT16,
    "uint24": UINT24,
    "sint24": SINT24,
    "uint32": UINT32,
    "sint32": SINT32,
    "uint48": UINT48,
    "float32": FLOAT32,
    "int16": SINT16,
}


def get_extractor(type_name: str) -> RawExtractor | None:
    """Get extractor for a GSS type string.

    Args:
        type_name: Type string from GSS FieldSpec.type (e.g., "sint16", "uint8").

    Returns:
        Matching RawExtractor singleton, or None if type is not recognized.

    Examples:
        >>> extractor = get_extractor("sint16")
        >>> raw = extractor.extract(data, offset=0)
    """
    return _EXTRACTOR_MAP.get(type_name.lower())
