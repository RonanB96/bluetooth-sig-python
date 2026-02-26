"""Tests for Illuminance16 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Illuminance16Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIlluminance16Characteristic(CommonCharacteristicTests):
    """Test suite for Illuminance16 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Illuminance16Characteristic:
        """Provide Illuminance16 characteristic."""
        return Illuminance16Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Illuminance16."""
        return "2C1C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Illuminance16."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="zero illuminance",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="1000 lux",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=100,
                description="100 lux",
            ),
        ]
