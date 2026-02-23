"""Tests for PerceivedLightness characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PerceivedLightnessCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPerceivedLightnessCharacteristic(CommonCharacteristicTests):
    """Test suite for PerceivedLightness characteristic."""

    @pytest.fixture
    def characteristic(self) -> PerceivedLightnessCharacteristic:
        """Provide PerceivedLightness characteristic."""
        return PerceivedLightnessCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PerceivedLightness."""
        return "2B03"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for PerceivedLightness."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="zero lightness",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="lightness 1000",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),
                expected_value=65535,
                description="max lightness",
            ),
        ]
