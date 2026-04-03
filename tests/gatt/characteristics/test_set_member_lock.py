"""Tests for SetMemberLockCharacteristic (2B86)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.set_member_lock import SetMemberLockCharacteristic, SetMemberLockState
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSetMemberLock(CommonCharacteristicTests):
    """Test suite for SetMemberLockCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SetMemberLockCharacteristic:
        return SetMemberLockCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B86"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), SetMemberLockState.UNLOCKED, "Unlocked"),
            CharacteristicTestData(bytearray([0x02]), SetMemberLockState.LOCKED, "Locked"),
        ]
