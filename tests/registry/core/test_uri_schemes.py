"""Tests for URI schemes registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.uri_schemes import (
    UriSchemesRegistry,
    uri_schemes_registry,
)
from bluetooth_sig.types.registry.uri_schemes import UriSchemeInfo


@pytest.fixture(scope="session")
def registry() -> UriSchemesRegistry:
    """Create a URI schemes registry once per test session."""
    return uri_schemes_registry


class TestUriSchemesRegistry:
    """Test the UriSchemesRegistry class."""

    def test_registry_initialization(self, registry: UriSchemesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(registry, UriSchemesRegistry)
        # Registry should be lazily loaded, not loaded at init
        uri_schemes = registry.get_all_uri_schemes()
        assert isinstance(uri_schemes, dict)
        # Should have URI schemes after first access (submodule should be initialized)
        assert len(uri_schemes) >= 100  # Many URI schemes defined
        assert all(isinstance(info, UriSchemeInfo) for info in uri_schemes.values())

    def test_lazy_loading(self) -> None:
        """Test that YAML is not loaded until first access."""
        # Create a fresh registry instance
        fresh_registry = UriSchemesRegistry()
        # _loaded should be False initially (lazy loading)
        assert not fresh_registry._loaded
        # Access should trigger loading
        _ = fresh_registry.is_known_uri_scheme(0x16)
        # Now _loaded should be True
        assert fresh_registry._loaded

    def test_get_uri_scheme_info_by_value(self, registry: UriSchemesRegistry) -> None:
        """Test lookup by URI scheme value."""
        # Test with known URI schemes - registry should be loaded
        http_info = registry.get_uri_scheme_info(0x16)
        assert http_info is not None
        assert isinstance(http_info, UriSchemeInfo)
        assert http_info.value == 0x16
        assert http_info.name == "http:"

        https_info = registry.get_uri_scheme_info(0x17)
        assert https_info is not None
        assert isinstance(https_info, UriSchemeInfo)
        assert https_info.value == 0x17
        assert https_info.name == "https:"

        ftp_info = registry.get_uri_scheme_info(0x11)
        assert ftp_info is not None
        assert isinstance(ftp_info, UriSchemeInfo)
        assert ftp_info.value == 0x11
        assert ftp_info.name == "ftp:"

    def test_get_uri_scheme_by_name(self, registry: UriSchemesRegistry) -> None:
        """Test lookup by URI scheme name."""
        # Test with known URI scheme names - registry should be loaded
        http_info = registry.get_uri_scheme_by_name("http:")
        assert http_info is not None
        assert isinstance(http_info, UriSchemeInfo)
        assert http_info.value == 0x16

        https_info = registry.get_uri_scheme_by_name("https:")
        assert https_info is not None
        assert isinstance(https_info, UriSchemeInfo)
        assert https_info.value == 0x17

        # Test case insensitive
        http_upper = registry.get_uri_scheme_by_name("HTTP:")
        assert http_upper == http_info

        # Test not found
        info_none = registry.get_uri_scheme_by_name("nonexistent:")
        assert info_none is None

    def test_is_known_uri_scheme(self, registry: UriSchemesRegistry) -> None:
        """Test checking if URI scheme is known."""
        # When YAML is loaded, known URI schemes should return True
        assert registry.is_known_uri_scheme(0x16)  # http:
        assert registry.is_known_uri_scheme(0x17)  # https:
        assert registry.is_known_uri_scheme(0x11)  # ftp:

        # Unknown URI scheme value
        assert not registry.is_known_uri_scheme(0xFFFF)  # Not a valid scheme

    def test_get_uri_scheme_not_found(self, registry: UriSchemesRegistry) -> None:
        """Test lookup for non-existent URI scheme."""
        # Non-existent URI scheme value
        info = registry.get_uri_scheme_info(0xFFFF)
        assert info is None

        # Non-existent name
        info = registry.get_uri_scheme_by_name("nonexistent:")
        assert info is None

    def test_get_all_uri_schemes(self, registry: UriSchemesRegistry) -> None:
        """Test getting all URI schemes."""
        uri_schemes = registry.get_all_uri_schemes()
        assert isinstance(uri_schemes, dict)
        # Should have many URI schemes
        assert len(uri_schemes) >= 100
        # Verify http: is present
        assert 0x16 in uri_schemes
        assert uri_schemes[0x16].name == "http:"

    def test_decode_uri_prefix(self, registry: UriSchemesRegistry) -> None:
        """Test the convenience decode_uri_prefix method."""
        # Known schemes should return the scheme string
        assert registry.decode_uri_prefix(0x16) == "http:"
        assert registry.decode_uri_prefix(0x17) == "https:"
        assert registry.decode_uri_prefix(0x11) == "ftp:"

        # Unknown scheme should return empty string
        assert registry.decode_uri_prefix(0xFFFF) == ""

    def test_thread_safety(self, registry: UriSchemesRegistry) -> None:
        """Test concurrent access to the registry."""

        def lookup_uri_scheme(value: int) -> UriSchemeInfo | None:
            return registry.get_uri_scheme_info(value)

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Perform concurrent lookups
            futures = [executor.submit(lookup_uri_scheme, i) for i in range(30)]
            results = [f.result() for f in futures]

        # Known values should return valid info
        assert results[0x16] is not None  # http:
        assert results[0x16].name == "http:"


class TestUriSchemeInfoStruct:
    """Test the UriSchemeInfo struct."""

    def test_struct_immutability(self) -> None:
        """Test that UriSchemeInfo is immutable (frozen)."""
        info = UriSchemeInfo(value=0x16, name="http:")
        with pytest.raises(AttributeError):
            info.value = 0x17  # type: ignore[misc]

    def test_struct_equality(self) -> None:
        """Test struct equality comparison."""
        info1 = UriSchemeInfo(value=0x16, name="http:")
        info2 = UriSchemeInfo(value=0x16, name="http:")
        info3 = UriSchemeInfo(value=0x17, name="https:")

        assert info1 == info2
        assert info1 != info3

    def test_bit_property_alias(self) -> None:
        """Test the bit property alias for value."""
        info = UriSchemeInfo(value=0x16, name="http:")
        assert info.bit == info.value == 0x16
