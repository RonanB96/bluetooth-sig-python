"""Tests for Location Name characteristic (0x2AB5)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
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
                input_data=bytearray(b"Room 101\x00extra"),  # Null-terminated with extra data
                expected_value="Room 101",
                description="Null-terminated string with trailing data",
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

    def test_location_name_round_trip(self, characteristic: LocationNameCharacteristic) -> None:
        """Test that encoding and decoding preserve string content (round trip)."""
        test_cases = [
            ("Home", bytearray(b"Home")),
            ("Café Paris", bytearray("Café Paris".encode())),
            ("", bytearray()),
        ]

        for expected_str, input_data in test_cases:
            decoded = characteristic.parse_value(input_data)
            encoded = characteristic.build_value(decoded)
            re_decoded = characteristic.parse_value(encoded)
            assert re_decoded == expected_str, f"Round trip failed for: {expected_str!r}"

    def test_round_trip(
        self,
        characteristic: BaseCharacteristic[Any],
        valid_test_data: CharacteristicTestData | list[CharacteristicTestData],
    ) -> None:
        """Override round trip test to exclude null-terminated strings with extra data."""
        # Use only the first 3 test cases that can round trip exactly
        round_trip_data = valid_test_data[:3] if isinstance(valid_test_data, list) else [valid_test_data]

        for i, test_case in enumerate(round_trip_data):
            case_desc = f"Test case {i + 1} ({test_case.description})"
            parsed = characteristic.parse_value(test_case.input_data)
            encoded = characteristic.build_value(parsed)
            assert encoded == test_case.input_data, f"{case_desc}: Round trip failed - encoded data differs from input"
