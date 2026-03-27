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
            CharacteristicTestData(bytearray([0x00]), VolumeFlags(0), "No flags"),
            CharacteristicTestData(bytearray([0x01]), VolumeFlags.RESET_VOLUME_SETTING, "Reset volume setting"),
        ]

    def test_roundtrip(self, characteristic: VolumeFlagsCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), VolumeFlags(0), "No flags"),
            CharacteristicTestData(bytearray([0x01]), VolumeFlags.RESET_VOLUME_SETTING, "Reset volume setting"),
        ]
