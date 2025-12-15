"""Tests for coding format registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.coding_format import (
    CodingFormatRegistry,
    coding_format_registry,
)
from bluetooth_sig.types.registry.coding_format import CodingFormatInfo


@pytest.fixture(scope="session")
def registry() -> CodingFormatRegistry:
    """Create a coding format registry once per test session."""
    return coding_format_registry


class TestCodingFormatRegistry:
    """Test the CodingFormatRegistry class."""

    def test_registry_initialization(self, registry: CodingFormatRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(registry, CodingFormatRegistry)
        # Registry should be lazily loaded, not loaded at init
        coding_formats = registry.get_all_coding_formats()
        assert isinstance(coding_formats, dict)
        # Should have coding formats after first access (submodule should be initialized)
        assert len(coding_formats) >= 8  # Official Bluetooth coding formats
        assert all(isinstance(info, CodingFormatInfo) for info in coding_formats.values())

    def test_lazy_loading(self) -> None:
        """Test that YAML is not loaded until first access."""
        # Create a fresh registry instance
        fresh_registry = CodingFormatRegistry()
        # _loaded should be False initially (lazy loading)
        assert not fresh_registry._loaded
        # Access should trigger loading
        _ = fresh_registry.is_known_coding_format(0x06)
        # Now _loaded should be True
        assert fresh_registry._loaded

    def test_get_coding_format_info_by_value(self, registry: CodingFormatRegistry) -> None:
        """Test lookup by coding format value."""
        # Test with known coding formats - registry should be loaded
        lc3_info = registry.get_coding_format_info(0x06)
        assert lc3_info is not None
        assert isinstance(lc3_info, CodingFormatInfo)
        assert lc3_info.value == 0x06
        assert lc3_info.name == "LC3"

        msbc_info = registry.get_coding_format_info(0x05)
        assert msbc_info is not None
        assert isinstance(msbc_info, CodingFormatInfo)
        assert msbc_info.value == 0x05
        assert msbc_info.name == "mSBC"

        transparent_info = registry.get_coding_format_info(0x03)
        assert transparent_info is not None
        assert isinstance(transparent_info, CodingFormatInfo)
        assert transparent_info.value == 0x03
        assert transparent_info.name == "Transparent"

    def test_get_coding_format_by_name(self, registry: CodingFormatRegistry) -> None:
        """Test lookup by coding format name."""
        # Test with known coding format names - registry should be loaded
        lc3_info = registry.get_coding_format_by_name("LC3")
        assert lc3_info is not None
        assert isinstance(lc3_info, CodingFormatInfo)
        assert lc3_info.value == 0x06

        msbc_info = registry.get_coding_format_by_name("mSBC")
        assert msbc_info is not None
        assert isinstance(msbc_info, CodingFormatInfo)
        assert msbc_info.value == 0x05

        # Test case insensitive
        lc3_lower = registry.get_coding_format_by_name("lc3")
        assert lc3_lower == lc3_info

        # Test not found
        info_none = registry.get_coding_format_by_name("nonexistent")
        assert info_none is None

    def test_is_known_coding_format(self, registry: CodingFormatRegistry) -> None:
        """Test checking if coding format is known."""
        # When YAML is loaded, known coding formats should return True
        assert registry.is_known_coding_format(0x06)  # LC3
        assert registry.is_known_coding_format(0x05)  # mSBC
        assert registry.is_known_coding_format(0x04)  # Linear PCM
        assert registry.is_known_coding_format(0xFF)  # Vendor Specific

        # Unknown coding format value
        assert not registry.is_known_coding_format(0xFE)  # Not assigned

    def test_get_coding_format_not_found(self, registry: CodingFormatRegistry) -> None:
        """Test lookup for non-existent coding format."""
        # Non-existent coding format value (0xFE is not assigned)
        info = registry.get_coding_format_info(0xFE)
        assert info is None

        # Non-existent name
        info = registry.get_coding_format_by_name("Nonexistent Format")
        assert info is None

    def test_get_all_coding_formats(self, registry: CodingFormatRegistry) -> None:
        """Test getting all coding formats."""
        coding_formats = registry.get_all_coding_formats()
        assert isinstance(coding_formats, dict)
        # Should have all official coding formats
        assert len(coding_formats) >= 8
        # Verify LC3 is present
        assert 0x06 in coding_formats
        assert coding_formats[0x06].name == "LC3"

    def test_thread_safety(self, registry: CodingFormatRegistry) -> None:
        """Test concurrent access to the registry."""

        def lookup_coding_format(value: int) -> CodingFormatInfo | None:
            return registry.get_coding_format_info(value)

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Perform concurrent lookups
            futures = [executor.submit(lookup_coding_format, i) for i in range(10)]
            results = [f.result() for f in futures]

        # Known values should return valid info
        assert results[6] is not None  # LC3
        assert results[6].name == "LC3"


class TestCodingFormatInfoStruct:
    """Test the CodingFormatInfo struct."""

    def test_struct_immutability(self) -> None:
        """Test that CodingFormatInfo is immutable (frozen)."""
        info = CodingFormatInfo(value=0x06, name="LC3")
        with pytest.raises(AttributeError):
            info.value = 0x07  # type: ignore[misc]

    def test_struct_equality(self) -> None:
        """Test struct equality comparison."""
        info1 = CodingFormatInfo(value=0x06, name="LC3")
        info2 = CodingFormatInfo(value=0x06, name="LC3")
        info3 = CodingFormatInfo(value=0x05, name="mSBC")

        assert info1 == info2
        assert info1 != info3
