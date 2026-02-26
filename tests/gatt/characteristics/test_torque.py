"""Tests for Torque characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TorqueCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTorqueCharacteristic(CommonCharacteristicTests):
    """Test suite for Torque characteristic."""

    @pytest.fixture
    def characteristic(self) -> TorqueCharacteristic:
        """Provide Torque characteristic."""
        return TorqueCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Torque."""
        return "2C0B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Torque."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]),
                expected_value=10.0,
                description="1000 * 0.01 = 10.0 Nm",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=0.01,
                description="1 * 0.01 = 0.01 Nm",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="zero torque",
            ),
        ]
