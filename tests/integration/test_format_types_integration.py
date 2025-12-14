"""Integration tests for format types registry and related components."""

from __future__ import annotations

from bluetooth_sig.registry.core.formattypes import format_types_registry
from bluetooth_sig.types.gatt_enums import DataType
from bluetooth_sig.types.registry.formattypes import FormatTypeInfo


class TestFormatTypesIntegration:
    """Integration tests for format types registry."""

    def test_registry_loads_format_types(self) -> None:
        """Test that registry successfully loads format types from YAML."""
        format_types = format_types_registry.get_all_format_types()

        # Should have at least the standard format types
        assert len(format_types) >= 28

        # Check some key format types
        assert 0x01 in format_types  # boolean
        assert 0x19 in format_types  # utf8s
        assert 0x1A in format_types  # utf16s
        assert 0x1B in format_types  # struct

    def test_format_type_info_matches_hardcoded_enum(self) -> None:
        """Test that registry format types match the hardcoded FormatType enum values."""
        # Test some known format types - registry should be loaded
        boolean_info = format_types_registry.get_format_type_info(0x01)
        assert boolean_info is not None
        assert boolean_info.value == 0x01
        assert boolean_info.short_name == "boolean"

        utf8s_info = format_types_registry.get_format_type_info(0x19)
        assert utf8s_info is not None
        assert utf8s_info.value == 0x19
        assert utf8s_info.short_name == "utf8s"

        utf16s_info = format_types_registry.get_format_type_info(0x1A)
        assert utf16s_info is not None
        assert utf16s_info.value == 0x1A
        assert utf16s_info.short_name == "utf16s"

    def test_datatype_enum_integration(self) -> None:
        """Test that DataType enum integrates properly with format types."""
        # UTF16S should exist and work
        assert DataType.UTF16S.value == "utf16s"
        assert DataType.from_string("utf16s") == DataType.UTF16S
        assert DataType.UTF16S.to_value_type().value == "string"
        assert DataType.UTF16S.to_python_type() == "string"

        # Should be different from UTF8S
        assert DataType.UTF16S != DataType.UTF8S  # type: ignore[comparison-overlap]

    def test_registry_singleton(self) -> None:
        """Test that format_types_registry is a proper singleton."""
        from bluetooth_sig.registry.core import format_types_registry as imported_registry
        from bluetooth_sig.registry.core import format_types_registry as main_imported_registry

        # All imports should reference the same instance
        assert format_types_registry is imported_registry
        assert format_types_registry is main_imported_registry

    def test_format_type_info_structure(self) -> None:
        """Test that FormatTypeInfo has all required fields."""
        info = format_types_registry.get_format_type_info(0x01)
        assert info is not None
        # Should be a proper dataclass/struct
        assert isinstance(info, FormatTypeInfo)
        assert hasattr(info, "value")
        assert hasattr(info, "short_name")
        assert hasattr(info, "description")
        assert hasattr(info, "exponent")
        assert hasattr(info, "size")

        # Value should match key
        assert info.value == 0x01

    def test_utf16_format_type_present(self) -> None:
        """Test that UTF-16 format type is properly registered."""
        utf16s_info = format_types_registry.get_format_type_info(0x1A)
        assert utf16s_info is not None
        assert utf16s_info.short_name == "utf16s"
        assert "utf-16" in utf16s_info.description.lower()
        assert utf16s_info.value == 0x1A

        # Also check by name
        utf16s_by_name = format_types_registry.get_format_type_by_name("utf16s")
        assert utf16s_by_name == utf16s_info

    def test_all_format_types_have_valid_data(self) -> None:
        """Test that all loaded format types have valid data."""
        format_types = format_types_registry.get_all_format_types()

        for value, info in format_types.items():
            # Basic validation
            assert isinstance(info, FormatTypeInfo)
            assert info.value == value
            assert isinstance(info.short_name, str)
            assert len(info.short_name) > 0
            assert isinstance(info.description, str)
            assert isinstance(info.exponent, bool)
            assert info.size is None or isinstance(info.size, int)
            if info.size is not None:
                assert info.size >= 0
