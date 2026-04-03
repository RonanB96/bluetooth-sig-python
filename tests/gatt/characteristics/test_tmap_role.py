"""Tests for TMAPRoleCharacteristic (2B51)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.tmap_role import TMAPRole, TMAPRoleCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTMAPRole(CommonCharacteristicTests):
    """Test suite for TMAPRoleCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TMAPRoleCharacteristic:
        return TMAPRoleCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B51"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), TMAPRole(0), "No roles"),
            CharacteristicTestData(bytearray([0x01, 0x00]), TMAPRole.CALL_GATEWAY, "Call gateway"),
            CharacteristicTestData(
                bytearray([0x3F, 0x00]),
                TMAPRole.CALL_GATEWAY
                | TMAPRole.CALL_TERMINAL
                | TMAPRole.UNICAST_MEDIA_SENDER
                | TMAPRole.UNICAST_MEDIA_RECEIVER
                | TMAPRole.BROADCAST_MEDIA_SENDER
                | TMAPRole.BROADCAST_MEDIA_RECEIVER,
                "All roles",
            ),
        ]
