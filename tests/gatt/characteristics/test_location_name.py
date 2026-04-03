"""Tests for Location Name characteristic (0x2AB5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.location_name import LocationNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLocationNameCharacteristic(CommonCharacteristicTests):
    """Test suite for Location Name characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Tests UTF-8 string parsing for location names.
    """

    @pytest.fixture
    def characteristic(self) -> LocationNameCharacteristic:
        """Return a Location Name characteristic instance."""
        return LocationNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Location Name characteristic."""
        return "2AB5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for location name strings."""
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Home"), expected_value="Home", description="Simple ASCII location name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Office Building A"),
                expected_value="Office Building A",
                description="Multi-word ASCII location name",
            ),
            CharacteristicTestData(
                input_data=bytearray("Café Paris".encode()),
                expected_value="Café Paris",
                description="UTF-8 location name with accented characters",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Room 101"),
                expected_value="Room 101",
                description="Simple ASCII location name without null terminator",
            ),
        ]

    def test_location_name_utf8_handling(self, characteristic: LocationNameCharacteristic) -> None:
        """Test UTF-8 encoding and decoding."""
        test_strings = [
            "Library",
            "会议室",  # Chinese characters
            "Café Müller",  # German umlaut
            "🏢 Office",  # Emoji
            "",  # Empty string
        ]

        for test_str in test_strings:
            encoded = characteristic.build_value(test_str)
            decoded = characteristic.parse_value(encoded)
            assert decoded == test_str, f"UTF-8 round trip failed for: {test_str!r}"

    def test_location_name_null_termination(self, characteristic: LocationNameCharacteristic) -> None:
        """Test that null-terminated strings are handled correctly."""
        # Test with null terminator
        null_terminated = bytearray(b"Garage\x00")
        result = characteristic.parse_value(null_terminated)
        assert result == "Garage", f"Expected 'Garage', got {result!r}"

        # Test without null terminator
        no_null = bytearray(b"Garage")
        result = characteristic.parse_value(no_null)
        assert result == "Garage", f"Expected 'Garage', got {result!r}"

    def test_location_name_empty_string(self, characteristic: LocationNameCharacteristic) -> None:
        """Test empty string handling."""
        empty_data = bytearray()
        result = characteristic.parse_value(empty_data)
        assert result == "", "Empty data should decode to empty string"

        # Test encoding empty string
        encoded = characteristic.build_value("")
        assert encoded == bytearray(), "Empty string should encode to empty bytes"
