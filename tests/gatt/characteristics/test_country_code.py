"""Tests for CountryCode characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CountryCodeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCountryCodeCharacteristic(CommonCharacteristicTests):
    """Test suite for CountryCode characteristic."""

    @pytest.fixture
    def characteristic(self) -> CountryCodeCharacteristic:
        """Provide CountryCode characteristic."""
        return CountryCodeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CountryCode."""
        return "2AEC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for CountryCode."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x3A, 0x03]),
                expected_value=826,
                description="UK (ISO 3166-1)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="zero",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x50, 0x03]),
                expected_value=848,
                description="USA (840 LE=0x48,0x03)",
            ),
        ]
