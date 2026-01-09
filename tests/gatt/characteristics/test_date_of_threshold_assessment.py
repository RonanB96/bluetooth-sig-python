"""Tests for Date of Threshold Assessment characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DateOfThresholdAssessmentCharacteristic
from bluetooth_sig.gatt.characteristics.date_of_threshold_assessment import DateOfThresholdAssessmentData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDateOfThresholdAssessmentCharacteristic(CommonCharacteristicTests):
    """Test suite for Date of Threshold Assessment characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds date of threshold assessment-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> DateOfThresholdAssessmentCharacteristic:
        """Return a Date of Threshold Assessment characteristic instance."""
        return DateOfThresholdAssessmentCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Date of Threshold Assessment characteristic."""
        return "2A86"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for date of threshold assessment."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=DateOfThresholdAssessmentData(year=0, month=0, day=0),
                description="Epoch date",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07, 0x01, 0x01]),
                expected_value=DateOfThresholdAssessmentData(year=2000, month=1, day=1),
                description="January 1, 2000",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE4, 0x07, 0x0C, 0x1F]),
                expected_value=DateOfThresholdAssessmentData(year=2020, month=12, day=31),
                description="December 31, 2020",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0F, 0x27, 0x0C, 0x1F]),
                expected_value=DateOfThresholdAssessmentData(year=9999, month=12, day=31),
                description="Maximum year value",
            ),
        ]

    # === Date of Threshold Assessment-Specific Tests ===

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (2000, 1, 1),  # January 1, 2000
            (1990, 6, 15),  # June 15, 1990
            (2023, 12, 31),  # December 31, 2023
            (1970, 1, 1),  # Unix epoch date
        ],
    )
    def test_date_of_threshold_assessment_values(
        self, characteristic: DateOfThresholdAssessmentCharacteristic, year: int, month: int, day: int
    ) -> None:
        """Test date of threshold assessment with various valid values."""
        data = bytearray(
            [
                year & 0xFF,
                (year >> 8) & 0xFF,  # Year as uint16 little-endian
                month,  # Month as uint8
                day,  # Day as uint8
            ]
        )
        result = characteristic.parse_value(data)
        assert result == DateOfThresholdAssessmentData(year=year, month=month, day=day)

    def test_date_of_threshold_assessment_boundary_values(
        self, characteristic: DateOfThresholdAssessmentCharacteristic
    ) -> None:
        """Test date of threshold assessment boundary values."""
        # Test epoch (0, 0, 0)
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result == DateOfThresholdAssessmentData(year=0, month=0, day=0)

        # Test maximum year value
        result = characteristic.parse_value(bytearray([0xFF, 0xFF, 0x0C, 0x1F]))
        assert result == DateOfThresholdAssessmentData(year=65535, month=12, day=31)
