"""Tests for characteristic templates."""

from __future__ import annotations

from enum import IntEnum

import pytest

from bluetooth_sig.gatt.characteristics.templates import (
    EnumTemplate,
    Utf8StringTemplate,
    Utf16StringTemplate,
)
from bluetooth_sig.gatt.characteristics.utils.extractors import (
    SINT8,
    SINT16,
    SINT32,
    UINT8,
    UINT16,
    UINT32,
)
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError


# Test enums
class SimpleStatus(IntEnum):
    """Simple contiguous enum."""

    IDLE = 0
    ACTIVE = 1
    ERROR = 2
    COMPLETED = 3


class NonContiguousEnum(IntEnum):
    """Non-contiguous enum values."""

    FIRST = 0
    SECOND = 2
    THIRD = 5
    FOURTH = 10


class LargeEnum(IntEnum):
    """Enum with values requiring uint16."""

    LOW = 0x0100
    MEDIUM = 0x0200
    HIGH = 0x0300


class SignedEnum(IntEnum):
    """Enum with negative values."""

    NEGATIVE = -10
    ZERO = 0
    POSITIVE = 10


class TestEnumTemplateBasics:
    """Test basic EnumTemplate functionality."""

    def test_decode_simple_enum_success(self) -> None:
        """Test decoding valid enum values."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.decode_value(bytearray([0x00])) == SimpleStatus.IDLE
        assert template.decode_value(bytearray([0x01])) == SimpleStatus.ACTIVE
        assert template.decode_value(bytearray([0x02])) == SimpleStatus.ERROR
        assert template.decode_value(bytearray([0x03])) == SimpleStatus.COMPLETED

    def test_decode_with_offset(self) -> None:
        """Test decoding with non-zero offset."""
        template = EnumTemplate.uint8(SimpleStatus)
        data = bytearray([0xFF, 0xFF, 0x01, 0xFF])

        result = template.decode_value(data, offset=2)
        assert result == SimpleStatus.ACTIVE

    def test_encode_enum_instance(self) -> None:
        """Test encoding enum instances."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.encode_value(SimpleStatus.IDLE) == bytearray([0x00])
        assert template.encode_value(SimpleStatus.ACTIVE) == bytearray([0x01])
        assert template.encode_value(SimpleStatus.ERROR) == bytearray([0x02])

    def test_encode_int_value(self) -> None:
        """Test encoding from integer values."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.encode_value(0) == bytearray([0x00])
        assert template.encode_value(1) == bytearray([0x01])
        assert template.encode_value(2) == bytearray([0x02])

    def test_round_trip(self) -> None:
        """Test encode -> decode returns original value."""
        template = EnumTemplate.uint8(SimpleStatus)

        for status in SimpleStatus:
            encoded = template.encode_value(status)
            decoded = template.decode_value(encoded)
            assert decoded == status


class TestEnumTemplateErrorHandling:
    """Test error handling in EnumTemplate."""

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        template = EnumTemplate.uint8(SimpleStatus)

        with pytest.raises(InsufficientDataError) as exc_info:
            template.decode_value(bytearray([]))

        assert "SimpleStatus" in str(exc_info.value)

    def test_decode_invalid_enum_value(self) -> None:
        """Test error on invalid enum value."""
        template = EnumTemplate.uint8(SimpleStatus)

        with pytest.raises(ValueRangeError) as exc_info:
            template.decode_value(bytearray([0xFF]))

        error = exc_info.value
        assert error.field == "SimpleStatus"
        assert error.value == 255
        assert error.min_val == 0
        assert error.max_val == 3

    def test_encode_invalid_enum_value(self) -> None:
        """Test error on encoding invalid value."""
        template = EnumTemplate.uint8(SimpleStatus)

        with pytest.raises(ValueError) as exc_info:
            template.encode_value(99)

        assert "SimpleStatus" in str(exc_info.value)
        assert "99" in str(exc_info.value)
        assert "Valid range" in str(exc_info.value)

    def test_decode_with_offset_insufficient_data(self) -> None:
        """Test error with offset beyond data length."""
        template = EnumTemplate.uint8(SimpleStatus)
        data = bytearray([0x01])

        with pytest.raises(InsufficientDataError):
            template.decode_value(data, offset=5)


class TestEnumTemplateNonContiguous:
    """Test EnumTemplate with non-contiguous enum values."""

    def test_decode_non_contiguous_valid(self) -> None:
        """Test decoding valid non-contiguous enum values."""
        template = EnumTemplate.uint8(NonContiguousEnum)

        assert template.decode_value(bytearray([0x00])) == NonContiguousEnum.FIRST
        assert template.decode_value(bytearray([0x02])) == NonContiguousEnum.SECOND
        assert template.decode_value(bytearray([0x05])) == NonContiguousEnum.THIRD
        assert template.decode_value(bytearray([0x0A])) == NonContiguousEnum.FOURTH

    def test_decode_non_contiguous_invalid_gap(self) -> None:
        """Test error on decoding values in gaps."""
        template = EnumTemplate.uint8(NonContiguousEnum)

        # Value 1 is in a gap (between 0 and 2)
        with pytest.raises(ValueRangeError) as exc_info:
            template.decode_value(bytearray([0x01]))

        assert exc_info.value.value == 1

        # Value 3 is in a gap (between 2 and 5)
        with pytest.raises(ValueRangeError) as exc_info:
            template.decode_value(bytearray([0x03]))

        assert exc_info.value.value == 3

    def test_encode_non_contiguous(self) -> None:
        """Test encoding non-contiguous enum values."""
        template = EnumTemplate.uint8(NonContiguousEnum)

        assert template.encode_value(NonContiguousEnum.FIRST) == bytearray([0x00])
        assert template.encode_value(NonContiguousEnum.SECOND) == bytearray([0x02])
        assert template.encode_value(NonContiguousEnum.THIRD) == bytearray([0x05])
        assert template.encode_value(NonContiguousEnum.FOURTH) == bytearray([0x0A])


class TestEnumTemplateFactoryMethods:
    """Test factory methods for different byte sizes."""

    def test_uint8_factory(self) -> None:
        """Test uint8 factory method."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.data_size == 1
        assert template.extractor == UINT8
        assert template.decode_value(bytearray([0x01])) == SimpleStatus.ACTIVE

    def test_uint16_factory(self) -> None:
        """Test uint16 factory method."""
        template = EnumTemplate.uint16(LargeEnum)

        assert template.data_size == 2
        assert template.extractor == UINT16
        assert template.decode_value(bytearray([0x00, 0x01])) == LargeEnum.LOW
        assert template.encode_value(LargeEnum.HIGH) == bytearray([0x00, 0x03])

    def test_uint32_factory(self) -> None:
        """Test uint32 factory method."""

        class LargeValueEnum(IntEnum):
            HUGE = 0x10000000

        template = EnumTemplate.uint32(LargeValueEnum)

        assert template.data_size == 4
        assert template.extractor == UINT32

    def test_sint8_factory(self) -> None:
        """Test sint8 factory method."""
        template = EnumTemplate.sint8(SignedEnum)

        assert template.data_size == 1
        assert template.extractor == SINT8
        assert template.decode_value(bytearray([0xF6])) == SignedEnum.NEGATIVE  # -10 as signed byte
        assert template.decode_value(bytearray([0x00])) == SignedEnum.ZERO
        assert template.decode_value(bytearray([0x0A])) == SignedEnum.POSITIVE

    def test_sint16_factory(self) -> None:
        """Test sint16 factory method."""

        class LargeSignedEnum(IntEnum):
            LARGE_NEGATIVE = -1000
            LARGE_POSITIVE = 1000

        template = EnumTemplate.sint16(LargeSignedEnum)

        assert template.data_size == 2
        assert template.extractor == SINT16

    def test_sint32_factory(self) -> None:
        """Test sint32 factory method."""

        class VeryLargeSignedEnum(IntEnum):
            HUGE_NEGATIVE = -100000000
            HUGE_POSITIVE = 100000000

        template = EnumTemplate.sint32(VeryLargeSignedEnum)

        assert template.data_size == 4
        assert template.extractor == SINT32


