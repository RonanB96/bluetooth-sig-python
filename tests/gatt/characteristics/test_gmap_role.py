"""Tests for GMAPRoleCharacteristic (2C00)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.gmap_role import GMAPRole, GMAPRoleCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestGMAPRole(CommonCharacteristicTests):
    """Test suite for GMAPRoleCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> GMAPRoleCharacteristic:
        return GMAPRoleCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C00"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), GMAPRole(0), "No roles"),
            CharacteristicTestData(bytearray([0x01]), GMAPRole.UNICAST_GAME_GATEWAY, "UGG"),
            CharacteristicTestData(
                bytearray([0x0F]),
                GMAPRole.UNICAST_GAME_GATEWAY
                | GMAPRole.UNICAST_GAME_TERMINAL
                | GMAPRole.BROADCAST_GAME_SENDER
                | GMAPRole.BROADCAST_GAME_RECEIVER,
                "All roles",
            ),
        ]
