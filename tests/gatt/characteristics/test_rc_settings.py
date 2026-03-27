"""Tests for RCSettingsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.rc_settings import RCSettingsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestRCSettingsCharacteristic(CommonCharacteristicTests):
    """RCSettingsCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> RCSettingsCharacteristic:
        return RCSettingsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="Zero settings value",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x2A, 0x01]),
                expected_value=0x012A,
                description="Non-zero settings value (298 LE)",
            ),
        ]