class TestEnumTemplateProperties:
    """Test EnumTemplate property exposure."""

    def test_exposes_extractor(self) -> None:
        """Test that extractor property is exposed."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.extractor is not None
        assert template.extractor == UINT8

    def test_exposes_translator(self) -> None:
        """Test that translator property is exposed (IDENTITY)."""
        template = EnumTemplate.uint8(SimpleStatus)

        assert template.translator is not None
        # For enums, translator should be IDENTITY (no scaling)
        assert template.translator.translate(42) == 42

    def test_data_size_matches_extractor(self) -> None:
        """Test that data_size matches extractor byte size."""
        template_u8 = EnumTemplate.uint8(SimpleStatus)
        assert template_u8.data_size == 1

        template_u16 = EnumTemplate.uint16(LargeEnum)
        assert template_u16.data_size == 2


class TestEnumTemplateExplicitConstructor:
    """Test explicit constructor with custom extractors."""

    def test_explicit_constructor(self) -> None:
        """Test creating template with explicit extractor."""
        template = EnumTemplate(SimpleStatus, UINT8)

        assert template.decode_value(bytearray([0x01])) == SimpleStatus.ACTIVE
        assert template.encode_value(SimpleStatus.ERROR) == bytearray([0x02])

    def test_constructor_with_different_extractors(self) -> None:
        """Test that different extractors produce different behavior."""
        # Same enum, different extractors
        template_u8 = EnumTemplate(SimpleStatus, UINT8)
        template_u16 = EnumTemplate(SimpleStatus, UINT16)

        # Different byte sizes
        assert template_u8.data_size == 1
        assert template_u16.data_size == 2

        # Different encoding
        encoded_u8 = template_u8.encode_value(SimpleStatus.ACTIVE)
        encoded_u16 = template_u16.encode_value(SimpleStatus.ACTIVE)

        assert len(encoded_u8) == 1
        assert len(encoded_u16) == 2
        assert encoded_u8 == bytearray([0x01])
        assert encoded_u16 == bytearray([0x01, 0x00])  # Little-endian


class TestEnumTemplateEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_value_enum(self) -> None:
        """Test enum with only one value."""

        class SingleValue(IntEnum):
            ONLY = 42

        template = EnumTemplate.uint8(SingleValue)

        assert template.decode_value(bytearray([42])) == SingleValue.ONLY
        assert template.encode_value(SingleValue.ONLY) == bytearray([42])

        with pytest.raises(ValueRangeError):
            template.decode_value(bytearray([0]))

    def test_max_uint8_value(self) -> None:
        """Test enum with maximum uint8 value."""

        class MaxValue(IntEnum):
            MAX = 255

        template = EnumTemplate.uint8(MaxValue)

        assert template.decode_value(bytearray([255])) == MaxValue.MAX
        assert template.encode_value(MaxValue.MAX) == bytearray([255])

    def test_zero_offset_explicit(self) -> None:
        """Test explicitly passing offset=0."""
        template = EnumTemplate.uint8(SimpleStatus)
        data = bytearray([0x01])

        result = template.decode_value(data, offset=0)
        assert result == SimpleStatus.ACTIVE

    def test_enum_with_zero_and_max(self) -> None:
        """Test enum with minimum and maximum values."""

        class MinMax(IntEnum):
            MIN = 0
            MAX = 255

        template = EnumTemplate.uint8(MinMax)

        assert template.decode_value(bytearray([0x00])) == MinMax.MIN
        assert template.decode_value(bytearray([0xFF])) == MinMax.MAX

        # Middle value should fail
        with pytest.raises(ValueRangeError):
            template.decode_value(bytearray([0x80]))


class TestUtf8StringTemplate:
    """Test the Utf8StringTemplate class."""

    def test_decode_empty_string(self) -> None:
        """Test decoding empty data."""
        template = Utf8StringTemplate()
        result = template.decode_value(bytearray())
        assert result == ""

    def test_decode_simple_string(self) -> None:
        """Test decoding a simple UTF-8 string."""
        template = Utf8StringTemplate()
        data = bytearray(b"Hello")
        result = template.decode_value(data)
        assert result == "Hello"

    def test_decode_null_terminated_string(self) -> None:
        """Test decoding null-terminated UTF-8 string."""
        template = Utf8StringTemplate()
        data = bytearray(b"Hello\x00World")
        result = template.decode_value(data)
        assert result == "Hello"

    def test_encode_string(self) -> None:
        """Test encoding a string to UTF-8 bytes."""
        template = Utf8StringTemplate()
        result = template.encode_value("Hello")
        assert result == bytearray(b"Hello")

    def test_encode_empty_string(self) -> None:
        """Test encoding an empty string."""
        template = Utf8StringTemplate()
        result = template.encode_value("")
        assert result == bytearray(b"")

    def test_encode_too_long(self) -> None:
        """Test encoding a string that's too long."""
        template = Utf8StringTemplate(max_length=5)
        with pytest.raises(ValueError, match="String too long"):
            template.encode_value("Hello World")

    def test_invalid_utf8_decode(self) -> None:
        """Test decoding invalid UTF-8 data."""
        template = Utf8StringTemplate()
        data = bytearray(b"\xff\xfe")  # Invalid UTF-8
        with pytest.raises(ValueError, match="Invalid UTF-8 string data"):
            template.decode_value(data)

    def test_data_size(self) -> None:
        """Test data_size property."""
        template = Utf8StringTemplate(max_length=100)
        assert template.data_size == 100


