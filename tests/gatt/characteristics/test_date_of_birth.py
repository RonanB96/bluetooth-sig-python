"""Tests for Date of Birth characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DateOfBirthCharacteristic
from bluetooth_sig.gatt.characteristics.date_of_birth import DateOfBirthData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDateOfBirthCharacteristic(CommonCharacteristicTests):
    """Test suite for Date of Birth characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds date of birth-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> DateOfBirthCharacteristic:
        """Return a Date of Birth characteristic instance."""
        return DateOfBirthCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Date of Birth characteristic."""
        return "2A85"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for date of birth."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=DateOfBirthData(year=0, month=0, day=0),
                description="Epoch date",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07, 0x01, 0x01]),
                expected_value=DateOfBirthData(year=2000, month=1, day=1),
                description="January 1, 2000",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE4, 0x07, 0x0C, 0x1F]),
                expected_value=DateOfBirthData(year=2020, month=12, day=31),
                description="December 31, 2020",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0x0C, 0x1F]),
                expected_value=DateOfBirthData(year=65535, month=12, day=31),
                description="Maximum year value",
            ),
        ]

    # === Date of Birth-Specific Tests ===

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (2000, 1, 1),  # January 1, 2000
            (1990, 6, 15),  # June 15, 1990
            (2023, 12, 31),  # December 31, 2023
            (1970, 1, 1),  # Unix epoch date
        ],
    )
    def test_date_of_birth_values(
        self, characteristic: DateOfBirthCharacteristic, year: int, month: int, day: int
    ) -> None:
        """Test date of birth with various valid values."""
        data = bytearray(
            [
                year & 0xFF,
                (year >> 8) & 0xFF,  # Year as uint16 little-endian
                month,  # Month as uint8
                day,  # Day as uint8
            ]
        )
        result = characteristic.decode_value(data)
        assert result == DateOfBirthData(year=year, month=month, day=day)

    def test_date_of_birth_boundary_values(self, characteristic: DateOfBirthCharacteristic) -> None:
        """Test date of birth boundary values."""
        # Test epoch (0, 0, 0)
        result = characteristic.decode_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result == DateOfBirthData(year=0, month=0, day=0)

        # Test maximum year value
        result = characteristic.decode_value(bytearray([0xFF, 0xFF, 0x0C, 0x1F]))
        assert result == DateOfBirthData(year=65535, month=12, day=31)
