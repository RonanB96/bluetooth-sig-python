"""Tests for advertising parser appearance info functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.device.advertising_parser import AdvertisingParser
from bluetooth_sig.types import AppearanceData, BLEAdvertisementTypes


class TestAdvertisingParserAppearance:
    """Test appearance info parsing in advertising data."""

    @pytest.fixture
    def parser(self) -> AdvertisingParser:
        """Create advertising parser instance."""
        return AdvertisingParser()

    def test_parse_appearance_with_info(self, parser: AdvertisingParser) -> None:
        """Test that appearance value is parsed with registry lookup."""
        # Create advertising data with appearance
        # AD Structure: [length, type, data...]
        # Appearance (0x19): 2 bytes
        # Heart Rate Sensor Belt: 833 (0x0341) = [0x41, 0x03] in little endian
        ad_data = bytearray(
            [
                3,  # Length
                BLEAdvertisementTypes.APPEARANCE,  # Type 0x19
                0x41,
                0x03,  # Appearance value 833
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.appearance is not None
        assert isinstance(result.appearance, AppearanceData)
        assert result.appearance.raw_value == 833
        # If registry loaded, should have appearance_info
        if result.appearance.info:
            assert result.appearance.info.category == "Heart Rate Sensor"
            assert result.appearance.info.subcategory == "Heart Rate Belt"
            assert result.appearance.info.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_parse_appearance_category_only(self, parser: AdvertisingParser) -> None:
        """Test parsing appearance with category only (no subcategory)."""
        # Phone: 64 (0x0040) = [0x40, 0x00] in little endian
        ad_data = bytearray(
            [
                3,  # Length
                BLEAdvertisementTypes.APPEARANCE,  # Type 0x19
                0x40,
                0x00,  # Appearance value 64
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.appearance is not None
        assert isinstance(result.appearance, AppearanceData)
        assert result.appearance.raw_value == 64
        if result.appearance.info:
            assert result.appearance.info.category == "Phone"
            assert result.appearance.info.subcategory is None
            assert result.appearance.info.full_name == "Phone"

    def test_parse_appearance_unknown(self, parser: AdvertisingParser) -> None:
        """Test parsing unknown appearance value."""
        # Unknown: 0 (0x0000)
        ad_data = bytearray(
            [
                3,  # Length
                BLEAdvertisementTypes.APPEARANCE,  # Type 0x19
                0x00,
                0x00,  # Appearance value 0
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.appearance is not None
        assert result.appearance.raw_value == 0
        if result.appearance.info:
            assert result.appearance.info.category == "Unknown"

    def test_parse_appearance_not_in_registry(self, parser: AdvertisingParser) -> None:
        """Test parsing appearance value not in registry."""
        # Use unlikely value
        ad_data = bytearray(
            [
                3,  # Length
                BLEAdvertisementTypes.APPEARANCE,  # Type 0x19
                0xFF,
                0xFF,  # Appearance value 65535
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.appearance is not None
        assert result.appearance.raw_value == 65535
        # appearance.info should be None for unknown codes

    def test_parse_no_appearance_field(self, parser: AdvertisingParser) -> None:
        """Test parsing advertising data without appearance field."""
        # Just a complete local name
        ad_data = bytearray(
            [
                6,  # Length
                BLEAdvertisementTypes.COMPLETE_LOCAL_NAME,  # Type 0x09
                ord("T"),
                ord("e"),
                ord("s"),
                ord("t"),
                0,
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.appearance is None

    def test_parse_multiple_fields_with_appearance(self, parser: AdvertisingParser) -> None:
        """Test parsing advertising data with multiple fields including appearance."""
        # Multiple AD structures: flags, name, appearance
        ad_data = bytearray(
            [
                2,  # Length
                BLEAdvertisementTypes.FLAGS,  # Type 0x01
                0x06,  # Flags value
                6,  # Length
                BLEAdvertisementTypes.COMPLETE_LOCAL_NAME,  # Type 0x09
                ord("T"),
                ord("e"),
                ord("s"),
                ord("t"),
                0,
                3,  # Length
                BLEAdvertisementTypes.APPEARANCE,  # Type 0x19
                0x41,
                0x03,  # Heart Rate Belt
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        assert result.local_name is not None
        assert result.appearance is not None
        assert result.appearance.raw_value == 833
        if result.appearance.info:
            assert result.appearance.info.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_parse_computer_subcategories(self, parser: AdvertisingParser) -> None:
        """Test parsing various computer subcategories."""
        # Desktop: (2 << 6) | 1 = 129 (0x0081)
        ad_data_desktop = bytearray([3, BLEAdvertisementTypes.APPEARANCE, 0x81, 0x00])
        result_desktop = parser.parse_advertising_data(bytes(ad_data_desktop))

        assert result_desktop.appearance is not None
        assert result_desktop.appearance.raw_value == 129
        if result_desktop.appearance.info:
            assert result_desktop.appearance.info.category == "Computer"
            assert result_desktop.appearance.info.subcategory == "Desktop Workstation"

        # Laptop: (2 << 6) | 3 = 131 (0x0083)
        ad_data_laptop = bytearray([3, BLEAdvertisementTypes.APPEARANCE, 0x83, 0x00])
        result_laptop = parser.parse_advertising_data(bytes(ad_data_laptop))

        assert result_laptop.appearance is not None
        assert result_laptop.appearance.raw_value == 131
        if result_laptop.appearance.info:
            assert result_laptop.appearance.info.category == "Computer"
            assert result_laptop.appearance.info.subcategory == "Laptop"
