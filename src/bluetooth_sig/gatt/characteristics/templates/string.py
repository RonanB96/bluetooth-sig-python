"""String templates for UTF-8 and UTF-16LE variable-length parsing.

Covers Utf8StringTemplate and Utf16StringTemplate.
"""

from __future__ import annotations

from ...context import CharacteristicContext
from .base import CodingTemplate


class Utf8StringTemplate(CodingTemplate[str]):
    """Template for UTF-8 string parsing with variable length."""

    def __init__(self, max_length: int = 256) -> None:
        """Initialize with maximum string length.

        Args:
            max_length: Maximum string length in bytes

        """
        self.max_length = max_length

    @property
    def data_size(self) -> int:
        """Size: Variable (0 to max_length)."""
        return self.max_length

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> str:
        """Parse UTF-8 string from remaining data."""
        if offset >= len(data):
            return ""

        # Take remaining data from offset
        string_data = data[offset:]

        # Remove null terminator if present
        if b"\x00" in string_data:
            null_index = string_data.index(b"\x00")
            string_data = string_data[:null_index]

        try:
            return string_data.decode("utf-8")
        except UnicodeDecodeError as e:
            if validate:
                raise ValueError(f"Invalid UTF-8 string data: {e}") from e
            return ""

    def encode_value(self, value: str, *, validate: bool = True) -> bytearray:
        """Encode string to UTF-8 bytes."""
        encoded = value.encode("utf-8")
        if validate and len(encoded) > self.max_length:
            raise ValueError(f"String too long: {len(encoded)} > {self.max_length}")
        return bytearray(encoded)


class Utf16StringTemplate(CodingTemplate[str]):
    """Template for UTF-16LE string parsing with variable length."""

    # Unicode constants for UTF-16 validation
    UNICODE_SURROGATE_START = 0xD800
    UNICODE_SURROGATE_END = 0xDFFF
    UNICODE_BOM = "\ufeff"

    def __init__(self, max_length: int = 256) -> None:
        """Initialize with maximum string length.

        Args:
            max_length: Maximum string length in bytes (must be even)

        """
        if max_length % 2 != 0:
            raise ValueError("max_length must be even for UTF-16 strings")
        self.max_length = max_length

    @property
    def data_size(self) -> int:
        """Size: Variable (0 to max_length, even bytes only)."""
        return self.max_length

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> str:
        """Parse UTF-16LE string from remaining data."""
        if offset >= len(data):
            return ""

        # Take remaining data from offset
        string_data = data[offset:]

        # Find null terminator at even positions (UTF-16 alignment)
        null_index = len(string_data)
        for i in range(0, len(string_data) - 1, 2):
            if string_data[i : i + 2] == bytearray(b"\x00\x00"):
                null_index = i
                break
        string_data = string_data[:null_index]

        # UTF-16 requires even number of bytes
        if validate and len(string_data) % 2 != 0:
            raise ValueError(f"UTF-16 data must have even byte count, got {len(string_data)}")

        try:
            decoded = string_data.decode("utf-16-le")
            # Strip BOM if present (robustness)
            if decoded.startswith(self.UNICODE_BOM):
                decoded = decoded[1:]
            # Check for invalid surrogate pairs
            if validate and any(self.UNICODE_SURROGATE_START <= ord(c) <= self.UNICODE_SURROGATE_END for c in decoded):
                raise ValueError("Invalid UTF-16LE string data: contains unpaired surrogates")
        except UnicodeDecodeError as e:
            if validate:
                raise ValueError(f"Invalid UTF-16LE string data: {e}") from e
            return ""
        else:
            return decoded

    def encode_value(self, value: str, *, validate: bool = True) -> bytearray:
        """Encode string to UTF-16LE bytes."""
        encoded = value.encode("utf-16-le")
        if validate and len(encoded) > self.max_length:
            raise ValueError(f"String too long: {len(encoded)} > {self.max_length}")
        return bytearray(encoded)
