"""Tests for VolumeFlagsCharacteristic (2B7F)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.volume_flags import VolumeFlags, VolumeFlagsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVolumeFlags(CommonCharacteristicTests):
    """Test suite for VolumeFlagsCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> VolumeFlagsCharacteristic:
        return VolumeFlagsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), VolumeFlags.RESET_VOLUME_SETTING, "Reset volume setting"),
            CharacteristicTestData(bytearray([0x01]), VolumeFlags.USER_SET_VOLUME_SETTING, "User set volume setting"),
        ]
