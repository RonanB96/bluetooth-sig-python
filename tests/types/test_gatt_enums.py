"""Tests for GATT enums functionality."""

from __future__ import annotations

from bluetooth_sig.types.gatt_enums import DataType, ValueType


class TestDataType:
    """Test the DataType enum."""

    def test_utf16s_enum_member(self) -> None:
        """Test that UTF16S enum member exists."""
        assert hasattr(DataType, "UTF16S")
        assert DataType.UTF16S.value == "utf16s"

    def test_from_string_utf16s(self) -> None:
        """Test that from_string("utf16s") returns UTF16S, not UTF8S."""
        result = DataType.from_string("utf16s")
        assert result == DataType.UTF16S
        assert result != DataType.UTF8S  # type: ignore[comparison-overlap]

    def test_utf16s_to_value_type(self) -> None:
        """Test that UTF16S.to_value_type() returns STRING."""
        assert DataType.UTF16S.to_value_type() == ValueType.STRING

    def test_utf16s_to_python_type(self) -> None:
        """Test that UTF16S.to_python_type() returns "string"."""
        assert DataType.UTF16S.to_python_type() == "string"

    def test_utf8s_still_works(self) -> None:
        """Test that UTF8S still works as before."""
        assert DataType.UTF8S.to_value_type() == ValueType.STRING
        assert DataType.UTF8S.to_python_type() == "string"

    def test_from_string_case_insensitive(self) -> None:
        """Test that from_string is case insensitive."""
        assert DataType.from_string("UTF16S") == DataType.UTF16S
        assert DataType.from_string("utf16s") == DataType.UTF16S
        assert DataType.from_string("Utf16s") == DataType.UTF16S

    def test_from_string_aliases(self) -> None:
        """Test that aliases still work."""
        assert DataType.from_string("sfloat") == DataType.MEDFLOAT16
        assert DataType.from_string("float") == DataType.FLOAT32
        assert DataType.from_string("variable") == DataType.STRUCT

    def test_from_string_unknown(self) -> None:
        """Test that unknown strings return UNKNOWN."""
        assert DataType.from_string("unknown_type") == DataType.UNKNOWN
        assert DataType.from_string("") == DataType.UNKNOWN
        assert DataType.from_string(None) == DataType.UNKNOWN

    def test_all_members_have_value_type(self) -> None:
        """Test that all DataType members have a valid to_value_type."""
        for member in DataType:
            value_type = member.to_value_type()
            assert isinstance(value_type, ValueType)
            assert value_type != ValueType.UNKNOWN or member == DataType.UNKNOWN

    def test_all_members_have_python_type(self) -> None:
        """Test that all DataType members have a valid to_python_type."""
        for member in DataType:
            python_type = member.to_python_type()
            assert isinstance(python_type, str)
            assert len(python_type) > 0
