"""Tests for VolumeFlow characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import VolumeFlowCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestVolumeFlowCharacteristic(CommonCharacteristicTests):
    """Test suite for VolumeFlow characteristic."""

    @pytest.fixture
    def characteristic(self) -> VolumeFlowCharacteristic:
        """Provide VolumeFlow characteristic."""
        return VolumeFlowCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for VolumeFlow."""
        return "2B1B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for VolumeFlow."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1.0,
                description="1000 * 0.001 = 1.0 L/s",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=0.001,
                description="1 * 0.001 = 0.001 L/s",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0.0,
                description="zero flow",
            ),
        ]
