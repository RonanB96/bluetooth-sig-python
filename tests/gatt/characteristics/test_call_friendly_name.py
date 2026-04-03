"""Tests for CallFriendlyNameCharacteristic (2BC2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.call_friendly_name import (
    CallFriendlyNameCharacteristic,
    CallFriendlyNameData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCallFriendlyName(CommonCharacteristicTests):
    """Test suite for CallFriendlyNameCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> CallFriendlyNameCharacteristic:
        return CallFriendlyNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x01John Doe"),
                expected_value=CallFriendlyNameData(call_index=1, friendly_name="John Doe"),
                description="Call index 1, name John Doe",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x00"),
                expected_value=CallFriendlyNameData(call_index=0, friendly_name=""),
                description="Call index 0, empty name",
            ),
        ]
