"""Tests for LuminousExposure characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousExposureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLuminousExposureCharacteristic(CommonCharacteristicTests):
    """Test suite for LuminousExposure characteristic."""

    @pytest.fixture
    def characteristic(self) -> LuminousExposureCharacteristic:
        """Provide LuminousExposure characteristic."""
        return LuminousExposureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LuminousExposure."""
        return "2AFE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LuminousExposure."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x00]),
                expected_value=100,
                description="100 lux*h",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00]),
                expected_value=1000,
                description="1000 lux*h",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=1,
                description="1 lux*h",
            ),
        ]
