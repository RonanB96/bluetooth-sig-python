"""Tests for SetMemberRankCharacteristic (2B87)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.set_member_rank import SetMemberRankCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSetMemberRank(CommonCharacteristicTests):
    """Test suite for SetMemberRankCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SetMemberRankCharacteristic:
        return SetMemberRankCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B87"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), 1, "Rank 1"),
            CharacteristicTestData(bytearray([0x02]), 2, "Rank 2"),
            CharacteristicTestData(bytearray([0xFF]), 255, "Max rank"),
        ]
