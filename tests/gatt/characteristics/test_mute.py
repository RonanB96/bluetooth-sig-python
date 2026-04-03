"""Tests for Mute characteristic (0x2BC3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.mute import MuteCharacteristic, MuteState
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMute(CommonCharacteristicTests):
    """Test suite for Mute characteristic."""

    @pytest.fixture
    def characteristic(self) -> MuteCharacteristic:
        return MuteCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), MuteState.NOT_MUTED, "Not muted"),
            CharacteristicTestData(bytearray([0x01]), MuteState.MUTED, "Muted"),
            CharacteristicTestData(bytearray([0x02]), MuteState.DISABLED, "Disabled"),
        ]
