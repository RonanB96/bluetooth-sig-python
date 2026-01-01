"""Tests for characteristic templates."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.templates import Utf8StringTemplate, Utf16StringTemplate


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
