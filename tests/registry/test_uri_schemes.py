"""Tests for URI data types and registry integration."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.core.uri_schemes import uri_schemes_registry
from bluetooth_sig.types.uri import URIData


class TestUriSchemesRegistry:
    """Test URI schemes registry functionality."""

    def test_registry_loads(self) -> None:
        """Test that URI schemes registry loads successfully."""
        schemes = uri_schemes_registry.get_all_uri_schemes()
        assert len(schemes) > 0, "No URI schemes loaded"
        # Should have common schemes like http, https
        assert len(schemes) >= 50, f"Expected at least 50 schemes, got {len(schemes)}"

    def test_get_http_scheme(self) -> None:
        """Test getting http scheme info."""
        info = uri_schemes_registry.get_uri_scheme_info(0x16)
        assert info is not None
        assert info.name == "http:"
        assert info.value == 0x16

    def test_get_https_scheme(self) -> None:
        """Test getting https scheme info."""
        info = uri_schemes_registry.get_uri_scheme_info(0x17)
        assert info is not None
        assert info.name == "https:"
        assert info.value == 0x17

    def test_get_scheme_by_name(self) -> None:
        """Test getting scheme info by name."""
        info = uri_schemes_registry.get_uri_scheme_by_name("http:")
        assert info is not None
        assert info.value == 0x16

    def test_get_scheme_by_name_case_insensitive(self) -> None:
        """Test case insensitive name lookup."""
        info = uri_schemes_registry.get_uri_scheme_by_name("HTTP:")
        assert info is not None
        assert info.value == 0x16

    def test_unknown_scheme(self) -> None:
        """Test unknown scheme returns None."""
        info = uri_schemes_registry.get_uri_scheme_info(0xFFFF)
        assert info is None

    def test_is_known_scheme(self) -> None:
        """Test is_known_uri_scheme method."""
        assert uri_schemes_registry.is_known_uri_scheme(0x16) is True
        assert uri_schemes_registry.is_known_uri_scheme(0xFFFF) is False

    def test_decode_uri_prefix(self) -> None:
        """Test decode_uri_prefix convenience method."""
        assert uri_schemes_registry.decode_uri_prefix(0x16) == "http:"
        assert uri_schemes_registry.decode_uri_prefix(0x17) == "https:"
        assert uri_schemes_registry.decode_uri_prefix(0xFFFF) == ""


class TestURIData:
    """Test URIData parsing and construction."""

    def test_parse_http_uri(self) -> None:
        """Test parsing HTTP URI with scheme encoding."""
        # 0x16 = "http:", followed by "//example.com"
        raw_data = b"\x16//example.com"
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.scheme_code == 0x16
        assert uri_data.is_known_scheme is True
        assert uri_data.scheme_name == "http:"
        assert uri_data.full_uri == "http://example.com"
        assert uri_data.raw_data == raw_data

    def test_parse_https_uri(self) -> None:
        """Test parsing HTTPS URI with scheme encoding."""
        # 0x17 = "https:", followed by "//secure.example.com/path"
        raw_data = b"\x17//secure.example.com/path"
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.scheme_code == 0x17
        assert uri_data.is_known_scheme is True
        assert uri_data.scheme_name == "https:"
        assert uri_data.full_uri == "https://secure.example.com/path"

    def test_parse_unknown_scheme(self) -> None:
        """Test parsing URI with unknown scheme code."""
        raw_data = b"\xff//unknown.example.com"
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.scheme_code == 0xFF
        assert uri_data.is_known_scheme is False
        assert uri_data.scheme_name == ""
        assert uri_data.full_uri == "//unknown.example.com"

    def test_parse_empty_data(self) -> None:
        """Test parsing empty data."""
        uri_data = URIData.from_raw_data(b"")

        assert uri_data.scheme_code == 0
        assert uri_data.is_known_scheme is False
        assert uri_data.full_uri == ""

    def test_parse_scheme_only(self) -> None:
        """Test parsing data with only scheme code, no suffix."""
        raw_data = b"\x16"  # Just http: scheme code
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.scheme_code == 0x16
        assert uri_data.is_known_scheme is True
        assert uri_data.scheme_name == "http:"
        assert uri_data.full_uri == "http:"

    def test_parse_invalid_utf8_suffix(self) -> None:
        """Test parsing with invalid UTF-8 in suffix falls back to hex."""
        raw_data = b"\x16\xff\xfe\xfd"  # http: scheme + invalid UTF-8
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.scheme_code == 0x16
        assert uri_data.is_known_scheme is True
        # Should fall back to hex representation for invalid UTF-8
        assert "fffefd" in uri_data.full_uri.lower()

    def test_from_plain_uri(self) -> None:
        """Test creating URIData from plain URI string."""
        uri_data = URIData.from_plain_uri("https://example.com")

        assert uri_data.scheme_code == 0
        assert uri_data.is_known_scheme is False
        assert uri_data.full_uri == "https://example.com"

    def test_ftp_scheme(self) -> None:
        """Test FTP scheme parsing."""
        info = uri_schemes_registry.get_uri_scheme_info(0x11)
        assert info is not None
        assert info.name == "ftp:"

        raw_data = b"\x11//ftp.example.com/file.txt"
        uri_data = URIData.from_raw_data(raw_data)

        assert uri_data.full_uri == "ftp://ftp.example.com/file.txt"

    def test_tel_scheme(self) -> None:
        """Test tel: scheme for phone numbers."""
        # Find tel: scheme value
        info = uri_schemes_registry.get_uri_scheme_by_name("tel:")
        if info:
            raw_data = bytes([info.value]) + b"+1-555-123-4567"
            uri_data = URIData.from_raw_data(raw_data)

            assert uri_data.is_known_scheme is True
            assert uri_data.scheme_name == "tel:"
            assert uri_data.full_uri == "tel:+1-555-123-4567"


class TestURIDataIntegration:
    """Integration tests for URI data with advertising parser."""

    def test_uri_data_in_advertising(self) -> None:
        """Test that URIData can be created from advertising-like data."""
        # Simulate Eddystone URL beacon data format
        # 0x17 = https: scheme
        eddystone_uri_data = b"\x17//goo.gl/abc123"
        uri_data = URIData.from_raw_data(eddystone_uri_data)

        assert uri_data.full_uri == "https://goo.gl/abc123"
        assert uri_data.scheme_name == "https:"

    @pytest.mark.parametrize(
        ("scheme_code", "expected_scheme"),
        [
            (0x16, "http:"),
            (0x17, "https:"),
            (0x11, "ftp:"),
            (0x10, "file:"),
        ],
    )
    def test_common_schemes(self, scheme_code: int, expected_scheme: str) -> None:
        """Test common URI schemes are correctly resolved."""
        info = uri_schemes_registry.get_uri_scheme_info(scheme_code)
        assert info is not None
        assert info.name == expected_scheme
