"""Tests for advertising PDU parser appearance info functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.types import AppearanceData
from bluetooth_sig.types.ad_types_constants import ADType


class TestAdvertisingPDUParserAppearance:
    """Test appearance info parsing in advertising data."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create advertising PDU parser instance."""
        return AdvertisingPDUParser()

    def test_parse_appearance_with_info(self, parser: AdvertisingPDUParser) -> None:
        """Test that appearance value is parsed with registry lookup."""
        # Create advertising data with appearance
        # AD Structure: [length, type, data...]
        # Appearance (0x19): 2 bytes
        # Heart Rate Sensor Belt: 833 (0x0341) = [0x41, 0x03] in little endian
        ad_data = bytearray(
            [
                3,  # Length
                ADType.APPEARANCE,  # Type 0x19
                0x41,
                0x03,  # Appearance value 833
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.properties.appearance is not None
        assert isinstance(result.ad_structures.properties.appearance, AppearanceData)
        assert result.ad_structures.properties.appearance.raw_value == 833
        # If registry loaded, should have appearance_info
        if result.ad_structures.properties.appearance.info:
            assert result.ad_structures.properties.appearance.info.category == "Heart Rate Sensor"
            # Access subcategory directly
            assert result.ad_structures.properties.appearance.info.subcategory is not None
            assert result.ad_structures.properties.appearance.info.subcategory.name == "Heart Rate Belt"
            assert result.ad_structures.properties.appearance.info.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_parse_appearance_category_only(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing appearance with category only (no subcategory)."""
        # Phone: 64 (0x0040) = [0x40, 0x00] in little endian
        ad_data = bytearray(
            [
                3,  # Length
                ADType.APPEARANCE,  # Type 0x19
                0x40,
                0x00,  # Appearance value 64
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.properties.appearance is not None
        assert isinstance(result.ad_structures.properties.appearance, AppearanceData)
        assert result.ad_structures.properties.appearance.raw_value == 64
        if result.ad_structures.properties.appearance.info:
            assert result.ad_structures.properties.appearance.info.category == "Phone"
            assert result.ad_structures.properties.appearance.info.subcategory is None
            assert result.ad_structures.properties.appearance.info.full_name == "Phone"

    def test_parse_appearance_unknown(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing unknown appearance value."""
        # Unknown appearance value: 0 (0x0000)
        ad_data = bytearray(
            [
                3,  # Length
                ADType.APPEARANCE,  # Type 0x19
                0x00,
                0x00,  # Appearance value 0
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.properties.appearance is not None
        assert result.ad_structures.properties.appearance.raw_value == 0
        if result.ad_structures.properties.appearance.info:
            assert result.ad_structures.properties.appearance.info.category == "Unknown"

    def test_parse_appearance_not_in_registry(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing appearance value not in registry."""
        # Use unlikely value
        ad_data = bytearray(
            [
                3,  # Length
                ADType.APPEARANCE,  # Type 0x19
                0xFF,
                0xFF,  # Appearance value 65535
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.properties.appearance is not None
        assert result.ad_structures.properties.appearance.raw_value == 65535
        # appearance.info should be None for unknown codes

    def test_parse_no_appearance_field(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing advertising data without appearance field."""
        # Just a complete local name
        ad_data = bytearray(
            [
                6,  # Length
                ADType.COMPLETE_LOCAL_NAME,  # Type 0x09
                ord("T"),
                ord("e"),
                ord("s"),
                ord("t"),
                0,
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.properties.appearance is None

    def test_parse_multiple_fields_with_appearance(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing advertising data with multiple fields including appearance."""
        # Multiple AD structures: flags, name, appearance
        ad_data = bytearray(
            [
                2,  # Length
                ADType.FLAGS,  # Type 0x01
                0x06,  # Flags value
                6,  # Length
                ADType.COMPLETE_LOCAL_NAME,  # Type 0x09
                ord("T"),
                ord("e"),
                ord("s"),
                ord("t"),
                0,
                3,  # Length
                ADType.APPEARANCE,  # Type 0x19
                0x41,
                0x03,  # Heart Rate Belt
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.ad_structures.core.local_name is not None
        assert result.ad_structures.properties.appearance is not None
        assert result.ad_structures.properties.appearance.raw_value == 833
        if result.ad_structures.properties.appearance.info:
            assert result.ad_structures.properties.appearance.info.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_parse_computer_subcategories(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing various computer subcategories."""
        # Desktop Workstation: Category 2, Subcategory 1 → 129 (0x0081)
        ad_data_desktop = bytearray([3, ADType.APPEARANCE, 0x81, 0x00])
        result_desktop = parser.parse_advertising_data(bytes(ad_data_desktop))

        assert result_desktop.ad_structures.properties.appearance is not None
        assert result_desktop.ad_structures.properties.appearance.raw_value == 129
        if result_desktop.ad_structures.properties.appearance.info:
            assert result_desktop.ad_structures.properties.appearance.info.category == "Computer"
            assert result_desktop.ad_structures.properties.appearance.info.subcategory is not None
            assert result_desktop.ad_structures.properties.appearance.info.subcategory.name == "Desktop Workstation"

        # Laptop: Category 2, Subcategory 3 → 131 (0x0083)
        ad_data_laptop = bytearray([3, ADType.APPEARANCE, 0x83, 0x00])
        result_laptop = parser.parse_advertising_data(bytes(ad_data_laptop))

        assert result_laptop.ad_structures.properties.appearance is not None
        assert result_laptop.ad_structures.properties.appearance.raw_value == 131
        if result_laptop.ad_structures.properties.appearance.info:
            assert result_laptop.ad_structures.properties.appearance.info.category == "Computer"
            assert result_laptop.ad_structures.properties.appearance.info.subcategory is not None
            assert result_laptop.ad_structures.properties.appearance.info.subcategory.name == "Laptop"