class TestUtf16StringTemplate:
    """Test the Utf16StringTemplate class."""

    def test_init_odd_max_length(self) -> None:
        """Test that odd max_length raises ValueError."""
        with pytest.raises(ValueError, match="max_length must be even"):
            Utf16StringTemplate(max_length=5)

    def test_decode_empty_string(self) -> None:
        """Test decoding empty data."""
        template = Utf16StringTemplate()
        result = template.decode_value(bytearray())
        assert result == ""

    def test_decode_simple_string(self) -> None:
        """Test decoding a simple UTF-16LE string."""
        template = Utf16StringTemplate()
        # "Hello" in UTF-16LE: H\x00e\x00l\x00l\x00o\x00
        data = bytearray(b"H\x00e\x00l\x00l\x00o\x00")
        result = template.decode_value(data)
        assert result == "Hello"

    def test_decode_null_terminated_string(self) -> None:
        """Test decoding null-terminated UTF-16LE string."""
        template = Utf16StringTemplate()
        # "Hi" + null terminator + extra data
        data = bytearray(b"H\x00i\x00\x00\x00W\x00o\x00r\x00l\x00d\x00")
        result = template.decode_value(data)
        assert result == "Hi"

    def test_decode_with_bom(self) -> None:
        """Test decoding UTF-16LE with BOM (should be stripped)."""
        template = Utf16StringTemplate()
        # BOM (0xFEFF) + "Hi"
        data = bytearray(b"\xff\xfeH\x00i\x00")
        result = template.decode_value(data)
        assert result == "Hi"

    def test_encode_string(self) -> None:
        """Test encoding a string to UTF-16LE bytes."""
        template = Utf16StringTemplate()
        result = template.encode_value("Hello")
        expected = bytearray(b"H\x00e\x00l\x00l\x00o\x00")
        assert result == expected

    def test_encode_empty_string(self) -> None:
        """Test encoding an empty string."""
        template = Utf16StringTemplate()
        result = template.encode_value("")
        assert result == bytearray(b"")

    def test_encode_international_chars(self) -> None:
        """Test encoding international characters."""
        template = Utf16StringTemplate()
        # Chinese characters
        result = template.encode_value("你好")
        # 2 bytes per character in UTF-16LE
        assert len(result) == 4  # 2 chars * 2 bytes

        # Decode back to verify
        decoded = template.decode_value(result)
        assert decoded == "你好"

    def test_encode_emoji(self) -> None:
        """Test encoding emoji (surrogate pairs)."""
        template = Utf16StringTemplate()
        result = template.encode_value("😀")
        # Emoji uses surrogate pair: 4 bytes
        assert len(result) == 4

        # Decode back to verify
        decoded = template.decode_value(result)
        assert decoded == "😀"

    def test_encode_too_long(self) -> None:
        """Test encoding a string that's too long."""
        template = Utf16StringTemplate(max_length=4)  # Only room for 2 chars
        with pytest.raises(ValueError, match="String too long"):
            template.encode_value("Hello")  # 5 chars = 10 bytes

    def test_decode_odd_byte_count(self) -> None:
        """Test decoding data with odd byte count."""
        template = Utf16StringTemplate()
        data = bytearray(b"H\x00e\x00l")  # 5 bytes, odd
        with pytest.raises(ValueError, match="UTF-16 data must have even byte count"):
            template.decode_value(data)

    def test_decode_invalid_utf16(self) -> None:
        """Test decoding invalid UTF-16 data."""
        template = Utf16StringTemplate()
        data = bytearray(b"\x00\xd8")  # Lone high surrogate U+D800
        with pytest.raises(ValueError, match="Invalid UTF-16LE string data"):
            template.decode_value(data)

    def test_decode_invalid_surrogate(self) -> None:
        """Test decoding data with invalid surrogate pairs."""
        template = Utf16StringTemplate()
        # Lone high surrogate
        data = bytearray(b"\x00\xd8\x00\x00")  # High surrogate U+D800 without low
        with pytest.raises(ValueError, match="Invalid UTF-16LE string data"):
            template.decode_value(data)

    def test_round_trip_encoding(self) -> None:
        """Test that encode/decode round trip works."""
        template = Utf16StringTemplate()
        test_strings = ["Hello", "你好", "مرحبا", "😀🚀"]

        for s in test_strings:
            encoded = template.encode_value(s)
            decoded = template.decode_value(encoded)
            assert decoded == s

    def test_data_size(self) -> None:
        """Test data_size property."""
        template = Utf16StringTemplate(max_length=100)
        assert template.data_size == 100
